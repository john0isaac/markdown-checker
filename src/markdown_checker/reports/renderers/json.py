"""
Renders a `Report` as machine-readable JSON.
"""

import json

from markdown_checker.reports.base import ReportRenderer
from markdown_checker.reports.model import Report
from markdown_checker.reports.model import ReportFormat


class JsonRenderer(ReportRenderer):
    """Renders a `Report` as a JSON document, including both errors and warnings."""

    format_name: ReportFormat = "json"
    file_extension = ".json"

    def __init__(self, indent: int = 2) -> None:
        self.indent = indent

    def render(self, report: Report) -> str:
        """Render the report (errors and warnings) as a JSON string."""
        data = {
            "tool": {"name": report.context.tool_name, "version": report.context.tool_version},
            "check": report.context.check_name,
            "summary": {
                "files_checked": report.files_checked,
                "links_checked": report.links_checked,
                "errors": report.error_count,
                "warnings": report.warning_count,
            },
            "files": [
                {
                    "path": file_report.file_path.as_posix(),
                    "issues": [
                        {
                            "link": issue.link,
                            "line": issue.line_number,
                            "level": issue.level,
                            "message": issue.message,
                        }
                        for issue in (*file_report.errors, *file_report.warnings)
                    ],
                }
                for file_report in report.files
            ],
        }
        return json.dumps(data, indent=self.indent) + "\n"
