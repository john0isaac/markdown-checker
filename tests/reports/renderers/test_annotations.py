from pathlib import PureWindowsPath

from markdown_checker.reports.model import FileReport
from markdown_checker.reports.model import Report
from markdown_checker.reports.model import ReportContext
from markdown_checker.reports.model import ReportIssue
from markdown_checker.reports.renderers.annotations import GitHubAnnotationsRenderer


def test_github_annotations_renderer_formats_errors_and_warnings(sample_report):
    """GitHubAnnotationsRenderer emits one ::error/::warning line per issue."""
    result = GitHubAnnotationsRenderer().render(sample_report)
    assert "::error file=docs/usage.rst,line=42::" in result
    assert "::warning file=docs/usage.rst,line=7::" in result


def test_github_annotations_renderer_render_lines_levels(sample_report):
    """render_lines returns (text, level) pairs matching issue levels."""
    lines = GitHubAnnotationsRenderer().render_lines(sample_report)
    levels = {level for _, level in lines}
    assert levels == {"error", "warning"}


def test_github_annotations_renderer_windows_path_uses_forward_slashes():
    """A Windows-style file path is rendered with forward slashes in the `file=` annotation
    field, so GitHub can correctly link the annotation back to the file."""
    file_path = PureWindowsPath(r"content\6502_Assembly_Code\README.md")
    issue = ReportIssue(link="./missing.md", line_number=3, file_path=file_path, message="is broken", level="error")
    report = Report(
        context=ReportContext(check_name="check_broken_paths", output_mode="ci"),
        files=(FileReport(file_path=file_path, errors=(issue,)),),
    )
    result = GitHubAnnotationsRenderer().render(report)
    assert "file=content/6502_Assembly_Code/README.md,line=3" in result
    assert "\\" not in result
