from markdown_checker.checks.base import BaseCheck
from markdown_checker.models import Config, MarkdownLinkBase
from markdown_checker.utils.extract_links import MarkdownLinks


class BrokenPathsCheck(BaseCheck):
    """Check for relative paths in markdown files that do not exist on disk."""

    name = "check_broken_paths"
    link_type = "paths"

    def run(
        self,
        links: MarkdownLinks,
        config: Config | None = None,
    ) -> list[MarkdownLinkBase]:
        detected_issues: list[MarkdownLinkBase] = []
        for path in links.paths:
            if not path.exists():
                path.issue = "is broken"
                detected_issues.append(path)
        return detected_issues
