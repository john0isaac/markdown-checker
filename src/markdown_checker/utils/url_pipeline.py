"""Run-scoped URL checking pipeline.

Provides a single ``URLCheckService`` shared across all files in a run that:

- Checks each unique normalized URL exactly once (in-memory memo), and shares
  the in-flight result with any duplicate occurrences submitted concurrently.
- Serializes requests to the same host with a politeness delay between them.
- Applies a host-level circuit breaker: a rate-limited response pauses the
  whole host until its Retry-After window elapses, instead of every URL on
  that host independently discovering and retrying the rate limit. A second
  consecutive rate limit for the same host is treated as persistent
  throttling: every other job already queued for that host is resolved as
  rate_limited without spending a network request on each, and the host is
  blocked from new dispatches until the cooldown elapses.
- Bounds memory via backpressure: ``submit()`` blocks once ``max_pending``
  jobs are in flight, so memory stays flat regardless of repo size.

``submit()`` must only be called from a single producer thread for the
lifetime of a service instance; a second calling thread raises RuntimeError.
"""

import heapq
import threading
import time
from collections import deque
from concurrent.futures import Future
from dataclasses import dataclass
from dataclasses import field
from urllib.parse import urlparse
from urllib.parse import urlunparse

import httpx2

from markdown_checker.models.config import Config
from markdown_checker.models.config import create_http_client
from markdown_checker.models.url import MarkdownURL
from markdown_checker.models.url import URLCheckResult


def normalize_url(link: str) -> str:
    """
    Normalize a URL into a dedupe key.

    Lowercases the scheme and host, strips a trailing slash from the path,
    and drops the fragment. Query strings are preserved as-is.

    Args:
        link (str): The raw URL to normalize.

    Returns:
        The normalized URL string used as the memo/dedupe key.
    """
    parts = urlparse(link)
    return urlunparse(
        (parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), parts.params, parts.query, "")
    )


@dataclass(slots=True)
class _Job:
    """A single unique-URL check pending in the pipeline."""

    key: str
    url: MarkdownURL
    future: "Future[URLCheckResult]"
    requeues: int = 0


@dataclass(slots=True)
class _HostState:
    """Per-host queue and pacing state."""

    jobs: "deque[_Job]" = field(default_factory=deque)
    next_ready_at: float = 0.0
    in_heap: bool = False
    busy: bool = False
    blocked_until: float = 0.0
    """Set after two consecutive rate-limit signals for this host. Until this
    time elapses, jobs for this host are resolved as rate_limited without
    spending a network request on each - see _run_job / submit."""


class URLCheckService:
    """Run-scoped URL checking: dedupe memo, per-host pacing, host circuit breaker."""

    def __init__(self, config: Config) -> None:
        self._config = config
        self._cond = threading.Condition()
        self._results: dict[str, Future[URLCheckResult]] = {}
        self._pending: dict[str, _Job] = {}
        self._hosts: dict[str, _HostState] = {}
        self._heap: list[tuple[float, int, str]] = []
        self._seq = 0
        self._backpressure = threading.BoundedSemaphore(config.max_pending)
        self._shutdown = False
        self._producer_thread_id: int | None = None
        self._workers = [
            threading.Thread(target=self._worker, daemon=True, name=f"url-check-{i}") for i in range(config.max_workers)
        ]
        for worker in self._workers:
            worker.start()

    # -- producer side (must be called from a single thread) -------------

    def submit(self, url: MarkdownURL) -> "Future[URLCheckResult]":
        """
        Submit a URL for checking, deduped against the run-wide memo.

        Returns a Future that resolves once the underlying unique URL has
        been checked. Duplicate submissions of the same normalized URL,
        whether already resolved or still in flight, share the same result
        without triggering additional network activity.

        Must only ever be called from a single thread for the lifetime of a
        service instance; calling it from more than one thread raises
        RuntimeError, since the memo/backpressure handshake below is not safe
        under concurrent producers.
        """
        key = normalize_url(url.link)
        with self._cond:
            self._check_single_producer_locked()
            if key in self._results:
                return self._results[key]
            if key in self._pending:
                return self._pending[key].future

        # Blocks when max_pending jobs are in flight (backpressure keeps memory bounded).
        self._backpressure.acquire()
        job = _Job(key=key, url=url, future=Future())
        hostname = url.host_name().lower()
        with self._cond:
            self._pending[key] = job
            host = self._hosts.setdefault(hostname, _HostState())
            now = time.monotonic()
            if now < host.blocked_until:
                # Host is cooling down after repeated rate limiting; resolve immediately
                # instead of queueing behind an already-blocked host.
                self._finalize_locked(
                    job,
                    URLCheckResult(
                        status="rate_limited", http_status_code=None, retry_after=int(host.blocked_until - now)
                    ),
                )
            else:
                host.jobs.append(job)
                self._schedule_host_locked(hostname, host)
                self._cond.notify()
        return job.future

    def close(self) -> None:
        """Shut down worker threads. Call only after all submitted Futures have resolved."""
        with self._cond:
            self._shutdown = True
            self._cond.notify_all()
        for worker in self._workers:
            worker.join()

    # -- scheduling / bookkeeping (all called with self._cond held) -------

    def _check_single_producer_locked(self) -> None:
        current = threading.get_ident()
        if self._producer_thread_id is None:
            self._producer_thread_id = current
        elif current != self._producer_thread_id:
            raise RuntimeError(
                "URLCheckService.submit() must only be called from a single producer thread "
                f"(first called from thread {self._producer_thread_id}, now called from thread {current})."
            )

    def _finalize_locked(self, job: _Job, result: URLCheckResult) -> None:
        """Resolve a job with its final result: cache the completed future, free its permit."""
        job.future.set_result(result)
        self._results[job.key] = job.future
        del self._pending[job.key]
        self._backpressure.release()

    def _schedule_host_locked(self, hostname: str, host: _HostState) -> None:
        if host.jobs and not host.in_heap and not host.busy:
            self._seq += 1
            heapq.heappush(self._heap, (host.next_ready_at, self._seq, hostname))
            host.in_heap = True

    def _next_ready_host_locked(self) -> str | None:
        now = time.monotonic()
        while self._heap and self._heap[0][0] <= now:
            _, _, hostname = heapq.heappop(self._heap)
            host = self._hosts[hostname]
            host.in_heap = False
            if host.jobs and not host.busy:
                return hostname
        return None

    def _wait_timeout_locked(self) -> float | None:
        if not self._heap:
            return None
        return max(0.0, self._heap[0][0] - time.monotonic())

    def _worker(self) -> None:
        client = create_http_client()
        try:
            while True:
                with self._cond:
                    hostname = self._next_ready_host_locked()
                    while hostname is None:
                        if self._shutdown:
                            return
                        self._cond.wait(timeout=self._wait_timeout_locked())
                        hostname = self._next_ready_host_locked()
                    host = self._hosts[hostname]
                    host.busy = True
                    job = host.jobs.popleft()
                self._run_job(client, hostname, host, job)
        finally:
            client.close()

    def _run_job(self, client: httpx2.Client, hostname: str, host: _HostState, job: _Job) -> None:
        try:
            result = job.url.check(
                timeout=self._config.timeout,
                retries=self._config.retries,
                client=client,
                retry_on_429=self._config.retry_on_429,
                fallback_retry_delay=self._config.fallback_retry_delay,
            )
        except Exception:  # noqa: BLE001 - a worker crashing must not hang collect() forever
            # Treat it like any other unreachable-URL outcome instead of propagating: one
            # unexpected exception shouldn't abort collection of every other file's results.
            result = URLCheckResult(status="transient_error", http_status_code=None)

        now = time.monotonic()
        with self._cond:
            host.busy = False
            if result.status == "rate_limited":
                if job.requeues < 1:
                    # First rate-limit signal for this job: wait out the window, then retry once.
                    job.requeues += 1
                    host.jobs.appendleft(job)
                    host.next_ready_at = now + (result.retry_after or self._config.fallback_retry_delay)
                else:
                    # Persistent throttling: two rate-limit signals in a row for this host.
                    # Stop probing it job-by-job - drain every other job currently queued
                    # for this host as rate_limited without spending a network request on
                    # each, and block new submissions to this host until the cooldown ends.
                    cooldown_until = now + (result.retry_after or self._config.fallback_retry_delay)
                    host.blocked_until = cooldown_until
                    host.next_ready_at = cooldown_until
                    self._finalize_locked(job, result)
                    while host.jobs:
                        self._finalize_locked(host.jobs.popleft(), result)
            else:
                self._finalize_locked(job, result)
                host.next_ready_at = now + self._config.per_host_delay
            self._schedule_host_locked(hostname, host)
            self._cond.notify_all()
