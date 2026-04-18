from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from markdown_checker.checks import REGISTRY
from markdown_checker.models import Config, MarkdownLinkBase
from markdown_checker.utils import get_links_from_md_file


@dataclass
class CheckResult:
    """Result of running a check on one or more files."""

    issues: list[tuple[Path, list[MarkdownLinkBase]]] = field(default_factory=list)
    links_checked: int = 0


def detect_issues(
    func: str,
    file_path: Path,
    config: Config,
) -> tuple[list[MarkdownLinkBase], int]:
    """
    Detect issues in a single markdown file using the named check.

    Args:
        func (str): Name of the check to run (must be a key in REGISTRY).
        file_path (Path): Path to the markdown file to check.
        config (Config): Runtime configuration for the check.

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

    detected_issues = check.run(links=all_links, config=config)

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

    Args:
        func: Name of the check to run (must be a key in REGISTRY).
        files_paths: List of markdown file paths to check.
        config: Runtime configuration for the check.
        progress_callback: Callback invoked after each file is checked.

    Returns:
        A CheckResult with per-file issues and total links checked.
    """
    check = REGISTRY.get(func)
    if check is None:
        raise ValueError(f"Unknown check function: {func!r}. Available: {list(REGISTRY)}")

    result = CheckResult()

    for file_path in files_paths:
        detected_issues, links_count = detect_issues(func=func, file_path=file_path, config=config)
        result.links_checked += links_count
        if detected_issues:
            result.issues.append((file_path, detected_issues))
        progress_callback()

    return result
