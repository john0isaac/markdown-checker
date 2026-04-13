from markdown_checker.checks.base import BaseCheck
from markdown_checker.models.base import MarkdownLinkBase
from markdown_checker.utils.extract_links import MarkdownLinks


class URLsTrackingCheck(BaseCheck):
    """Check that URLs on configured tracking domains include a tracking ID."""

    name = "check_urls_tracking"

    def run(
        self,
        links: MarkdownLinks,
        skip_domains: list[str] | None = None,
        skip_urls_containing: list[str] | None = None,
        tracking_domains: list[str] | None = None,
        timeout: int = 15,
        retries: int = 3,
    ) -> list[MarkdownLinkBase]:
        skip_domains = skip_domains or []
        skip_urls_containing = skip_urls_containing or []
        tracking_domains = tracking_domains or []

        detected_issues: list[MarkdownLinkBase] = []
        for url in links.urls:
            if any(url.host_name().lower() in domain.lower() for domain in skip_domains) or any(
                substring in url.link for substring in skip_urls_containing
            ):
                continue
            if any(url.host_name().lower() in domain.lower() for domain in tracking_domains) and not url.has_tracking():
                url.issue = "is missing tracking id"
                detected_issues.append(url)
        return detected_issues


class PathsTrackingCheck(BaseCheck):
    """Check that relative paths include a tracking ID."""

    name = "check_paths_tracking"

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
            if not path.has_tracking():
                path.issue = "is missing tracking id"
                detected_issues.append(path)
        return detected_issues
