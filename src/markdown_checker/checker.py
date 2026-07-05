"""Runs a named check (from the checks registry) across a set of files and
aggregates the results into a single :class:`CheckResult`.
"""

from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

from markdown_checker.checks import REGISTRY
from markdown_checker.models import Config
from markdown_checker.models import MarkdownLinkBase
from markdown_checker.utils import get_links_from_md_file
from markdown_checker.utils.url_pipeline import URLCheckService

_MIN_FILE_WINDOW = 4
"""Bounds on how many files may have their check submitted (but not yet collected) at
once. The window drains early once enough links are in flight to keep every worker
fed (target ~2x max_workers), so link-dense files don't balloon memory; it never
drains before _MIN_FILE_WINDOW files, so link-sparse files (few links per file) still
get real cross-file overlap; _MAX_FILE_WINDOW is an absolute cap regardless of
link density."""
_MAX_FILE_WINDOW = 64
"""Bounds on how many files may have their check submitted (but not yet collected) at
once. The window drains early once enough links are in flight to keep every worker
fed (target ~2x max_workers), so link-dense files don't balloon memory; it never
drains before _MIN_FILE_WINDOW files, so link-sparse files (few links per file) still
get real cross-file overlap; _MAX_FILE_WINDOW is an absolute cap regardless of
link density."""


@dataclass
class CheckResult:
    """Result of running a check on one or more files."""

    issues: list[tuple[Path, list[MarkdownLinkBase]]] = field(default_factory=list)
    links_checked: int = 0


def detect_issues(
    func: str,
    file_path: Path,
    config: Config,
    service: URLCheckService | None = None,
) -> tuple[list[MarkdownLinkBase], int]:
    """
    Detect issues in a single markdown file using the named check.

    Args:
        func (str): Name of the check to run (must be a key in REGISTRY).
        file_path (Path): Path to the markdown file to check.
        config (Config): Runtime configuration for the check.
        service: Optional shared URL-checking pipeline, reused across files
            in a run so duplicate URLs are only checked once.

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

    detected_issues = check.run(links=all_links, config=config, service=service)

    links_count = len(all_links.paths) if check.link_type == "paths" else len(all_links.urls)
    return detected_issues, links_count


def run_check_on_files(
    func: str,
    files_paths: list[Path],
    config: Config,
    progress_callback: Callable[[], None],
) -> CheckResult:
    """
    Run a named check across multiple files.

    Files are processed through an adaptive window: a file's check is submitted
    (but not necessarily collected) as soon as it's reached, so link extraction
    for upcoming files overlaps with the network wait of files already submitted.
    The window drains early once roughly ``2 * config.max_workers`` links are in
    flight - enough to keep every worker fed without link-dense files ballooning
    memory - but never before ``_MIN_FILE_WINDOW`` files, so link-sparse files
    still get real overlap; ``_MAX_FILE_WINDOW`` is an absolute cap either way.
    ``progress_callback`` fires as each file is submitted rather than once its
    results are collected, so the bar advances smoothly instead of lagging
    behind in bursts.

    Args:
        func: Name of the check to run (must be a key in REGISTRY).
        files_paths: List of markdown file paths to check.
        config: Runtime configuration for the check.
        progress_callback: Callback invoked once each file has been submitted.

    Returns:
        A CheckResult with per-file issues and total links checked.
    """
    check = REGISTRY.get(func)
    if check is None:
        raise ValueError(f"Unknown check function: {func!r}. Available: {list(REGISTRY)}")

    result = CheckResult()
    # Shared across all files so duplicate URLs are checked once, requests to the
    # same host are paced, and a rate limit pauses that host instead of retrying
    # it file-by-file.
    service = URLCheckService(config) if check.link_type == "urls" else None
    window: deque[tuple[Path, object, int]] = deque()
    window_links = 0
    target_links_in_flight = max(config.max_workers * 2, 1)

    def drain_one() -> int:
        """Collect the oldest submitted file and return its link count."""
        file_path, pending, links_count = window.popleft()
        detected_issues = check.collect(pending)
        result.links_checked += links_count
        if detected_issues:
            result.issues.append((file_path, detected_issues))
        return links_count

    def window_full() -> bool:
        if len(window) >= _MAX_FILE_WINDOW:
            return True
        return len(window) >= _MIN_FILE_WINDOW and window_links >= target_links_in_flight

    try:
        for file_path in files_paths:
            all_links = get_links_from_md_file(file_path)
            if not all_links.paths and not all_links.urls:
                progress_callback()
                continue

            pending = check.submit(links=all_links, config=config, service=service)
            links_count = len(all_links.paths) if check.link_type == "paths" else len(all_links.urls)
            window.append((file_path, pending, links_count))
            window_links += links_count
            progress_callback()
            if window_full():
                window_links -= drain_one()

        while window:
            drain_one()
    finally:
        if service is not None:
            service.close()

    return result
