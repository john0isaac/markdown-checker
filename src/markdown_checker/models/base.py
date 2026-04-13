import re
from abc import ABC
from dataclasses import dataclass
from pathlib import Path

_LOCALE_PATTERN = re.compile(r"\/[a-z]{2}-[a-z]{2}\/")
_TRACKING_PATTERN = re.compile(r"(\?|\&)(WT|wt)\.mc_id=")


@dataclass(slots=True)
class MarkdownLinkBase(ABC):
    """Base class for markdown links"""

    link: str
    line_number: int
    file_path: Path
    issue: str = ""

    def has_locale(self) -> bool:
        """
        Check if the link has a locale

        Returns:
            True if the link has a locale, False otherwise
        """
        return bool(_LOCALE_PATTERN.search(self.link))

    def has_tracking(self) -> bool:
        """
        Check if the link has a tracking ID

        Returns:
            True if the link has a tracking ID, False otherwise
        """
        return bool(_TRACKING_PATTERN.search(self.link))

    def __str__(self) -> str:
        return self.link

    def __repr__(self) -> str:
        return self.link
