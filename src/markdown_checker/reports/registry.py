"""
Registry mapping report format names to `ReportRenderer` implementations.
"""

from markdown_checker.reports.base import ReportRenderer
from markdown_checker.reports.model import ReportFormat
from markdown_checker.reports.renderers.annotations import GitHubAnnotationsRenderer
from markdown_checker.reports.renderers.console import ConsoleRenderer
from markdown_checker.reports.renderers.json import JsonRenderer
from markdown_checker.reports.renderers.markdown import MarkdownRenderer

RENDERERS: dict[ReportFormat, type[ReportRenderer]] = {
    MarkdownRenderer.format_name: MarkdownRenderer,
    JsonRenderer.format_name: JsonRenderer,
    GitHubAnnotationsRenderer.format_name: GitHubAnnotationsRenderer,
    ConsoleRenderer.format_name: ConsoleRenderer,
}
"""Maps the CLI ``--report-format`` argument value to the corresponding renderer class."""


def get_renderer(format_name: ReportFormat, **options: object) -> ReportRenderer:
    """
    Instantiate a renderer by name.

    Args:
        format_name: One of the keys in `RENDERERS`.
        **options: Constructor keyword arguments forwarded to the renderer class.

    Raises:
        ValueError: If `format_name` is not a registered renderer.
    """
    renderer_cls = RENDERERS.get(format_name)
    if renderer_cls is None:
        raise ValueError(f"Unknown report format: {format_name!r}. Available: {list(RENDERERS)}")
    return renderer_cls(**options)
