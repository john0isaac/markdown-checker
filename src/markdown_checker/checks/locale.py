from markdown_checker.checks.base import BaseCheck
from markdown_checker.models import Config
from markdown_checker.models import MarkdownURL
from markdown_checker.utils.extract_links import MarkdownLinks
from markdown_checker.utils.url_pipeline import URLCheckService

# Domains where locale is required in the URL path; always skipped for locale checks.
_BUILTIN_SKIP_DOMAINS: list[str] = [
    "www.nvidia.com",
]


class URLsLocaleCheck(BaseCheck[MarkdownURL]):
    """Check that URLs do not contain a country/language locale segment."""

    name = "check_urls_locale"
    link_type = "urls"

    def run(
        self,
        links: MarkdownLinks,
        config: Config | None = None,
        service: URLCheckService | None = None,
    ) -> list[MarkdownURL]:
        config = config or Config()
        effective_skip = [*config.skip_domains, *_BUILTIN_SKIP_DOMAINS]
        skip_urls_containing = config.skip_urls_containing

        detected_issues: list[MarkdownURL] = []
        for url in links.urls:
            hostname = url.host_name().lower()
            if any(domain.lower() in hostname for domain in effective_skip) or any(
                substring in url.link for substring in skip_urls_containing
            ):
                continue
            if url.has_locale():
                url.issue = "has locale"
                detected_issues.append(url)
        return detected_issues
