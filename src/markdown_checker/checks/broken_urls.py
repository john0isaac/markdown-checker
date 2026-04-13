import concurrent.futures
from functools import partial

from markdown_checker.checks.base import BaseCheck
from markdown_checker.models import Config, MarkdownLinkBase, MarkdownURL
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
) -> MarkdownURL | None:
    """Thread worker: checks a single URL with its own httpx client."""
    hostname = url.host_name().lower()
    if any(domain.lower() in hostname for domain in skip_domains) or any(
        substring in url.link for substring in skip_urls_containing
    ):
        return None
    # Each worker creates its own client via is_alive(client=None).
    if not url.is_alive(timeout=timeout, retries=retries):
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
    ) -> list[MarkdownLinkBase]:
        config = config or Config()
        effective_skip = [*config.skip_domains, *_BUILTIN_SKIP_DOMAINS]
        skip_urls_containing = config.skip_urls_containing

        worker = partial(
            _check_url,
            skip_domains=effective_skip,
            skip_urls_containing=skip_urls_containing,
            timeout=config.timeout,
            retries=config.retries,
        )
        # NOTE: httpx.Client is NOT thread-safe. Do not share a single client
        # across ThreadPoolExecutor workers. Each worker creates its own
        # client via is_alive(client=None) to avoid RuntimeError crashes.
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(worker, url): url for url in links.urls}
            results: list[MarkdownLinkBase] = []
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result is not None:
                    results.append(result)
        return results
