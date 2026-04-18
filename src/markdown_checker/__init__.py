"""
markdown-checker — a markdown link validation reporting tool.
"""

__version__ = "1.0.1"

from markdown_checker.cli import main
from markdown_checker.models import Config, MarkdownLinkBase, MarkdownPath, MarkdownURL

__all__ = ["Config", "main", "MarkdownLinkBase", "MarkdownPath", "MarkdownURL", "__version__"]
