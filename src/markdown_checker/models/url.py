import email.utils
import time
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from typing import Literal
from urllib.parse import ParseResult
from urllib.parse import urlparse

import httpx2

from markdown_checker.models.base import MarkdownLinkBase
from markdown_checker.models.config import create_http_client


@dataclass(slots=True)
class URLCheckResult:
    """Typed outcome of checking whether a URL is reachable."""

    status: Literal["alive", "broken", "rate_limited", "transient_error", "unverifiable"]
    """One of:

    - ``alive``: A 2xx response was received. The link is healthy.
    - ``broken``: All retries returned a non-2xx response with no
      rate-limit or auth signal. Reported as an error-level issue.
    - ``rate_limited``: A 429 (or another non-success response carrying
      ``Retry-After``) was seen. Reported as a warning-level issue; never
      fails the run.
    - ``unverifiable``: Both HEAD and GET returned 401/403 - the server is
      reachable but blocking automated access. Reported as a warning-level issue.
    - ``transient_error``: A network-level error (DNS failure, connection
      timeout, etc.) with no HTTP response at all. Reported as a
      warning-level issue.
    """

    http_status_code: int | None = None
    """The last HTTP status code observed, or None if no response was ever
    received (e.g. ``transient_error``).
    """

    retry_after: int | None = None
    """Seconds the caller should wait before retrying, set only when
    ``status`` is ``rate_limited``.
    """


def _retry_after_delay(response: httpx2.Response, fallback: int) -> float | None:
    """Return seconds to sleep if the response warrants a Retry-After wait.

    Returns None when normal exponential backoff should be used instead.
    """
    is_429 = response.status_code == 429
    has_retry_after = "retry-after" in response.headers
    triggered = is_429 or (not response.is_success and not response.is_redirect and has_retry_after)
    if not triggered:
        return None

    header = response.headers.get("retry-after")
    if header:
        # Try integer seconds first.
        try:
            return float(header.strip())
        except ValueError:
            pass
        # Try HTTP-date format (e.g. "Wed, 21 Oct 2015 07:28:00 GMT").
        try:
            dt: datetime = email.utils.parsedate_to_datetime(header)
            now: datetime = datetime.now(timezone.utc)
            delay: float = (dt - now).total_seconds()
            return max(0.0, delay)
        except Exception:
            pass

    return float(fallback)


@dataclass(slots=True)
class MarkdownURL(MarkdownLinkBase):
    """A single web URL extracted from a markdown file, plus the ability to check it."""

    @property
    def parsed_url(self) -> ParseResult:
        """
        Parse the URL and return the result

        Returns:
            ParseResult: The parsed URL
        """
        return urlparse(self.link)

    def host_name(self) -> str:
        """
        Return the URL's hostname (netloc), including any port but not the
        scheme, e.g. ``"example.com"`` for ``"https://example.com/path"``.
        """
        return self.parsed_url.netloc

    def check(
        self,
        timeout: int = 20,
        retries: int = 3,
        client: httpx2.Client | None = None,
        retry_on_429: bool = True,
        fallback_retry_delay: int = 30,
    ) -> URLCheckResult:
        """
        Check whether the URL is reachable and return a typed outcome.

        Rate-limit signals (429, or any non-success response carrying a
        Retry-After header) and auth errors (401/403) are returned
        immediately without sleeping or retrying: retrying them wastes
        traffic against hosts that are already blocking or throttling us.
        Callers that want to wait out a rate limit (e.g. a host-level
        circuit breaker) should do so themselves using ``retry_after``.

        Args:
            timeout (int): Timeout for the request in seconds.
            retries (int): Number of retries if the request fails.
            client (httpx2.Client | None): Optional shared client for connection pooling.
            retry_on_429 (bool): When True, honour Retry-After headers on 429 responses.
            fallback_retry_delay (int): Seconds to wait when a 429 carries no Retry-After header.

        Returns:
            URLCheckResult with status one of: ``alive``, ``broken``,
            ``rate_limited``, ``unverifiable``, or ``transient_error``.
        """
        _client = client or create_http_client()
        last_status_code: int | None = None
        saw_hard_failure = False
        try:
            for attempt in range(retries):
                try:
                    response = _client.head(self.link, timeout=timeout)
                    last_status_code = response.status_code
                    if response.is_success:
                        return URLCheckResult(status="alive", http_status_code=response.status_code)
                    if retry_on_429:
                        delay = _retry_after_delay(response, fallback_retry_delay)
                        if delay is not None:
                            return URLCheckResult(
                                status="rate_limited", http_status_code=response.status_code, retry_after=int(delay)
                            )
                    # Fall back to GET - some servers reject HEAD but allow GET.
                    response = _client.get(self.link, timeout=timeout)
                    last_status_code = response.status_code
                    if response.is_success:
                        return URLCheckResult(status="alive", http_status_code=response.status_code)
                    if retry_on_429:
                        delay = _retry_after_delay(response, fallback_retry_delay)
                        if delay is not None:
                            return URLCheckResult(
                                status="rate_limited", http_status_code=response.status_code, retry_after=int(delay)
                            )
                    if response.status_code in (401, 403):
                        # 401/403 means the server exists but is blocking automated access.
                        # Retrying will not change the outcome, so return immediately.
                        return URLCheckResult(status="unverifiable", http_status_code=response.status_code)
                    saw_hard_failure = True
                except httpx2.UnsupportedProtocol:
                    # Server redirected to a non-HTTP scheme (e.g. vscode://).
                    # The original URL is reachable; treat it as alive.
                    return URLCheckResult(status="alive", http_status_code=None)
                except (httpx2.HTTPError, RuntimeError):
                    pass
                if attempt < retries - 1:
                    time.sleep(0.5 * 2**attempt)
        finally:
            if client is None:
                _client.close()
        if saw_hard_failure:
            return URLCheckResult(status="broken", http_status_code=last_status_code)
        return URLCheckResult(status="transient_error", http_status_code=None)
