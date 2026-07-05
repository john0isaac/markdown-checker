"""Format-agnostic report model, renderers, and the writer that emits them.

See :mod:`markdown_checker.reports.model` for the ``build_report()``
entry point that converts checker output into a :class:`Report
<markdown_checker.reports.model.Report>`.
"""

from markdown_checker.reports.base import ReportRenderer
from markdown_checker.reports.model import build_report
from markdown_checker.reports.model import FileReport
from markdown_checker.reports.model import Report
from markdown_checker.reports.model import ReportContext
from markdown_checker.reports.model import ReportFormat
from markdown_checker.reports.model import ReportIssue
from markdown_checker.reports.registry import get_renderer
from markdown_checker.reports.registry import RENDERERS
from markdown_checker.reports.renderers.annotations import GitHubAnnotationsRenderer
from markdown_checker.reports.renderers.console import ConsoleRenderer
from markdown_checker.reports.renderers.json import JsonRenderer
from markdown_checker.reports.renderers.markdown import MarkdownRenderer
from markdown_checker.reports.writer import write_report

__all__ = [
    "RENDERERS",
    "ConsoleRenderer",
    "FileReport",
    "GitHubAnnotationsRenderer",
    "JsonRenderer",
    "MarkdownRenderer",
    "Report",
    "ReportContext",
    "ReportFormat",
    "ReportIssue",
    "ReportRenderer",
    "build_report",
    "get_renderer",
    "write_report",
]
