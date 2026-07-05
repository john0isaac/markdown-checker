"""Shared base dataclass for the two kinds of link markdown-checker extracts: URLs and paths."""

from abc import ABC
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from markdown_checker.patterns import LOCALE_PATTERN
from markdown_checker.patterns import TRACKING_PATTERN


@dataclass(slots=True)
class MarkdownLinkBase(ABC):
    """Base class for a single link found in a markdown file."""

    link: str
    """The raw link destination as written in the file (e.g.
    ``"https://example.com"`` or ``"../img.png"``).
    """

    line_number: int
    """1-based line number where the link was found."""

    file_path: Path
    """Path to the markdown file the link was found in."""

    issue: str = ""
    """Human-readable description set by a check when this link fails it
    (e.g. ``"is broken"``); empty when no issue was found.
    """

    issue_level: Literal["error", "warning"] = "error"
    """Severity of ``issue`` once set. ``"error"`` fails the CLI run (exit
    code 1); ``"warning"`` is reported but never fails it.
    """

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
