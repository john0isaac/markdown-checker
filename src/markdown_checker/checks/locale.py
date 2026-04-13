from markdown_checker.checks.base import BaseCheck
from markdown_checker.models.base import MarkdownLinkBase
from markdown_checker.utils.extract_links import MarkdownLinks

# Domains where locale is required in the URL path; always skipped for locale checks.
_BUILTIN_SKIP_DOMAINS: list[str] = [
    "www.nvidia.com",
]


class URLsLocaleCheck(BaseCheck):
    """Check that URLs do not contain a country/language locale segment."""

    name = "check_urls_locale"

    def run(
        self,
        links: MarkdownLinks,
        skip_domains: list[str] | None = None,
        skip_urls_containing: list[str] | None = None,
        tracking_domains: list[str] | None = None,
        timeout: int = 15,
        retries: int = 3,
    ) -> list[MarkdownLinkBase]:
        effective_skip = [*(skip_domains or []), *_BUILTIN_SKIP_DOMAINS]
        skip_urls_containing = skip_urls_containing or []

        detected_issues: list[MarkdownLinkBase] = []
        for url in links.urls:
            if any(url.host_name().lower() in domain.lower() for domain in effective_skip) or any(
                substring in url.link for substring in skip_urls_containing
            ):
                continue
            if url.has_locale():
                url.issue = "has locale"
                detected_issues.append(url)
        return detected_issues


class PathsLocaleCheck(BaseCheck):
    """Check that relative paths do not contain a country/language locale segment."""

    name = "check_paths_locale"

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
            if path.has_locale():
                path.issue = "has locale"
                detected_issues.append(path)
        return detected_issues
