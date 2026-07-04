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
        detected_issues: list[MarkdownPath] = []
        for path in links.paths:
            if not path.exists():
                path.issue = "is broken"
                detected_issues.append(path)
        return detected_issues
