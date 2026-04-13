import re
from dataclasses import dataclass
from pathlib import Path

from markdown_checker.models.path import MarkdownPath
from markdown_checker.models.url import MarkdownURL

_LINK_PATTERN = re.compile(r"\]\((.*?)\)| \)")
_URL_PATTERN = re.compile(
    r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9]{1,6}\b([-a-zA-Z0-9@:%_\+.~#?&\/\/=]*)"
)
_PATH_PATTERN = re.compile(r"(?:\.{1,2}\/|\/)+(?:[A-Za-z0-9-]+\/)*(?:.+\.[A-Za-z]+)")
_FENCE_OPEN = re.compile(r"^\s*(`{3,}|~{3,})")


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

    with open(file_path, encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            # Track fenced code blocks (``` or ~~~)
            fence_match = _FENCE_OPEN.match(line)
            if fence_match:
                marker = fence_match.group(1)[0]  # '`' or '~'
                min_len = len(fence_match.group(1))
                if fence_marker is None:
                    # Opening fence
                    fence_marker = marker
                elif line.strip().startswith(marker * min_len) and marker == fence_marker:
                    # Closing fence (same char, at least as many)
                    fence_marker = None
                continue
            if fence_marker is not None:
                continue

            for matched_group in _LINK_PATTERN.finditer(line):
                matched_link = matched_group.group(1)
                if matched_link:
                    if _URL_PATTERN.findall(matched_link):
                        markdown_links.urls.append(
                            MarkdownURL(
                                link=matched_link,
                                line_number=line_number,
                                file_path=file_path,
                            )
                        )
                    elif _PATH_PATTERN.findall(matched_link):
                        markdown_links.paths.append(
                            MarkdownPath(
                                link=matched_link,
                                line_number=line_number,
                                file_path=file_path,
                            )
                        )
    return markdown_links
