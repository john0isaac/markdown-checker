"""
markdown-checker — a markdown link validation reporting tool.
"""

__version__ = "1.0.3"

from markdown_checker.cli import main
from markdown_checker.models import Config
from markdown_checker.models import MarkdownLinkBase
from markdown_checker.models import MarkdownPath
from markdown_checker.models import MarkdownURL

__all__ = ["Config", "main", "MarkdownLinkBase", "MarkdownPath", "MarkdownURL", "__version__"]
