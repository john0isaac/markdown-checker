"""
Module to format the output of the markdown checker.
"""

import os
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
    formatted_links = "<table><thead><tr><th>#</th><th>Link</th><th>Line Number</th></tr></thead><tbody>"
    # Ref: https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/variables#default-environment-variables
    github_ci = os.getenv("CI", "false")
    # repo_name = os.getenv("GITHUB_REPOSITORY", "../tree/")
    # branch_name = os.getenv("GITHUB_HEAD_REF", os.getenv("GITHUB_REF_NAME", "main"))
    # repo name is always target repo in PR not source
    # need more work in upcoming release
    if github_ci == "true":
        for link in range(len(links)):
            formatted_links += (
                f"<tr><td>{link + 1}</td><td>`{links[link].link}`</td><td>`{links[link].line_number}`</td></tr>"
            )
    else:
        for link in range(len(links)):
            formatted_links += (
                f"<tr><td>{link + 1}</td><td>`{links[link].link}`</td>"
                f"<td>[`{links[link].line_number}`]({links[link].file_path}#L{links[link].line_number})</td></tr>"
            )

    formatted_links += "</tbody></table>|\n"
    return formatted_links
