"""
markdown-checker — a markdown link validation reporting tool.
"""

__version__ = "1.0.0"

from markdown_checker.cli import main, main_with_spinner
from markdown_checker.models import Config, MarkdownLinkBase, MarkdownPath, MarkdownURL

__all__ = ["Config", "main", "main_with_spinner", "MarkdownLinkBase", "MarkdownPath", "MarkdownURL", "__version__"]
