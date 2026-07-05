"""
Renders a `Report` as plain, human-readable console text (local/non-CI mode).
"""

from markdown_checker.reports.base import ReportRenderer
from markdown_checker.reports.model import Level
from markdown_checker.reports.model import Report
from markdown_checker.reports.model import ReportFormat
from markdown_checker.reports.model import ReportIssue


def _console_line(issue: ReportIssue, resolved_path: object) -> str:
    return f"\tFile '{resolved_path}', line {issue.line_number}\n{issue.link} {issue.message}.\n"


class ConsoleRenderer(ReportRenderer):
    """Renders a `Report` as plain console text, one block per issue."""

    format_name: ReportFormat = "console"
    file_extension = ".txt"

    def render_lines(self, report: Report) -> list[tuple[str, Level]]:
        """Return (console_block, level) pairs, in file/issue order."""
        lines: list[tuple[str, Level]] = []
        for file_report in report.files:
            resolved_path = (
                file_report.file_path.resolve() if report.context.output_mode == "local" else file_report.file_path
            )
            for issue in (*file_report.errors, *file_report.warnings):
                lines.append((_console_line(issue, resolved_path), issue.level))
        return lines

    def render(self, report: Report) -> str:
        """Render every issue as a plain console text block."""
        return "\n".join(line for line, _ in self.render_lines(report))
