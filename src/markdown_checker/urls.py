import time
from dataclasses import dataclass
from urllib.parse import ParseResult, urlparse

import requests

from markdown_checker.markdown_link_base import MarkdownLinkBase


@dataclass
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

    def is_alive(self, timeout: int = 10, retries: int = 3) -> bool:
        """
        Check if the URL is alive

        Args:
            timeout (int): Timeout for the request in seconds.
            retries (int): Number of retries if the request fails.

        Returns:
            bool: True if the URL is alive, False otherwise
        """
        for _ in range(retries):
            try:
                response = requests.head(self.link, timeout=timeout, allow_redirects=True)
                if response.status_code == 200:
                    return True
                else:
                    response = requests.get(self.link, timeout=timeout, allow_redirects=True)
                    if response.status_code == 200:
                        return True
            except requests.RequestException:
                continue
            time.sleep(1)
        return False
