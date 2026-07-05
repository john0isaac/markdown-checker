"""The ``check_broken_paths`` check: flags relative/root-relative paths that don't exist on disk."""

from markdown_checker.checks.base import BaseCheck
from markdown_checker.models import Config
from markdown_checker.models import MarkdownPath
from markdown_checker.utils.extract_links import MarkdownLinks
from markdown_checker.utils.url_pipeline import URLCheckService


class BrokenPathsCheck(BaseCheck[MarkdownPath]):
    """Check for relative paths in markdown files that do not exist on disk."""

    name = "check_broken_paths"
    link_type = "paths"

    def run(
        self,
        links: MarkdownLinks,
        config: Config | None = None,
        service: URLCheckService | None = None,
    ) -> list[MarkdownPath]:
        """Flag every path in ``links.paths`` whose target does not exist on
        disk (see :meth:`MarkdownPath.exists
        <markdown_checker.models.path.MarkdownPath.exists>`), setting
        ``issue="is broken"`` (error-level) on each. ``config`` and
        ``service`` are unused: this check does no network I/O.
        """
        detected_issues: list[MarkdownPath] = []
        for path in links.paths:
            if not path.exists():
                path.issue = "is broken"
                detected_issues.append(path)
        return detected_issues
