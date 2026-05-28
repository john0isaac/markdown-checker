import concurrent.futures
from functools import partial

from markdown_checker.checks.base import BaseCheck
from markdown_checker.models import Config
from markdown_checker.models import MarkdownURL
from markdown_checker.utils.extract_links import MarkdownLinks

# Domains known to block automated requests (e.g. Cloudflare 403);
# always skipped for URL checks.
_BUILTIN_SKIP_DOMAINS: list[str] = [
    "openai.com",
]


def _check_url(
    url: MarkdownURL,
    skip_domains: list[str],
    skip_urls_containing: list[str],
    timeout: int,
    retries: int,
    retry_on_429: bool,
    fallback_retry_delay: int,
) -> MarkdownURL | None:
    """Thread worker: checks a single URL with its own httpx2 client."""
    hostname = url.host_name().lower()
    if any(domain in hostname for domain in skip_domains) or any(
        substring in url.link for substring in skip_urls_containing
    ):
        return None
    # Each worker creates its own client via check(client=None).
    result = url.check(
        timeout=timeout,
        retries=retries,
        retry_on_429=retry_on_429,
        fallback_retry_delay=fallback_retry_delay,
    )
    if result.status == "alive":
        return None
    if result.status == "broken":
        url.issue = "is broken"
        url.issue_level = "error"
        return url
    if result.status == "rate_limited":
        url.issue = "was skipped due to rate limiting"
    else:
        # transient_error
        url.issue = "could not be reached due to a network error"
    url.issue_level = "warning"
    return url


class BrokenURLsCheck(BaseCheck[MarkdownURL]):
    """Check for URLs in markdown files that return non-2xx responses."""

    name = "check_broken_urls"
    link_type = "urls"

    def run(
        self,
        links: MarkdownLinks,
        config: Config | None = None,
    ) -> list[MarkdownURL]:
        config = config or Config()
        effective_skip = [domain.lower() for domain in [*config.skip_domains, *_BUILTIN_SKIP_DOMAINS]]
        skip_urls_containing = config.skip_urls_containing

        worker = partial(
            _check_url,
            skip_domains=effective_skip,
            skip_urls_containing=skip_urls_containing,
            timeout=config.timeout,
            retries=config.retries,
            retry_on_429=config.retry_on_429,
            fallback_retry_delay=config.fallback_retry_delay,
        )
        # NOTE: httpx2.Client is NOT thread-safe. Do not share a single client
        # across ThreadPoolExecutor workers. Each worker creates its own
        # client via check(client=None) to avoid RuntimeError crashes.
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results: list[MarkdownURL] = [
                outcome for outcome in executor.map(worker, links.urls) if outcome is not None
            ]
        return results
