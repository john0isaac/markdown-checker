from pathlib import Path

from markdown_checker.checks import REGISTRY
from markdown_checker.models.base import MarkdownLinkBase
from markdown_checker.utils.extract_links import get_links_from_md_file

# Checks that count paths (not URLs) toward the links_count total.
_PATH_CHECKS = {"check_broken_paths", "check_paths_tracking", "check_paths_locale"}


def detect_issues(
    func: str,
    file_path: Path,
    skip_urls_containing: list[str],
    skip_domains: list[str],
    tracking_domains: list[str],
    timeout: int,
    retries: int,
) -> tuple[list[MarkdownLinkBase], int]:
    """
    Detect issues in a single markdown file using the named check.

    Args:
        func (str): Name of the check to run (must be a key in REGISTRY).
        file_path (Path): Path to the markdown file to check.
        skip_urls_containing (list[str]): URL substrings to skip.
        skip_domains (list[str]): Domain names to skip.
        tracking_domains (list[str]): Domains that require tracking IDs.
        timeout (int): HTTP request timeout in seconds.
        retries (int): Number of HTTP request retries.

    Returns:
        A tuple of (detected_issues, links_checked_count).

    Raises:
        ValueError: If func is not a registered check name.
    """
    check = REGISTRY.get(func)
    if check is None:
        raise ValueError(f"Unknown check function: {func!r}. Available: {list(REGISTRY)}")

    all_links = get_links_from_md_file(file_path)
    if not all_links.paths and not all_links.urls:
        return [], 0

    detected_issues = check.run(
        links=all_links,
        skip_domains=skip_domains,
        skip_urls_containing=skip_urls_containing,
        tracking_domains=tracking_domains,
        timeout=timeout,
        retries=retries,
    )

    links_count = len(all_links.paths) if func in _PATH_CHECKS else len(all_links.urls)
    return detected_issues, links_count
