import concurrent.futures

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
) -> MarkdownURL | None:
    """Top-level helper so it can be pickled by ProcessPoolExecutor."""
    if any(url.host_name().lower() in domain.lower() for domain in skip_domains) or any(
        url.link in substring for substring in skip_urls_containing
    ):
        return None
    if not url.is_alive(timeout=timeout, retries=retries):
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

        with concurrent.futures.ProcessPoolExecutor() as executor:
            results = list(
                executor.map(
                    _check_url,
                    links.urls,
                    [effective_skip] * len(links.urls),
                    [skip_urls_containing] * len(links.urls),
                    [timeout] * len(links.urls),
                    [retries] * len(links.urls),
                )
            )
        return [r for r in results if r is not None]
