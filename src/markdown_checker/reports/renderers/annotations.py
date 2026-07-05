"""
Renders a `Report` as GitHub Actions workflow annotations
(`::error file=...,line=...::...`).
"""

from markdown_checker.reports.base import ReportRenderer
from markdown_checker.reports.model import Level
from markdown_checker.reports.model import Report
from markdown_checker.reports.model import ReportFormat
from markdown_checker.reports.model import ReportIssue


def _annotation_line(issue: ReportIssue) -> str:
    level = "warning" if issue.level == "warning" else "error"
    file_path = issue.file_path.as_posix()
    return (
        f"::{level} file={file_path},line={issue.line_number}::"
        f"File {file_path}, line {issue.line_number}, "
        f"Link {issue.link} {issue.message}."
    )


class GitHubAnnotationsRenderer(ReportRenderer):
    """Renders a `Report` as one GitHub Actions annotation per issue."""

    format_name: ReportFormat = "github-annotations"
    file_extension = ".txt"

    def render_lines(self, report: Report) -> list[tuple[str, Level]]:
        """Return (annotation_line, level) pairs, in file/issue order."""
        lines: list[tuple[str, Level]] = []
        for file_report in report.files:
            for issue in (*file_report.errors, *file_report.warnings):
                lines.append((_annotation_line(issue), issue.level))
        return lines

    def render(self, report: Report) -> str:
        """Render every issue as a GitHub Actions annotation line."""
        return "\n".join(line for line, _ in self.render_lines(report))
