import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

from markdown_checker.models.base import MarkdownLinkBase
from markdown_checker.patterns import QUERY_OR_ANCHOR_PATTERN
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
        fragment from the link, then percent-decode what's left (e.g.
        ``my%20file.md`` becomes ``my file.md``), leaving just the file path.

        As in any URL, the first ``?`` or ``#`` starts the fragment, so a
        literal ``#`` or ``?`` in a file name must be written as ``%23``/``%3F``.

        Returns:
            The link with its fragment removed, as a string.
        """
        cleaned = TRACKING_QUERY_PATTERN.sub("", self.link)
        return unquote(QUERY_OR_ANCHOR_PATTERN.sub("", cleaned))

    def get_full_path(self) -> Path:
        """
        Resolve the link (with its fragment stripped) to an absolute path.

        Root-relative links (e.g. ``/docs/usage.md``) resolve against the
        current working directory, which is treated as the repository root.
        Other links resolve relative to the current working directory too;
        if that fails (e.g. on an unusual path), this falls back to
        :meth:`get_full_path_relative`.

        Returns:
            The resolved absolute path.
        """
        cleaned = self.remove_fragments()
        if cleaned.startswith("/"):
            return Path(os.path.normpath(Path.cwd() / cleaned.lstrip("/")))
        try:
            return Path(cleaned).resolve()
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

        Tries resolution relative to the containing markdown file first, then
        relative to the current working directory. Root-relative links (e.g.
        ``/docs/usage.md``) are tried the same way with the leading ``/``
        dropped. Used by ``check_broken_paths`` to flag links whose target is
        missing.

        Returns:
            True if the path exists, False otherwise
        """
        cleaned = self.remove_fragments().lstrip("/")

        relative_path = os.path.normpath(os.path.join(os.path.dirname(self.file_path), cleaned))
        if os.path.exists(relative_path):
            return True
        try:
            return Path(cleaned).resolve().exists()
        except (FileNotFoundError, RuntimeError, OSError):
            return False
