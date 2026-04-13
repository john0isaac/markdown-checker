from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class Config:
    """Holds all runtime configuration for a check run."""

    skip_domains: list[str] = field(default_factory=list)
    skip_urls_containing: list[str] = field(default_factory=list)
    tracking_domains: list[str] = field(default_factory=list)
    timeout: int = 20
    retries: int = 3
    output_mode: Literal["ci", "local"] = "local"
