"""Extracts markdown link destinations from a file, split into URLs and paths."""

from dataclasses import dataclass
from pathlib import Path

from markdown_checker.models.path import MarkdownPath
from markdown_checker.models.url import MarkdownURL
from markdown_checker.patterns import FENCE_OPEN_PATTERN
from markdown_checker.patterns import LINK_PATTERN
from markdown_checker.patterns import SCHEME_PATTERN


@dataclass
class MarkdownLinks:
    """The links found in one markdown file, split by kind."""

    urls: list[MarkdownURL]
    """Web URLs (``http://``/``https://``, including protocol-relative
    ``//host/...`` links, which are normalized to ``https:``).
    """

    paths: list[MarkdownPath]
    """Relative or root-relative file paths (anything that is neither a URL
    nor a link with another URI scheme, e.g. ``mailto:``, nor a bare
    ``#fragment``).
    """


def get_links_from_md_file(file_path: Path) -> MarkdownLinks:
    """Extract every markdown link destination from a file.

    Scans each line for inline links of the form ``[text](destination)`` (see
    :data:`~markdown_checker.patterns.LINK_PATTERN`), skipping lines inside
    fenced code blocks (marked with three or more backtick or tilde
    characters) so example links in code samples are never checked. Each
    destination is then classified as:

    - a **URL** if it starts with ``http://``/``https://`` (or ``//``, which
      is treated as ``https://``);
    - ignored if it starts with another URI scheme (e.g. ``mailto:``) or is a
      bare same-page anchor (``#section``);
    - a **path** otherwise, e.g. ``./img.png``, ``../docs/usage.md``, or a
      bare ``docs/usage.md``.

    Args:
        file_path (Path): The file path to check.

    Returns:
        markdown_links (MarkdownLinks): Dataclass with urls and paths
    """
    markdown_links = MarkdownLinks(urls=[], paths=[])
    fence_marker: str | None = None
    fence_len: int = 0

    with open(file_path, encoding="utf-8", errors="replace") as file:
        for line_number, line in enumerate(file, start=1):
            # Track fenced code blocks (``` or ~~~)
            fence_match = FENCE_OPEN_PATTERN.match(line)
            if fence_match:
                marker = fence_match.group(1)[0]  # '`' or '~'
                match_len = len(fence_match.group(1))
                if fence_marker is None:
                    # Opening fence, remember char and length
                    fence_marker = marker
                    fence_len = match_len
                elif marker == fence_marker and match_len >= fence_len:
                    # Closing fence (same char, at least as long as opening)
                    fence_marker = None
                    fence_len = 0
                continue
            if fence_marker is not None:
                continue

            for matched_group in LINK_PATTERN.finditer(line):
                matched_link = matched_group.group("angle") or matched_group.group("plain")
                if not matched_link:
                    continue
                if matched_link.startswith("//"):
                    # Protocol-relative URL, check as https
                    matched_link = "https:" + matched_link
                if matched_link.startswith(("http://", "https://")):
                    markdown_links.urls.append(
                        MarkdownURL(
                            link=matched_link,
                            line_number=line_number,
                            file_path=file_path,
                        )
                    )
                elif not matched_link.startswith("#") and not SCHEME_PATTERN.match(matched_link):
                    markdown_links.paths.append(
                        MarkdownPath(
                            link=matched_link,
                            line_number=line_number,
                            file_path=file_path,
                        )
                    )
    return markdown_links
