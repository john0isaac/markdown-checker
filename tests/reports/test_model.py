from pathlib import Path

import pytest

from markdown_checker.checker import CheckResult
from markdown_checker.models.url import MarkdownURL
from markdown_checker.reports.model import build_report
from markdown_checker.reports.model import ReportContext
from markdown_checker.reports.model import ReportIssue


def _check_result_with(*, errors=0, warnings=0, file_path=Path("sample.md")) -> CheckResult:
    issues = [
        MarkdownURL(link=f"https://example.com/{i}", line_number=i, file_path=file_path, issue="is broken")
        for i in range(errors)
    ] + [
        MarkdownURL(
            link=f"https://warn.example.com/{i}",
            line_number=100 + i,
            file_path=file_path,
            issue="was skipped",
            issue_level="warning",
        )
        for i in range(warnings)
    ]
    return CheckResult(issues=[(file_path, issues)] if issues else [], links_checked=errors + warnings)


def test_build_report_splits_errors_and_warnings():
    """build_report splits issues into errors/warnings per file."""
    check_result = _check_result_with(errors=2, warnings=1)
    context = ReportContext(check_name="check_broken_urls")
    report = build_report(check_result, context=context, files_checked=1)

    assert len(report.files) == 1
    assert len(report.files[0].errors) == 2
    assert len(report.files[0].warnings) == 1
    assert report.error_count == 2
    assert report.warning_count == 1
    assert report.has_errors is True
    assert report.has_warnings is True


def test_build_report_empty_check_result():
    """build_report with no issues produces an empty report."""
    context = ReportContext(check_name="check_broken_urls")
    report = build_report(CheckResult(), context=context, files_checked=3)

    assert report.files == ()
    assert report.error_count == 0
    assert report.has_errors is False
    assert report.files_checked == 3


def test_build_report_carries_links_checked():
    """build_report copies links_checked from the CheckResult."""
    check_result = _check_result_with(errors=1)
    context = ReportContext(check_name="check_broken_urls")
    report = build_report(check_result, context=context, files_checked=1)
    assert report.links_checked == check_result.links_checked


def test_report_model_is_frozen():
    """Report and its parts are immutable."""
    issue = ReportIssue(link="https://x", line_number=1, file_path=Path("a.md"), message="msg", level="error")
    with pytest.raises(AttributeError):
        issue.link = "https://y"


def test_report_error_and_warning_counts_default_to_zero():
    """A Report with no files has zero errors/warnings and no error/warning flags."""
    context = ReportContext(check_name="check_broken_urls")
    report = build_report(CheckResult(), context=context, files_checked=0)
    assert report.error_count == 0
    assert report.warning_count == 0
    assert report.has_errors is False
    assert report.has_warnings is False
