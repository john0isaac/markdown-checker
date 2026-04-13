import time
from dataclasses import dataclass
from urllib.parse import ParseResult, urlparse

import httpx

from markdown_checker.models.base import MarkdownLinkBase
from markdown_checker.models.config import create_http_client


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

    def is_alive(self, timeout: int = 20, retries: int = 3, client: httpx.Client | None = None) -> bool:
        """
        Check if the URL is alive

        Args:
            timeout (int): Timeout for the request in seconds.
            retries (int): Number of retries if the request fails.
            client (httpx.Client | None): Optional shared client for connection pooling.

        Returns:
            bool: True if the URL is alive, False otherwise
        """
        _client = client or create_http_client()
        try:
            for attempt in range(retries):
                try:
                    response = _client.head(self.link, timeout=timeout)
                    if response.is_success:
                        return True
                    response = _client.get(self.link, timeout=timeout)
                    if response.is_success:
                        return True
                except httpx.UnsupportedProtocol:
                    # Server redirected to a non-HTTP scheme (e.g. vscode://).
                    # The original URL is reachable; treat it as alive.
                    return True
                except (httpx.HTTPError, RuntimeError):
                    pass
                if attempt < retries - 1:
                    time.sleep(0.5 * 2**attempt)
        finally:
            if client is None:
                _client.close()
        return False
