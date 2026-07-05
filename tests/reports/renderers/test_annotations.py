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
