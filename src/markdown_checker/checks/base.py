from abc import ABC, abstractmethod

from markdown_checker.models.base import MarkdownLinkBase
from markdown_checker.utils.extract_links import MarkdownLinks


class BaseCheck(ABC):
    """Abstract base class for all link checks."""

    name: str

    @abstractmethod
    def run(
        self,
        links: MarkdownLinks,
        skip_domains: list[str] | None = None,
        skip_urls_containing: list[str] | None = None,
        tracking_domains: list[str] | None = None,
        timeout: int = 15,
        retries: int = 3,
    ) -> list[MarkdownLinkBase]:
        """
        Run the check against the extracted links.

        Args:
            links (MarkdownLinks): Extracted URLs and paths from a file.
            skip_domains: Domains to skip entirely.
            skip_urls_containing: Skip URLs that contain any of these substrings.
            tracking_domains: Domains that require a tracking ID.
            timeout: HTTP request timeout in seconds.
            retries: Number of retry attempts for HTTP requests.

        Returns:
            List of links that failed the check, each with an .issue set.
        """
        raise NotImplementedError
