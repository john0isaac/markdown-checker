from concurrent.futures import Future
from typing import cast

from markdown_checker.checks.base import BaseCheck
from markdown_checker.models import Config
from markdown_checker.models import MarkdownURL
from markdown_checker.models.url import URLCheckResult
from markdown_checker.utils.extract_links import MarkdownLinks
from markdown_checker.utils.url_pipeline import URLCheckService

# Domains known to block automated requests (e.g. Cloudflare 403);
# always skipped for URL checks.
_BUILTIN_SKIP_DOMAINS: list[str] = []

# Opaque token handed from submit() to collect(): the submitted jobs, plus the
# service to close afterwards if this check created a private one for itself.
_Pending = tuple[list[tuple[MarkdownURL, "Future[URLCheckResult]"]], URLCheckService | None]


def _to_issue(url: MarkdownURL, result: URLCheckResult) -> MarkdownURL | None:
    """Map a URLCheckResult onto a MarkdownURL's issue fields."""
    if result.status == "alive":
        return None
    if result.status == "broken":
        url.issue = "is broken"
        url.issue_level = "error"
        return url
    if result.status == "rate_limited":
        url.issue = "was skipped due to rate limiting"
    elif result.status == "unverifiable":
        url.issue = "could not be verified (access was forbidden by the server)"
    else:
        # transient_error
        url.issue = "could not be reached due to a network error"
    url.issue_level = "warning"
    return url


class BrokenURLsCheck(BaseCheck[MarkdownURL]):
    """Check for URLs in markdown files that return non-2xx responses."""

    name = "check_broken_urls"
    link_type = "urls"

    def submit(
        self,
        links: MarkdownLinks,
        config: Config | None = None,
        service: URLCheckService | None = None,
    ) -> object:
        config = config or Config()
        effective_skip = [domain.lower() for domain in [*config.skip_domains, *_BUILTIN_SKIP_DOMAINS]]
        skip_urls_containing = config.skip_urls_containing

        # Standalone fallback (direct calls, tests): own a private service for this run only.
        owns_service = service is None
        _service = service or URLCheckService(config)

        pending: list[tuple[MarkdownURL, Future[URLCheckResult]]] = []
        for url in links.urls:
            hostname = url.host_name().lower()
            if any(domain in hostname for domain in effective_skip) or any(
                substring in url.link for substring in skip_urls_containing
            ):
                continue
            pending.append((url, _service.submit(url)))
        return (pending, _service if owns_service else None)

    def collect(self, pending: object) -> list[MarkdownURL]:
        jobs, owned_service = cast(_Pending, pending)
        try:
            results: list[MarkdownURL] = []
            for url, future in jobs:
                issue = _to_issue(url, future.result())
                if issue is not None:
                    results.append(issue)
            return results
        finally:
            if owned_service is not None:
                owned_service.close()

    def run(
        self,
        links: MarkdownLinks,
        config: Config | None = None,
        service: URLCheckService | None = None,
    ) -> list[MarkdownURL]:
        return self.collect(self.submit(links, config=config, service=service))
