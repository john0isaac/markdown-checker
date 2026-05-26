import email.utils
import time
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from urllib.parse import ParseResult
from urllib.parse import urlparse

import httpx2

from markdown_checker.models.base import MarkdownLinkBase
from markdown_checker.models.config import create_http_client


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
            dt = email.utils.parsedate_to_datetime(header)
            now = datetime.now(timezone.utc)
            delay = (dt - now).total_seconds()
            return max(0.0, delay)
        except Exception:
            pass

    return float(fallback)


@dataclass(slots=True)
class MarkdownURL(MarkdownLinkBase):
    """Dataclass to store info about a url"""

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
        Returns the hostname of the URL without the protocol
        """
        return self.parsed_url.netloc

    def is_alive(
        self,
        timeout: int = 20,
        retries: int = 3,
        client: httpx2.Client | None = None,
        retry_on_429: bool = True,
        fallback_retry_delay: int = 30,
    ) -> bool:
        """
        Check if the URL is alive

        Args:
            timeout (int): Timeout for the request in seconds.
            retries (int): Number of retries if the request fails.
            client (httpx2.Client | None): Optional shared client for connection pooling.
            retry_on_429 (bool): When True, honour Retry-After headers on 429 responses.
            fallback_retry_delay (int): Seconds to wait when a 429 carries no Retry-After header.

        Returns:
            bool: True if the URL is alive, False otherwise
        """
        _client = client or create_http_client()
        try:
            for attempt in range(retries):
                sleep_override: float | None = None
                try:
                    response = _client.head(self.link, timeout=timeout)
                    if response.is_success:
                        return True
                    if retry_on_429:
                        sleep_override = _retry_after_delay(response, fallback_retry_delay)
                    if sleep_override is None:
                        response = _client.get(self.link, timeout=timeout)
                        if response.is_success:
                            return True
                        if retry_on_429:
                            sleep_override = _retry_after_delay(response, fallback_retry_delay)
                except httpx2.UnsupportedProtocol:
                    # Server redirected to a non-HTTP scheme (e.g. vscode://).
                    # The original URL is reachable; treat it as alive.
                    return True
                except (httpx2.HTTPError, RuntimeError):
                    pass
                if attempt < retries - 1:
                    if sleep_override is not None:
                        time.sleep(sleep_override)
                    else:
                        time.sleep(0.5 * 2**attempt)
        finally:
            if client is None:
                _client.close()
        return False
