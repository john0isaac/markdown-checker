from dataclasses import dataclass
from pathlib import Path

from markdown_checker.models.path import MarkdownPath
from markdown_checker.models.url import MarkdownURL
from markdown_checker.patterns import FENCE_OPEN_PATTERN
from markdown_checker.patterns import LINK_PATTERN
from markdown_checker.patterns import SCHEME_PATTERN


@dataclass
class MarkdownLinks:
    """Dataclass to store markdown links"""

    urls: list[MarkdownURL]
    paths: list[MarkdownPath]


def get_links_from_md_file(file_path: Path) -> MarkdownLinks:
    """function to get an array of markdown urls, paths from a file
    flags markdown links captures the part inside () that comes right after []

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
