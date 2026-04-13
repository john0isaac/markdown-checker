import concurrent.futures
from functools import partial

import httpx

from markdown_checker.checks.base import BaseCheck
from markdown_checker.models.base import MarkdownLinkBase
from markdown_checker.models.url import MarkdownURL
from markdown_checker.utils.extract_links import MarkdownLinks

# Domains known to block automated requests; always skipped for URL checks.
_BUILTIN_SKIP_DOMAINS: list[str] = [
    "openai.com",
    "beta.openai.com",
    "help.openai.com",
    "platform.openai.com",
    "vscode.dev",
    "en.wikipedia.org",
    "www.midjourney.com",
    "www.linkedin.com",
    "rodtrent.substack.com",
    "github.com",
]


def _check_url(
    url: MarkdownURL,
    skip_domains: list[str],
    skip_urls_containing: list[str],
    timeout: int,
    retries: int,
    client: httpx.Client,
) -> MarkdownURL | None:
    """Thread worker: checks a single URL using the shared httpx.Client."""
    if any(url.host_name().lower() in domain.lower() for domain in skip_domains) or any(
        substring in url.link for substring in skip_urls_containing
    ):
        return None
    if not url.is_alive(timeout=timeout, retries=retries, client=client):
        url.issue = "is broken"
        return url
    return None


class BrokenURLsCheck(BaseCheck):
    """Check for URLs in markdown files that return non-2xx responses."""

    name = "check_broken_urls"

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

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        }
        worker = partial(
            _check_url,
            skip_domains=effective_skip,
            skip_urls_containing=skip_urls_containing,
            timeout=timeout,
            retries=retries,
        )
        with httpx.Client(follow_redirects=True, headers=headers) as client:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = list(executor.map(lambda url: worker(url, client=client), links.urls))
        return [r for r in results if r is not None]
