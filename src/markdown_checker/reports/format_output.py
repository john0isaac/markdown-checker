"""
Module to format check results into markdown output.
"""

from pathlib import Path
from typing import Literal

from markdown_checker.models.base import MarkdownLinkBase


def _repo_file_link(repo_url: str, file_path: Path) -> str | None:
    """
    Build a clickable repository URL for a file, or return None if the path
    cannot be expressed relative to the repository root (assumed to be the
    current working directory in CI).
    """
    if file_path.is_absolute():
        try:
            file_path = file_path.relative_to(Path.cwd())
        except ValueError:
            return None
    return f"{repo_url}/{file_path.as_posix()}"


def format_links(
    links: list[MarkdownLinkBase],
    output_mode: Literal["ci", "local"] = "local",
    repo_url: str | None = None,
) -> str:
    """
    Formats a List of links into a string with numbered bullets.

    Args:
        links (list[MarkdownLinkBase]): The list of links to format.
        output_mode: "ci" omits file links unless repo_url is given; "local" includes clickable links.
        repo_url: Base blob URL (e.g. resolved from the GitHub Actions context) used to build
            clickable file links in "ci" mode. Ignored in "local" mode.

    Returns:
        formatted_links (str): The formatted string with numbered bullets.
    """
    parts: list[str] = ["<table><thead><tr><th>#</th><th>Link</th><th>Line Number</th></tr></thead><tbody>"]
    for i, item in enumerate(links, 1):
        if output_mode == "ci":
            file_link = _repo_file_link(repo_url, item.file_path) if repo_url else None
        else:
            file_link = str(item.file_path)
        if file_link is None:
            parts.append(f"<tr><td>{i}</td><td>`{item.link}`</td><td>`{item.line_number}`</td></tr>")
        else:
            parts.append(
                f"<tr><td>{i}</td><td>`{item.link}`</td>"
                f"<td>[`{item.line_number}`]({file_link}#L{item.line_number})</td></tr>"
            )

    parts.append("</tbody></table>|\n")
    return "".join(parts)


def format_issues_table(
    file_issues: list[tuple[Path, list[MarkdownLinkBase]]],
    output_mode: Literal["ci", "local"] = "local",
    repo_url: str | None = None,
) -> str:
    """
    Format all per-file issues into a complete markdown table.

    Args:
        file_issues: List of (file_path, issues) tuples.
        output_mode: "ci" omits file links unless repo_url is given; "local" includes clickable links.
        repo_url: Base blob URL (e.g. resolved from the GitHub Actions context) used to build
            clickable file links in "ci" mode. Ignored in "local" mode.

    Returns:
        A markdown table string with header and all rows.
    """
    rows: list[str] = []
    for file_path, issues in file_issues:
        if output_mode == "ci":
            file_link = _repo_file_link(repo_url, file_path) if repo_url else None
        else:
            file_link = str(file_path)
        if file_link is None:
            rows.append(f"| `{file_path}` |" + format_links(issues, output_mode, repo_url))
        else:
            rows.append(f"| [`{file_path}`]({file_link}) |" + format_links(issues, output_mode, repo_url))

    return "| File Full Path | Issues |\n|--------|--------|\n" + "".join(rows)
