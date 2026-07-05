from pathlib import Path

import pytest

from markdown_checker.reports.model import FileReport
from markdown_checker.reports.model import Report
from markdown_checker.reports.model import ReportContext
from markdown_checker.reports.model import ReportIssue
from markdown_checker.reports.renderers.markdown import MarkdownRenderer


def _errors_file_report(file_path: Path, errors: tuple[ReportIssue, ...]) -> FileReport:
    return FileReport(file_path=file_path, errors=errors)


@pytest.fixture
def two_errors():
    file_path = Path("file.md")
    return (
        ReportIssue(
            link="https://example.com/broken", line_number=10, file_path=file_path, message="is broken", level="error"
        ),
        ReportIssue(
            link="https://example.com/also-broken",
            line_number=20,
            file_path=file_path,
            message="is broken",
            level="error",
        ),
    )


@pytest.mark.parametrize(
    "check_name",
    [
        "check_broken_paths",
        "check_broken_urls",
        "check_paths_tracking",
        "check_urls_tracking",
        "check_urls_locale",
    ],
)
def test_markdown_renderer_loads_template_per_check(check_name, sample_report):
    """MarkdownRenderer prepends the header template for the given check name."""
    context = ReportContext(check_name=check_name)
    report = Report(context=context, files=sample_report.files)
    renderer = MarkdownRenderer()
    result = renderer.render(report)
    assert renderer.templates[check_name] in result


def test_markdown_renderer_invalid_check_name_raises():
    """MarkdownRenderer raises ValueError for unknown check names."""
    context = ReportContext(check_name="nonexistent_check")
    report = Report(context=context, files=())
    with pytest.raises(ValueError, match="Invalid function name"):
        MarkdownRenderer().render(report)


def test_markdown_renderer_includes_contributing_guide_url(sample_report):
    """Contributing guide URL is included when set on the context."""
    context = ReportContext(check_name="check_broken_urls", guide_url="https://example.com/CONTRIBUTING.md")
    report = Report(context=context, files=sample_report.files)
    result = MarkdownRenderer().render(report)
    assert "https://example.com/CONTRIBUTING.md" in result


def test_markdown_renderer_only_includes_errors(sample_report):
    """MarkdownRenderer's table includes error links but not warning links."""
    result = MarkdownRenderer().render(sample_report)
    assert "https://broken.example.com" in result
    assert "https://warn.example.com" not in result


def test_markdown_renderer_templates_lazy_loaded():
    """Templates are lazy-loaded: empty at init, populated after render."""
    renderer = MarkdownRenderer()
    assert renderer.templates == {}
    context = ReportContext(check_name="check_broken_paths")
    renderer.render(Report(context=context, files=()))
    assert "check_broken_paths" in renderer.templates


def test_issue_rows_html_table_structure(two_errors):
    """The rendered table includes the expected HTML scaffolding."""
    context = ReportContext(check_name="check_broken_urls")
    result = MarkdownRenderer()._format_issue_rows(two_errors, context)
    assert "<table>" in result
    assert "</table>" in result
    assert "<thead>" in result
    assert "<tbody>" in result


def test_issue_rows_contains_all_links(two_errors):
    """Includes every issue's link in the output."""
    context = ReportContext(check_name="check_broken_urls")
    result = MarkdownRenderer()._format_issue_rows(two_errors, context)
    for issue in two_errors:
        assert issue.link in result


def test_issue_rows_numbering(two_errors):
    """Numbers issues sequentially starting from 1."""
    context = ReportContext(check_name="check_broken_urls")
    result = MarkdownRenderer()._format_issue_rows(two_errors, context)
    assert "<td>1</td>" in result
    assert "<td>2</td>" in result


def test_issue_rows_ends_with_pipe_newline(two_errors):
    """Output ends with the table closing pipe and newline."""
    context = ReportContext(check_name="check_broken_urls")
    result = MarkdownRenderer()._format_issue_rows(two_errors, context)
    assert result.endswith("|\n")


def test_issue_rows_local_mode_has_file_links(two_errors):
    """In non-CI mode, line numbers are rendered as file links."""
    context = ReportContext(check_name="check_broken_urls", output_mode="local")
    result = MarkdownRenderer()._format_issue_rows(two_errors, context)
    assert "file.md#L10" in result


def test_issue_rows_ci_mode_no_repo_url(two_errors):
    """In CI mode without a repo_url, line numbers are plain text without file links."""
    context = ReportContext(check_name="check_broken_urls", output_mode="ci")
    result = MarkdownRenderer()._format_issue_rows(two_errors, context)
    assert "file.md#L" not in result


def test_issue_rows_ci_mode_with_repo_url_has_clickable_links(two_errors):
    """In CI mode with a repo_url, line numbers are rendered as clickable repo links."""
    context = ReportContext(
        check_name="check_broken_urls", output_mode="ci", repo_url="https://github.com/owner/repo/blob/sha"
    )
    result = MarkdownRenderer()._format_issue_rows(two_errors, context)
    assert "[`10`](https://github.com/owner/repo/blob/sha/file.md#L10)" in result
    assert "[`20`](https://github.com/owner/repo/blob/sha/file.md#L20)" in result


def test_issue_rows_empty_list():
    """Returns a valid table structure even with an empty tuple of issues."""
    context = ReportContext(check_name="check_broken_urls")
    result = MarkdownRenderer()._format_issue_rows((), context)
    assert "<table>" in result
    assert "</table>" in result


def test_issue_rows_url_link_is_clickable(two_errors):
    """URL links are rendered as clickable Markdown links, not plain code."""
    context = ReportContext(check_name="check_broken_urls")
    result = MarkdownRenderer()._format_issue_rows(two_errors, context)
    assert "[`https://example.com/broken`](https://example.com/broken)" in result


def test_issue_rows_non_url_link_stays_as_code():
    """Non-URL links (e.g. relative paths) are rendered as plain code, not links."""
    file_path = Path("file.md")
    issue = ReportIssue(link="./missing.md", line_number=1, file_path=file_path, message="is broken", level="error")
    context = ReportContext(check_name="check_broken_paths")
    result = MarkdownRenderer()._format_issue_rows((issue,), context)
    assert "<td>`./missing.md`</td>" in result
    assert "[`./missing.md`]" not in result


def test_issues_table_local_mode_has_file_links(two_errors):
    """In non-CI mode, file paths are rendered as clickable links."""
    context = ReportContext(check_name="check_broken_urls", output_mode="local")
    files = (_errors_file_report(Path("file.md"), two_errors),)
    result = MarkdownRenderer()._format_issues_table(files, context)
    assert "[`file.md`](file.md)" in result


def test_issues_table_ci_mode_no_repo_url(two_errors):
    """In CI mode without a repo_url, file paths are plain text without links."""
    context = ReportContext(check_name="check_broken_urls", output_mode="ci")
    files = (_errors_file_report(Path("file.md"), two_errors),)
    result = MarkdownRenderer()._format_issues_table(files, context)
    assert "[`file.md`]" not in result
    assert "`file.md`" in result


def test_issues_table_ci_mode_with_repo_url_has_clickable_links(two_errors):
    """In CI mode with a repo_url, file paths are rendered as clickable repo links."""
    context = ReportContext(
        check_name="check_broken_urls", output_mode="ci", repo_url="https://github.com/owner/repo/blob/sha"
    )
    files = (_errors_file_report(Path("file.md"), two_errors),)
    result = MarkdownRenderer()._format_issues_table(files, context)
    assert "[`file.md`](https://github.com/owner/repo/blob/sha/file.md)" in result


def test_issues_table_skips_files_without_errors(two_errors):
    """Files with only warnings (no errors) are omitted from the table."""
    context = ReportContext(check_name="check_broken_urls")
    warning_only = FileReport(
        file_path=Path("warn.md"),
        warnings=(
            ReportIssue(
                link="https://warn.example.com",
                line_number=1,
                file_path=Path("warn.md"),
                message="msg",
                level="warning",
            ),
        ),
    )
    result = MarkdownRenderer()._format_issues_table((warning_only,), context)
    assert "warn.md" not in result
