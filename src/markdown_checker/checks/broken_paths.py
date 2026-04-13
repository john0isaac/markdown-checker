from markdown_checker.checks.base import BaseCheck
from markdown_checker.models.base import MarkdownLinkBase
from markdown_checker.utils.extract_links import MarkdownLinks


class BrokenPathsCheck(BaseCheck):
    """Check for relative paths in markdown files that do not exist on disk."""

    name = "check_broken_paths"

    def run(
        self,
        links: MarkdownLinks,
        skip_domains: list[str] | None = None,
        skip_urls_containing: list[str] | None = None,
        tracking_domains: list[str] | None = None,
        timeout: int = 15,
        retries: int = 3,
    ) -> list[MarkdownLinkBase]:
        detected_issues: list[MarkdownLinkBase] = []
        for path in links.paths:
            if not path.exists():
                path.issue = "is broken"
                detected_issues.append(path)
        return detected_issues
