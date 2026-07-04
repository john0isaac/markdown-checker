import threading
import time
from concurrent.futures import Future
from pathlib import Path
from unittest.mock import patch

import pytest

from markdown_checker.models.config import Config
from markdown_checker.models.url import MarkdownURL
from markdown_checker.models.url import URLCheckResult
from markdown_checker.utils.url_pipeline import normalize_url
from markdown_checker.utils.url_pipeline import URLCheckService


def _url(link: str, file_path: Path = Path("test.md")) -> MarkdownURL:
    return MarkdownURL(link=link, line_number=1, file_path=file_path)


# --- normalize_url ---


@pytest.mark.parametrize(
    "link, expected",
    [
        ("HTTPS://Example.COM/Path", "https://example.com/Path"),
        ("https://example.com/path/", "https://example.com/path"),
        ("https://example.com/path#fragment", "https://example.com/path"),
        ("https://example.com/path?q=1", "https://example.com/path?q=1"),
        ("https://example.com/", "https://example.com"),
    ],
)
def test_normalize_url(link: str, expected: str):
    """Lowercases scheme/host, strips trailing slash and fragment, keeps query."""
    assert normalize_url(link) == expected


# --- memo / dedupe ---


def test_submit_memo_hit_avoids_second_check():
    """A second submit() of an already-resolved URL does not trigger another check()."""
    config = Config(max_workers=2)
    service = URLCheckService(config)
    try:
        alive = URLCheckResult(status="alive", http_status_code=200)
        with patch.object(MarkdownURL, "check", return_value=alive) as mock_check:
            future1 = service.submit(_url("https://example.com/a"))
            result1 = future1.result(timeout=5)
            future2 = service.submit(_url("https://example.com/a"))
            result2 = future2.result(timeout=5)
        assert mock_check.call_count == 1
        assert result1 is result2 is alive
    finally:
        service.close()


def test_submit_in_flight_dedupe_shares_future():
    """Two submits of the same URL while the first is still in flight share one Future."""
    config = Config(max_workers=2)
    service = URLCheckService(config)
    release = threading.Event()
    alive = URLCheckResult(status="alive", http_status_code=200)

    def fake_check(self: MarkdownURL, **kwargs: object) -> URLCheckResult:
        release.wait(timeout=5)
        return alive

    try:
        with patch.object(MarkdownURL, "check", fake_check):
            future1 = service.submit(_url("https://example.com/b"))
            # Give the worker a moment to pick up the job before submitting the duplicate.
            time.sleep(0.05)
            future2 = service.submit(_url("https://example.com/b"))
            assert future1 is future2
            release.set()
            assert future1.result(timeout=5) is alive
    finally:
        release.set()
        service.close()


# --- per-host serialization ---


def test_per_host_requests_never_overlap():
    """Two URLs on the same host are never checked concurrently."""
    config = Config(max_workers=4, per_host_delay=0.0)
    service = URLCheckService(config)
    lock = threading.Lock()
    intervals: list[tuple[float, float]] = []

    def fake_check(self: MarkdownURL, **kwargs: object) -> URLCheckResult:
        start = time.monotonic()
        time.sleep(0.05)
        end = time.monotonic()
        with lock:
            intervals.append((start, end))
        return URLCheckResult(status="alive", http_status_code=200)

    try:
        with patch.object(MarkdownURL, "check", fake_check):
            future1 = service.submit(_url("https://same-host.example.com/1"))
            future2 = service.submit(_url("https://same-host.example.com/2"))
            future1.result(timeout=5)
            future2.result(timeout=5)
    finally:
        service.close()

    assert len(intervals) == 2
    (start_a, end_a), (start_b, end_b) = sorted(intervals)
    assert end_a <= start_b, "requests to the same host overlapped"


def test_different_hosts_are_not_serialized():
    """URLs on different hosts are not blocked by each other's pacing."""
    config = Config(max_workers=4, per_host_delay=0.0)
    service = URLCheckService(config)
    barrier = threading.Barrier(2, timeout=5)

    def fake_check(self: MarkdownURL, **kwargs: object) -> URLCheckResult:
        barrier.wait()  # only succeeds if both hosts are being checked concurrently
        return URLCheckResult(status="alive", http_status_code=200)

    try:
        with patch.object(MarkdownURL, "check", fake_check):
            future1 = service.submit(_url("https://host-a.example.com/1"))
            future2 = service.submit(_url("https://host-b.example.com/1"))
            assert future1.result(timeout=5).status == "alive"
            assert future2.result(timeout=5).status == "alive"
    finally:
        service.close()


def test_per_host_delay_paces_consecutive_requests():
    """Consecutive requests to the same host are spaced by at least per_host_delay."""
    config = Config(max_workers=1, per_host_delay=0.2)
    service = URLCheckService(config)
    timestamps: list[float] = []

    def fake_check(self: MarkdownURL, **kwargs: object) -> URLCheckResult:
        timestamps.append(time.monotonic())
        return URLCheckResult(status="alive", http_status_code=200)

    try:
        with patch.object(MarkdownURL, "check", fake_check):
            future1 = service.submit(_url("https://paced.example.com/1"))
            future2 = service.submit(_url("https://paced.example.com/2"))
            future1.result(timeout=5)
            future2.result(timeout=5)
    finally:
        service.close()

    assert len(timestamps) == 2
    assert timestamps[1] - timestamps[0] >= 0.2 - 0.01


# --- host-level circuit breaker ---


def test_rate_limit_pauses_host_and_requeues_once():
    """A rate_limited result pauses the host until retry_after elapses, then retries once."""
    config = Config(max_workers=1, per_host_delay=0.0)
    service = URLCheckService(config)
    call_times: list[float] = []
    rate_limited = URLCheckResult(status="rate_limited", http_status_code=429, retry_after=1)
    alive = URLCheckResult(status="alive", http_status_code=200)

    def fake_check(self: MarkdownURL, **kwargs: object) -> URLCheckResult:
        call_times.append(time.monotonic())
        return rate_limited if len(call_times) == 1 else alive

    try:
        with patch.object(MarkdownURL, "check", fake_check):
            start = time.monotonic()
            future = service.submit(_url("https://throttled.example.com/1"))
            result = future.result(timeout=5)
    finally:
        service.close()

    assert result.status == "alive"
    assert len(call_times) == 2
    assert call_times[1] - start >= 1 - 0.05, "retry happened before the retry_after window elapsed"


def test_persistent_rate_limit_drains_queued_jobs_without_network():
    """Two consecutive rate-limited results for a host drain every other queued job for
    that host as rate_limited too, without spending a network request on each."""
    config = Config(max_workers=1, per_host_delay=0.0)
    service = URLCheckService(config)
    calls: list[float] = []
    rate_limited = URLCheckResult(status="rate_limited", http_status_code=429, retry_after=0.3)

    def fake_check(self: MarkdownURL, **kwargs: object) -> URLCheckResult:
        calls.append(time.monotonic())
        return rate_limited

    try:
        with patch.object(MarkdownURL, "check", fake_check):
            future1 = service.submit(_url("https://persistent.example.com/1"))
            future2 = service.submit(_url("https://persistent.example.com/2"))
            result1 = future1.result(timeout=5)
            result2 = future2.result(timeout=5)
    finally:
        service.close()

    assert result1.status == "rate_limited"
    assert result2.status == "rate_limited"
    # job1 is checked twice (initial + one requeue) before the host is marked persistent;
    # job2 is drained directly from the queue and never reaches the network.
    assert len(calls) == 2


def test_persistent_rate_limit_blocks_new_submissions_during_cooldown():
    """A new submission for a host that is mid-cooldown is resolved immediately."""
    config = Config(max_workers=1, per_host_delay=0.0)
    service = URLCheckService(config)
    calls: list[float] = []

    def fake_check(self: MarkdownURL, **kwargs: object) -> URLCheckResult:
        calls.append(time.monotonic())
        # Short wait before the requeued attempt, then a long cooldown once persistent
        # throttling is detected, so the test stays fast but still exercises the window.
        retry_after = 0.2 if len(calls) == 1 else 5
        return URLCheckResult(status="rate_limited", http_status_code=429, retry_after=retry_after)

    try:
        with patch.object(MarkdownURL, "check", fake_check):
            future1 = service.submit(_url("https://cooldown.example.com/1"))
            result1 = future1.result(timeout=5)
            # By now the host has requeued once and hit persistent throttling (2 calls) and
            # is blocked for ~5s. A submission arriving during that window must not queue.
            future2 = service.submit(_url("https://cooldown.example.com/2"))
            result2 = future2.result(timeout=5)
    finally:
        service.close()

    assert result1.status == "rate_limited"
    assert result2.status == "rate_limited"
    assert len(calls) == 2, "the second URL should have been drained, not sent over the network"


# --- backpressure ---


def test_backpressure_blocks_submit_until_slot_frees():
    """submit() blocks the single producer thread once max_pending jobs are outstanding."""
    config = Config(max_workers=2, max_pending=2, per_host_delay=0.0)
    service = URLCheckService(config)
    release = threading.Event()
    alive = URLCheckResult(status="alive", http_status_code=200)

    def fake_check(self: MarkdownURL, **kwargs: object) -> URLCheckResult:
        if "host-c" not in self.link:
            release.wait(timeout=5)
        return alive

    third_submitted = threading.Event()
    futures: list[Future[URLCheckResult]] = []

    def producer() -> None:
        # All submissions come from this single producer thread, per the single-producer contract.
        futures.append(service.submit(_url("https://host-a.example.com/1")))
        futures.append(service.submit(_url("https://host-b.example.com/1")))
        # Both permits are now held by the blocking jobs above; this call must block until
        # one of them completes and releases a permit.
        futures.append(service.submit(_url("https://host-c.example.com/1")))
        third_submitted.set()

    try:
        with patch.object(MarkdownURL, "check", fake_check):
            thread = threading.Thread(target=producer)
            thread.start()
            time.sleep(0.2)
            assert not third_submitted.is_set(), "submit() did not apply backpressure"

            release.set()
            thread.join(timeout=5)
            assert third_submitted.is_set()
            assert futures[2].result(timeout=5).status == "alive"
    finally:
        release.set()
        service.close()


# --- single-producer contract ---


def test_submit_from_second_thread_raises():
    """submit() from a second thread after the first raises RuntimeError."""
    config = Config(max_workers=1)
    service = URLCheckService(config)
    alive = URLCheckResult(status="alive", http_status_code=200)
    errors: list[BaseException] = []

    def other_thread_submit() -> None:
        try:
            service.submit(_url("https://second-thread.example.com/1"))
        except BaseException as exc:  # noqa: BLE001 - captured to assert on in the test thread
            errors.append(exc)

    try:
        with patch.object(MarkdownURL, "check", return_value=alive):
            service.submit(_url("https://first-thread.example.com/1")).result(timeout=5)
            thread = threading.Thread(target=other_thread_submit)
            thread.start()
            thread.join(timeout=5)
    finally:
        service.close()

    assert len(errors) == 1
    assert isinstance(errors[0], RuntimeError)
    assert "single producer thread" in str(errors[0])


# --- worker exception safety ---


def test_unexpected_exception_resolves_as_transient_error():
    """An unexpected exception from check() resolves the future instead of leaving it hanging."""
    config = Config(max_workers=1)
    service = URLCheckService(config)

    def raising_check(self: MarkdownURL, **kwargs: object) -> URLCheckResult:
        raise ValueError("boom")

    try:
        with patch.object(MarkdownURL, "check", raising_check):
            future = service.submit(_url("https://exploding.example.com/1"))
            result = future.result(timeout=5)
    finally:
        service.close()

    assert result.status == "transient_error"


# --- shutdown ---


def test_close_joins_all_worker_threads():
    """close() joins every worker thread; none remain alive afterwards."""
    config = Config(max_workers=3)
    service = URLCheckService(config)
    workers = list(service._workers)  # noqa: SLF001 - internal, but this is a whitebox test
    assert all(worker.is_alive() for worker in workers)
    service.close()
    assert all(not worker.is_alive() for worker in workers)
