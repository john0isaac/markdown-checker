import httpx

from markdown_checker.checks.base import BaseCheck
from markdown_checker.models import Config, MarkdownLinkBase
from markdown_checker.utils.extract_links import MarkdownLinks

# Domains where locale is required in the URL path; always skipped for locale checks.
_BUILTIN_SKIP_DOMAINS: list[str] = [
    "www.nvidia.com",
]


class URLsLocaleCheck(BaseCheck):
    """Check that URLs do not contain a country/language locale segment."""

    name = "check_urls_locale"
    link_type = "urls"

    def run(
        self,
        links: MarkdownLinks,
        config: Config | None = None,
        client: httpx.Client | None = None,
    ) -> list[MarkdownLinkBase]:
        config = config or Config()
        effective_skip = [*config.skip_domains, *_BUILTIN_SKIP_DOMAINS]
        skip_urls_containing = config.skip_urls_containing

        detected_issues: list[MarkdownLinkBase] = []
        for url in links.urls:
            hostname = url.host_name().lower()
            if any(hostname in domain.lower() for domain in effective_skip) or any(
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
    link_type = "paths"

    def run(
        self,
        links: MarkdownLinks,
        config: Config | None = None,
        client: httpx.Client | None = None,
    ) -> list[MarkdownLinkBase]:
        detected_issues: list[MarkdownLinkBase] = []
        for path in links.paths:
            if path.has_locale():
                path.issue = "has locale"
                detected_issues.append(path)
        return detected_issues
