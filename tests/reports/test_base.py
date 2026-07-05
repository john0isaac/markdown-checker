import pytest

from markdown_checker.reports.base import ReportRenderer
from markdown_checker.reports.model import Report
from markdown_checker.reports.model import ReportContext


def test_report_renderer_cannot_be_instantiated_directly():
    """ReportRenderer is abstract and cannot be instantiated on its own."""
    with pytest.raises(TypeError):
        ReportRenderer()


def test_report_renderer_subclass_must_implement_render():
    """A subclass that doesn't implement render() cannot be instantiated."""

    class IncompleteRenderer(ReportRenderer):
        format_name = "incomplete"
        file_extension = ".txt"

    with pytest.raises(TypeError):
        IncompleteRenderer()


def test_report_renderer_concrete_subclass_works():
    """A concrete subclass implementing render() can be instantiated and used."""

    class EchoRenderer(ReportRenderer):
        format_name = "echo"
        file_extension = ".txt"

        def render(self, report: Report) -> str:
            return report.context.check_name

    context = ReportContext(check_name="check_broken_urls")
    renderer = EchoRenderer()
    assert renderer.render(Report(context=context, files=())) == "check_broken_urls"
