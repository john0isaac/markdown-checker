import re
from dataclasses import dataclass
from pathlib import Path

from markdown_checker.paths import MarkdownPath
from markdown_checker.urls import MarkdownURL


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
    link_pattern = re.compile(r"\]\((.*?)\)| \)")
    url_pattern = re.compile(
        r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9]{1,6}\b([-a-zA-Z0-9@:%_\+.~#?&\/\/=]*)"
    )
    path_pattern = re.compile(r"(?:\.{1,2}\/|\/)+(?:[A-Za-z0-9-]+\/)*(?:.+\.[A-Za-z]+)")

    with open(file_path, encoding="utf-8") as file:
        data = file.readlines()
        line_count = 1
        for line in data:
            matches = re.finditer(link_pattern, line)
            for matched_group in matches:
                matched_link = matched_group.group(1)
                if matched_link:
                    matched_url = re.findall(url_pattern, matched_link)
                    matched_path = re.findall(path_pattern, matched_link)
                    if matched_url:
                        markdown_links.urls.append(
                            MarkdownURL(
                                link=matched_link,
                                line_number=line_count,
                                file_path=file_path,
                            )
                        )
                    elif matched_path:
                        markdown_links.paths.append(
                            MarkdownPath(
                                link=matched_link,
                                line_number=line_count,
                                file_path=file_path,
                            )
                        )
            line_count += 1
    return markdown_links
