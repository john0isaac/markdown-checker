"""
Module to format the output of the markdown checker.
"""

from typing import Union

from markdown_checker.paths import MarkdownPath
from markdown_checker.urls import MarkdownURL


def format_links(links: list[Union[MarkdownPath, MarkdownURL]]) -> str:
    """
    Formats a List of links into a string with numbered bullets.

    Args:
        links (list[Union[MarkdownPath, MarkdownURL]]): The list of links to format.

    Returns:
        formatted_links (str): The formatted string with numbered bullets.
    """
    formatted_links = ""
    i = 1
    for link in links:
        if i == len(links):
            formatted_links += f" {i}. `{link}` |\n"
        else:
            formatted_links += f" {i}. `{link}` <br/>"
        i += 1

    return formatted_links
