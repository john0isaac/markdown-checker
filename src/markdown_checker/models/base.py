from abc import ABC
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from markdown_checker.patterns import LOCALE_PATTERN
from markdown_checker.patterns import TRACKING_PATTERN


@dataclass(slots=True)
class MarkdownLinkBase(ABC):
    """Base class for markdown links"""

    link: str
    line_number: int
    file_path: Path
    issue: str = ""
    issue_level: Literal["error", "warning"] = "error"

    def has_locale(self) -> bool:
        """
        Check if the link has a locale

        Returns:
            True if the link has a locale, False otherwise
        """
        return bool(LOCALE_PATTERN.search(self.link))

    def has_tracking(self) -> bool:
        """
        Check if the link has a tracking ID

        Returns:
            True if the link has a tracking ID, False otherwise
        """
        return bool(TRACKING_PATTERN.search(self.link))

    def __str__(self) -> str:
        return self.link

    def __repr__(self) -> str:
        return self.link
