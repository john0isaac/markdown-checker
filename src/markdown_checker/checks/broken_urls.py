import concurrent.futures
from functools import partial

import httpx

from markdown_checker.checks.base import BaseCheck
from markdown_checker.models import Config, MarkdownLinkBase, MarkdownURL
from markdown_checker.utils.extract_links import MarkdownLinks

# Domains known to block automated requests; always skipped for URL checks.
_BUILTIN_SKIP_DOMAINS: list[str] = []


def _check_url(
    url: MarkdownURL,
    skip_domains: list[str],
    skip_urls_containing: list[str],
    timeout: int,
    retries: int,
    client: httpx.Client,
) -> MarkdownURL | None:
    """Thread worker: checks a single URL using the shared httpx.Client."""
    hostname = url.host_name().lower()
    if any(hostname in domain.lower() for domain in skip_domains) or any(
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

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        }
        worker = partial(
            _check_url,
            skip_domains=effective_skip,
            skip_urls_containing=skip_urls_containing,
            timeout=config.timeout,
            retries=config.retries,
        )
        owns_client = client is None
        if owns_client:
            client = httpx.Client(follow_redirects=True, max_redirects=10, headers=headers)
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = {executor.submit(worker, url, client=client): url for url in links.urls}
                results: list[MarkdownLinkBase] = []
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    if result is not None:
                        results.append(result)
        finally:
            if owns_client and client is not None:
                client.close()
        return results
