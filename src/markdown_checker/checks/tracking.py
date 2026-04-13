from markdown_checker.checks.base import BaseCheck
from markdown_checker.models import Config, MarkdownLinkBase
from markdown_checker.utils.extract_links import MarkdownLinks


class URLsTrackingCheck(BaseCheck):
    """Check that URLs on configured tracking domains include a tracking ID."""

    name = "check_urls_tracking"
    link_type = "urls"

    def run(
        self,
        links: MarkdownLinks,
        config: Config | None = None,
    ) -> list[MarkdownLinkBase]:
        config = config or Config()
        skip_domains = config.skip_domains
        skip_urls_containing = config.skip_urls_containing
        tracking_domains = config.tracking_domains

        detected_issues: list[MarkdownLinkBase] = []
        for url in links.urls:
            hostname = url.host_name().lower()
            if any(domain.lower() in hostname for domain in skip_domains) or any(
                substring in url.link for substring in skip_urls_containing
            ):
                continue
            if any(domain.lower() in hostname for domain in tracking_domains) and not url.has_tracking():
                url.issue = "is missing tracking id"
                detected_issues.append(url)
        return detected_issues


class PathsTrackingCheck(BaseCheck):
    """Check that relative paths include a tracking ID."""

    name = "check_paths_tracking"
    link_type = "paths"

    def run(
        self,
        links: MarkdownLinks,
        config: Config | None = None,
    ) -> list[MarkdownLinkBase]:
        detected_issues: list[MarkdownLinkBase] = []
        for path in links.paths:
            if not path.has_tracking():
                path.issue = "is missing tracking id"
                detected_issues.append(path)
        return detected_issues
