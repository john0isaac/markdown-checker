"""
Module to format check results into markdown output.
"""

from pathlib import Path
from typing import Literal

from markdown_checker.models.base import MarkdownLinkBase


def format_links(links: list[MarkdownLinkBase], output_mode: Literal["ci", "local"] = "local") -> str:
    """
    Formats a List of links into a string with numbered bullets.

    Args:
        links (list[MarkdownLinkBase]): The list of links to format.
        output_mode: "ci" omits file links; "local" includes clickable links.

    Returns:
        formatted_links (str): The formatted string with numbered bullets.
    """
    parts: list[str] = ["<table><thead><tr><th>#</th><th>Link</th><th>Line Number</th></tr></thead><tbody>"]
    if output_mode == "ci":
        for i, item in enumerate(links, 1):
            parts.append(f"<tr><td>{i}</td><td>`{item.link}`</td><td>`{item.line_number}`</td></tr>")
    else:
        for i, item in enumerate(links, 1):
            parts.append(
                f"<tr><td>{i}</td><td>`{item.link}`</td>"
                f"<td>[`{item.line_number}`]({item.file_path}#L{item.line_number})</td></tr>"
            )

    parts.append("</tbody></table>|\n")
    return "".join(parts)


def format_issues_table(
    file_issues: list[tuple[Path, list[MarkdownLinkBase]]],
    output_mode: Literal["ci", "local"] = "local",
) -> str:
    """
    Format all per-file issues into a complete markdown table.

    Args:
        file_issues: List of (file_path, issues) tuples.
        output_mode: "ci" omits file links; "local" includes clickable links.

    Returns:
        A markdown table string with header and all rows.
    """
    rows: list[str] = []
    for file_path, issues in file_issues:
        if output_mode == "ci":
            rows.append(f"| `{file_path}` |" + format_links(issues, output_mode))
        else:
            rows.append(f"| [`{file_path}`]({file_path}) |" + format_links(issues, output_mode))

    return "| File Full Path | Issues |\n|--------|--------|\n" + "".join(rows)
