from markdown_checker.reports.renderers.console import ConsoleRenderer


def test_console_renderer_formats_errors_and_warnings(sample_report):
    """ConsoleRenderer includes both error and warning issue text."""
    result = ConsoleRenderer().render(sample_report)
    assert "https://broken.example.com is broken." in result
    assert "https://warn.example.com was rate limited." in result


def test_console_renderer_render_lines_levels(sample_report):
    """render_lines returns (text, level) pairs matching issue levels."""
    lines = ConsoleRenderer().render_lines(sample_report)
    levels = {level for _, level in lines}
    assert levels == {"error", "warning"}
