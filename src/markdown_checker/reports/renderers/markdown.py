"""
Renders a `Report` as a Markdown document with an HTML issues table.

This mirrors the original `MarkdownGenerator` output exactly: a per-check
header template, an optional contributing-guide line, then a table of
error-level issues only (warnings are not included in the Markdown report).
"""

import pathlib
from pathlib import Path

from markdown_checker.reports.base import ReportRenderer
from markdown_checker.reports.model import FileReport
from markdown_checker.reports.model import Report
from markdown_checker.reports.model import ReportContext
from markdown_checker.reports.model import ReportFormat
from markdown_checker.reports.model import ReportIssue

_TEMPLATES_DIR = pathlib.Path(__file__).resolve().parent.parent / "templates"

_TEMPLATE_PATHS: dict[str, str] = {
    "check_broken_paths": "paths/broken.md",
    "check_broken_urls": "urls/broken.md",
    "check_paths_tracking": "paths/tracking.md",
    "check_urls_tracking": "urls/tracking.md",
    "check_urls_locale": "urls/locale.md",
}


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


def _link_cell(link: str) -> str:
    """Render a link as a clickable Markdown link when it's a URL, plain code otherwise."""
    if link.startswith(("http://", "https://")):
        return f"[`{link}`]({link})"
    return f"`{link}`"


class MarkdownRenderer(ReportRenderer):
    """Renders a `Report` as Markdown, matching the historical `comment.md` output."""

    format_name: ReportFormat = "markdown"
    file_extension = ".md"

    def __init__(self) -> None:
        self.templates: dict[str, str] = {}

    def _template(self, check_name: str) -> str:
        """Lazily load and cache the header template for a check name."""
        if check_name not in _TEMPLATE_PATHS:
            raise ValueError("Invalid function name")
        if check_name not in self.templates:
            path = _TEMPLATES_DIR / _TEMPLATE_PATHS[check_name]
            self.templates[check_name] = path.read_text(encoding="utf-8")
        return self.templates[check_name]

    def _file_link(self, file_path: Path, context: ReportContext) -> str | None:
        if context.output_mode == "ci":
            return _repo_file_link(context.repo_url, file_path) if context.repo_url else None
        return str(file_path)

    def _format_issue_rows(self, issues: tuple[ReportIssue, ...], context: ReportContext) -> str:
        parts: list[str] = ["<table><thead><tr><th>#</th><th>Link</th><th>Line Number</th></tr></thead><tbody>"]
        for i, issue in enumerate(issues, 1):
            file_link = self._file_link(issue.file_path, context)
            link_cell = _link_cell(issue.link)
            if file_link is None:
                parts.append(f"<tr><td>{i}</td><td>{link_cell}</td><td>`{issue.line_number}`</td></tr>")
            else:
                parts.append(
                    f"<tr><td>{i}</td><td>{link_cell}</td>"
                    f"<td>[`{issue.line_number}`]({file_link}#L{issue.line_number})</td></tr>"
                )
        parts.append("</tbody></table>|\n")
        return "".join(parts)

    def _format_issues_table(self, files: tuple[FileReport, ...], context: ReportContext) -> str:
        rows: list[str] = []
        for file_report in files:
            if not file_report.errors:
                continue
            file_link = self._file_link(file_report.file_path, context)
            issue_rows = self._format_issue_rows(file_report.errors, context)
            if file_link is None:
                rows.append(f"| `{file_report.file_path}` |" + issue_rows)
            else:
                rows.append(f"| [`{file_report.file_path}`]({file_link}) |" + issue_rows)
        return "| File Full Path | Issues |\n|--------|--------|\n" + "".join(rows)

    def render(self, report: Report) -> str:
        """Render the report's error-level issues as a Markdown document."""
        header = self._template(report.context.check_name)
        guide_line = (
            f" For more details, check our [Contributing Guide]({report.context.guide_url}).\n\n"
            if report.context.guide_url
            else "\n\n"
        )
        table = self._format_issues_table(report.files, report.context)
        return header + guide_line + table
