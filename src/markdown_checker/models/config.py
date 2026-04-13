from dataclasses import dataclass, field
from typing import Literal

import httpx

DEFAULT_HEADERS: dict[str, str] = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
}


def create_http_client(headers: dict[str, str] | None = None) -> httpx.Client:
    """Create a pre-configured httpx.Client for URL checking."""
    return httpx.Client(
        follow_redirects=True,
        max_redirects=10,
        headers=headers or DEFAULT_HEADERS,
    )


@dataclass(frozen=True)
class Config:
    """Holds all runtime configuration for a check run."""

    skip_domains: list[str] = field(default_factory=list)
    skip_urls_containing: list[str] = field(default_factory=list)
    tracking_domains: list[str] = field(default_factory=list)
    timeout: int = 20
    retries: int = 3
    output_mode: Literal["ci", "local"] = "local"
