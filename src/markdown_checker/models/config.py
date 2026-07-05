from dataclasses import dataclass
from dataclasses import field
from typing import Literal

import httpx2

DEFAULT_HEADERS: dict[str, str] = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
}


def create_http_client(headers: dict[str, str] | None = None) -> httpx2.Client:
    """Create a pre-configured httpx2.Client for URL checking.

    Args:
        headers: Request headers to send. Defaults to :data:`DEFAULT_HEADERS`,
            which impersonate a desktop browser so servers that block
            non-browser user agents (e.g. some CDNs) don't reject the request.

    Returns:
        A client configured to follow redirects (up to 10 hops).
    """
    return httpx2.Client(
        follow_redirects=True,
        max_redirects=10,
        headers=headers or DEFAULT_HEADERS,
    )


@dataclass(frozen=True)
class Config:
    """Holds all runtime configuration for a check run."""

    skip_domains: list[str] = field(default_factory=list)
    """Hostnames to exclude from URL checks (substring match against the
    URL's hostname). Used by ``check_broken_urls`` and ``check_urls_locale``.
    """

    skip_urls_containing: list[str] = field(default_factory=list)
    """Substrings to exclude from URL checks (matched anywhere in the full
    URL). Used by the same checks as ``skip_domains``.
    """

    tracking_domains: list[str] = field(default_factory=list)
    """Hostnames that must carry a ``wt.mc_id`` tracking parameter. Only
    used by ``check_urls_tracking``; URLs on other hosts are ignored by
    that check.
    """

    timeout: int = 20
    """Per-request timeout in seconds for URL checks."""

    retries: int = 3
    """Number of attempts for a URL before it is reported as ``broken``.
    Does not apply to rate-limit/auth responses, which return immediately
    (see :meth:`MarkdownURL.check <markdown_checker.models.url.MarkdownURL.check>`).
    """

    retry_on_429: bool = True
    """When True, honour a ``Retry-After`` header (or a bare 429) instead of
    the exponential backoff normally used for hard failures.
    """

    fallback_retry_delay: int = 30
    """Seconds reported as ``retry_after`` when a 429 response carries no
    ``Retry-After`` header.
    """

    max_workers: int = 10
    """Maximum number of concurrent URL-check worker threads shared across
    the whole run.
    """

    per_host_delay: float = 0.5
    """Minimum delay in seconds enforced between two requests to the same host."""

    max_pending: int = 200
    """Maximum number of in-flight (submitted but not yet resolved) URL
    checks before new submissions block; bounds memory use on very large runs.
    """

    output_mode: Literal["ci", "local"] = "local"
    """``"ci"`` switches CLI output to GitHub Actions ``::error``/``::warning``
    annotations; ``"local"`` uses plain coloured console output.
    """
