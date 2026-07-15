from pathlib import Path

import pytest

from markdown_checker.reports.model import FileReport
from markdown_checker.reports.model import Report
from markdown_checker.reports.model import ReportContext
from markdown_checker.reports.model import ReportIssue


@pytest.fixture
def sample_report():
    """A Report with one file that has both an error and a warning."""
    file_report = FileReport(
        file_path=Path("docs/usage.rst"),
        errors=(
            ReportIssue(
                link="https://broken.example.com",
                line_number=42,
                file_path=Path("docs/usage.rst"),
                message="is broken",
                level="error",
            ),
        ),
        warnings=(
            ReportIssue(
                link="https://warn.example.com",
                line_number=7,
                file_path=Path("docs/usage.rst"),
                message="was rate limited",
                level="warning",
            ),
        ),
    )
    context = ReportContext(check_name="check_broken_urls", tool_version="1.2.2")
    return Report(context=context, files=(file_report,), links_checked=2, files_checked=1)
