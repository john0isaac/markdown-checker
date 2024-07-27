import re
from abc import ABC
from dataclasses import dataclass
from pathlib import Path


@dataclass
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
            bool: True if the link has a locale, False otherwise
        """
        locale_pattern = re.compile(r"\/[a-z]{2}-[a-z]{2}\/")
        matches = re.findall(locale_pattern, self.link)
        return bool(matches)

    def has_tracking(self) -> bool:
        """
        Check if the link has a tracking ID

        Returns:
            bool: True if the link has a tracking ID, False otherwise
        """
        tracking_pattern = re.compile(r"(\?|\&)(WT|wt)\.mc_id=")
        matches = re.findall(tracking_pattern, self.link)
        return bool(matches)

    def __str__(self) -> str:
        return self.link

    def __repr__(self) -> str:
        return self.link
