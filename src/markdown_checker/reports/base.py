"""
Renderer contract for turning a `Report` into a string.
"""

from abc import ABC
from abc import abstractmethod

from markdown_checker.reports.model import Report
from markdown_checker.reports.model import ReportFormat


class ReportRenderer(ABC):
    """Renders a `Report` into a string. Pure: no file or network I/O."""

    format_name: ReportFormat
    """Registry key and CLI value, e.g. "markdown", "json"""
    file_extension: str
    """Default file extension for this report format, including the dot, e.g. ".md", ".json"."""

    @abstractmethod
    def render(self, report: Report) -> str:
        """Return the complete report body as a string."""
        raise NotImplementedError
