import os
from dataclasses import dataclass
from pathlib import Path

from markdown_checker.models.base import MarkdownLinkBase
from markdown_checker.patterns import TRACKING_QUERY_PATTERN


@dataclass(slots=True)
class MarkdownPath(MarkdownLinkBase):
    """A relative (or root-relative) file path extracted from a markdown link.

    "Fragment" below always means the trailing ``?query`` and/or ``#anchor``
    part of the link, e.g. in ``docs/usage.md#section?wt.mc_id=x`` the
    fragment is ``#section?wt.mc_id=x`` and the path is ``docs/usage.md``.
    """

    @property
    def path_without_fragments(self) -> Path:
        """
        The link as a :class:`~pathlib.Path`, with any query/anchor fragment
        stripped. Equivalent to ``Path(self.remove_fragments())``.
        """
        return Path(self.remove_fragments())

    def remove_fragments(self) -> str:
        """
        Strip the tracking query string and any trailing ``?query``/``#anchor``
        fragment from the link, leaving just the file path portion.

        Returns:
            The link with its fragment removed, as a string.
        """
        cleaned = TRACKING_QUERY_PATTERN.sub("", self.link)

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
        Resolve the link (with its fragment stripped) to an absolute path,
        relative to the current working directory.

        This is used for links that are themselves absolute (e.g.
        ``/docs/usage.md``) or otherwise resolvable without knowing which
        file the link appeared in. If resolution fails (e.g. on an unusual
        path), falls back to :meth:`get_full_path_relative`.

        Returns:
            The resolved absolute path.
        """
        try:
            return self.path_without_fragments.resolve()
        except (FileNotFoundError, RuntimeError):
            return Path(self.get_full_path_relative())

    def get_full_path_relative(self) -> str:
        """
        Resolve the link (with its fragment stripped) relative to the
        directory of the markdown file it was found in (``self.file_path``),
        e.g. a link ``../img.png`` found in ``docs/usage.md`` resolves
        against ``docs/``.

        Returns:
            The resolved path, as a normalized string.
        """
        return os.path.normpath(os.path.join(os.path.dirname(self.file_path), self.remove_fragments()))

    def exists(self) -> bool:
        """
        Check whether the link's target file exists on disk.

        Tries resolution relative to the containing markdown file first
        (see :meth:`get_full_path_relative`), then as an absolute/CWD-relative
        path (see :meth:`get_full_path`). Used by ``check_broken_paths`` to
        flag links whose target is missing.

        Returns:
            True if the path exists, False otherwise
        """
        # For paths starting with /, strip the leading / to allow relative resolution
        link = self.link.lstrip("/") if self.link.startswith("/") else self.link
        cleaned = TRACKING_QUERY_PATTERN.sub("", link)

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
