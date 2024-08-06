import os
import re
from dataclasses import dataclass
from pathlib import Path

from markdown_checker.markdown_link_base import MarkdownLinkBase


@dataclass
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
        # Find the last occurrence of the dot
        dot_index = self.link.rfind(".")
        self.link = re.sub(r"(\?|\&)(WT|wt)\.mc_id=.*", "", self.link)

        # If a dot is found, slice the string up to the end of the extension
        if dot_index != -1:
            # Find the next slash or fragment after the dot
            slash_index = self.link.find("/", dot_index)
            fragment_index = self.link.find("#", dot_index)

            # Determine the earliest occurrence of either slash or fragment or query
            end_index = min(
                slash_index if slash_index != -1 else len(self.link),
                fragment_index if fragment_index != -1 else len(self.link),
            )
            return self.link[:end_index]
        else:
            return self.link

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
        # Paths starting with / are considered absolute and not resolved
        # so we need to remove the / and check if the path exists
        changed = False
        if self.link.startswith("/"):
            self.link = self.link[1:]
            changed = True
        # Check if the path exists using the relative path resolution
        if os.path.exists(self.get_full_path_relative()):
            return True
        # Check if the path exists using the full path resolution recursively
        if self.get_full_path().exists():
            return True
        # Change the link back to the original value
        if changed:
            self.link = "/" + self.link
        return False
