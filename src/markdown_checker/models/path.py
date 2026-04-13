import os
import re
from dataclasses import dataclass
from pathlib import Path

from markdown_checker.models.base import MarkdownLinkBase

_TRACKING_QUERY_PATTERN = re.compile(r"(\?|\&)(WT|wt)\.mc_id=.*")


@dataclass(slots=True)
class MarkdownPath(MarkdownLinkBase):
    """Dataclass to store info about a path"""

    @property
    def path_without_fragments(self) -> Path:
        """
        Get the path without the fragment

        Returns:
            The path without the fragment
        """
        return Path(self.remove_fragments())

    def remove_fragments(self) -> str:
        """
        Remove the fragments from a path

        Returns:
            The path without the fragment
        """
        cleaned = _TRACKING_QUERY_PATTERN.sub("", self.link)

        # Find the last occurrence of the dot
        dot_index = cleaned.rfind(".")

        # If a dot is found, slice the string up to the end of the extension
        if dot_index != -1:
            # Find the next slash or fragment after the dot
            slash_index = cleaned.find("/", dot_index)
            fragment_index = cleaned.find("#", dot_index)

            # Determine the earliest occurrence of either slash or fragment or query
            end_index = min(
                slash_index if slash_index != -1 else len(cleaned),
                fragment_index if fragment_index != -1 else len(cleaned),
            )
            return cleaned[:end_index]
        else:
            return cleaned

    def get_full_path(self) -> Path:
        """
        Get the full path of the file by resolving the path without fragments

        Returns:
            The full path of the file
        """
        try:
            return self.path_without_fragments.resolve()
        except (FileNotFoundError, RuntimeError):
            return Path(self.get_full_path_relative())

    def get_full_path_relative(self) -> str:
        """
        Get the full path of the file by resolving the path without fragments

        Returns:
            The full path of the file
        """
        return os.path.normpath(os.path.join(os.path.dirname(self.file_path), self.remove_fragments()))

    def exists(self) -> bool:
        """
        Check if the path exists

        Returns:
            True if the path exists, False otherwise
        """
        # For paths starting with /, strip the leading / to allow relative resolution
        link = self.link.lstrip("/") if self.link.startswith("/") else self.link
        cleaned = _TRACKING_QUERY_PATTERN.sub("", link)

        # Strip fragments/anchors the same way remove_fragments() does
        dot_index = cleaned.rfind(".")
        if dot_index != -1:
            slash_index = cleaned.find("/", dot_index)
            fragment_index = cleaned.find("#", dot_index)
            end_index = min(
                slash_index if slash_index != -1 else len(cleaned),
                fragment_index if fragment_index != -1 else len(cleaned),
            )
            cleaned = cleaned[:end_index]

        # Check relative path resolution
        relative_path = os.path.normpath(os.path.join(os.path.dirname(self.file_path), cleaned))
        if os.path.exists(relative_path):
            return True
        # Check absolute path resolution
        try:
            if Path(cleaned).resolve().exists():
                return True
        except (FileNotFoundError, RuntimeError, OSError):
            resolved = Path(relative_path)
            if resolved.exists():
                return True
        return False
