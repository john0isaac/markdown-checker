from abc import ABC, abstractmethod
from typing import Literal

import httpx

from markdown_checker.models import Config, MarkdownLinkBase
from markdown_checker.utils.extract_links import MarkdownLinks


class BaseCheck(ABC):
    """Abstract base class for all link checks."""

    name: str
    link_type: Literal["paths", "urls"]

    @abstractmethod
    def run(
        self,
        links: MarkdownLinks,
        config: Config | None = None,
        client: httpx.Client | None = None,
    ) -> list[MarkdownLinkBase]:
        """
        Run the check against the extracted links.

        Args:
            links (MarkdownLinks): Extracted URLs and paths from a file.
            config: Runtime configuration for the check run.
            client: Optional shared HTTP client (used by URL checks).

        Returns:
            List of links that failed the check, each with an .issue set.
        """
        raise NotImplementedError
