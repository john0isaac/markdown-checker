import threading
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from markdown_checker.checker import detect_issues
from markdown_checker.checker import run_check_on_files
from markdown_checker.models.config import Config
from markdown_checker.models.url import MarkdownURL
from markdown_checker.models.url import URLCheckResult


def test_detect_issues_unknown_func_raises():
    """Raises ValueError for unknown check function names."""
    with pytest.raises(ValueError, match="Unknown check function"):
        detect_issues(
            func="nonexistent",
            file_path=Path("test.md"),
            config=Config(),
        )


def test_detect_issues_empty_file(tmp_path):
    """Returns empty list and zero count for a file with no links."""
    md = tmp_path / "empty.md"
    md.write_text("# No links\n")
    issues, count = detect_issues(
        func="check_broken_paths",
        file_path=md,
        config=Config(),
    )
    assert issues == []
    assert count == 0


def test_detect_issues_broken_path(tmp_path):
    """Detects broken relative paths in a markdown file."""
    md = tmp_path / "test.md"
    md.write_text("[link](./nonexistent.md)\n")
    issues, count = detect_issues(
        func="check_broken_paths",
        file_path=md,
        config=Config(),
    )
    assert len(issues) == 1
    assert count == 1


def test_detect_issues_valid_path(tmp_path):
    """Returns no issues for valid relative paths."""
    target = tmp_path / "exists.md"
    target.write_text("# Exists")
    md = tmp_path / "test.md"
    md.write_text("[link](./exists.md)\n")
    issues, count = detect_issues(
        func="check_broken_paths",
        file_path=md,
        config=Config(),
    )
    assert issues == []
    assert count == 1


def test_detect_issues_paths_tracking(tmp_path):
    """Detects paths missing tracking IDs."""
    md = tmp_path / "test.md"
    md.write_text("[link](./docs/guide.md)\n")
    issues, count = detect_issues(
        func="check_paths_tracking",
        file_path=md,
        config=Config(),
    )
    assert len(issues) == 1
    assert count == 1


def test_detect_issues_urls_tracking(tmp_path):
    """Detects URLs missing tracking IDs on tracking domains."""
    md = tmp_path / "test.md"
    md.write_text("[link](https://learn.microsoft.com/azure)\n")
    issues, count = detect_issues(
        func="check_urls_tracking",
        file_path=md,
        config=Config(tracking_domains=["learn.microsoft.com"]),
    )
    assert len(issues) == 1
    assert count == 1


def test_detect_issues_urls_locale(tmp_path):
    """Detects URLs with locale segments."""
    md = tmp_path / "test.md"
    md.write_text("[link](https://learn.microsoft.com/en-us/azure)\n")
    issues, count = detect_issues(
        func="check_urls_locale",
        file_path=md,
        config=Config(),
    )
    assert len(issues) == 1
    assert count == 1


def test_detect_issues_returns_path_count_for_path_checks(tmp_path):
    """Links count is path count for path-based checks."""
    md = tmp_path / "test.md"
    md.write_text("[p1](./a.md)\n[p2](./b.md)\n[u](https://example.com)\n")
    _, count = detect_issues(
        func="check_broken_paths",
        file_path=md,
        config=Config(),
    )
    assert count == 2


def test_detect_issues_returns_url_count_for_url_checks(tmp_path):
    """Links count is URL count for URL-based checks."""
    md = tmp_path / "test.md"
    md.write_text("[p](./a.md)\n[u1](https://a.com/page)\n[u2](https://b.com/page)\n")
    _, count = detect_issues(
        func="check_urls_locale",
        file_path=md,
        config=Config(),
    )
    assert count == 2


def test_link_type_used_instead_of_path_checks():
    """link_type on checks replaces the old _PATH_CHECKS set."""
    from markdown_checker.checks import REGISTRY

    path_checks = {name for name, check in REGISTRY.items() if check.link_type == "paths"}
    assert "check_broken_paths" in path_checks
    assert "check_paths_tracking" in path_checks

    url_checks = {name for name, check in REGISTRY.items() if check.link_type == "urls"}
    assert "check_broken_urls" in url_checks
    assert "check_urls_tracking" in url_checks
    assert "check_urls_locale" in url_checks


def test_run_check_on_files(tmp_path):
    """run_check_on_files aggregates results across multiple files."""
    md1 = tmp_path / "a.md"
    md1.write_text("[link](./missing.md)\n")
    md2 = tmp_path / "b.md"
    md2.write_text("# No links\n")
    result = run_check_on_files(
        func="check_broken_paths",
        files_paths=[md1, md2],
        config=Config(),
        progress_callback=lambda: None,
    )
    assert len(result.issues) == 1
    assert result.issues[0][0] == md1
    assert result.links_checked == 1


# --- Stage 2: bounded file-window pipelining ---


def test_run_check_on_files_overlaps_url_checks_across_files(tmp_path):
    """URL checks for multiple files are submitted concurrently instead of one file at a time."""
    files = []
    for i in range(3):
        md = tmp_path / f"file{i}.md"
        md.write_text(f"[link](https://host{i}.example.com/page)\n")
        files.append(md)

    def slow_check(self: MarkdownURL, **kwargs: object) -> URLCheckResult:
        time.sleep(0.2)
        return URLCheckResult(status="alive", http_status_code=200)

    config = Config(max_workers=3, per_host_delay=0.0)
    start = time.monotonic()
    with patch.object(MarkdownURL, "check", slow_check):
        result = run_check_on_files(
            func="check_broken_urls",
            files_paths=files,
            config=config,
            progress_callback=lambda: None,
        )
    elapsed = time.monotonic() - start

    assert result.links_checked == 3
    assert result.issues == []
    # Sequential (Stage 1) would take ~3 * 0.2s = 0.6s; overlapping submission keeps it near 0.2s.
    assert elapsed < 0.4, f"expected overlapping checks (~0.2s), took {elapsed:.2f}s"


def test_run_check_on_files_smaller_than_window_size_still_correct(tmp_path, monkeypatch):
    """More files than the window still produce complete, correctly ordered results."""
    monkeypatch.setattr("markdown_checker.checker._MIN_FILE_WINDOW", 1)
    monkeypatch.setattr("markdown_checker.checker._MAX_FILE_WINDOW", 2)
    files = []
    for i in range(5):
        md = tmp_path / f"f{i}.md"
        md.write_text(f"[link](https://broken{i}.example.com/page)\n")
        files.append(md)

    broken_result = URLCheckResult(status="broken", http_status_code=404)
    with patch.object(MarkdownURL, "check", return_value=broken_result):
        result = run_check_on_files(
            func="check_broken_urls",
            files_paths=files,
            config=Config(),
            progress_callback=lambda: None,
        )

    assert result.links_checked == 5
    assert len(result.issues) == 5
    assert [path for path, _ in result.issues] == files


def test_window_admits_more_files_when_max_workers_is_larger(tmp_path, monkeypatch):
    """The adaptive window scales with max_workers: more files get submitted (and their
    checks dispatched) before the producer blocks collecting the oldest one."""
    monkeypatch.setattr("markdown_checker.checker._MIN_FILE_WINDOW", 1)
    monkeypatch.setattr("markdown_checker.checker._MAX_FILE_WINDOW", 100)

    def make_files(prefix: str, n: int) -> list[Path]:
        paths = []
        for i in range(n):
            md = tmp_path / f"{prefix}{i}.md"
            md.write_text(f"[link](https://{prefix}-host{i}.example.com/page)\n")
            paths.append(md)
        return paths

    def dispatched_before_block(max_workers: int, prefix: str) -> int:
        files = make_files(prefix, 6)
        release = threading.Event()
        lock = threading.Lock()
        calls: list[float] = []

        def blocking_check(self: MarkdownURL, **kwargs: object) -> URLCheckResult:
            with lock:
                calls.append(time.monotonic())
            release.wait(timeout=5)
            return URLCheckResult(status="alive", http_status_code=200)

        done = threading.Event()

        def run() -> None:
            with patch.object(MarkdownURL, "check", blocking_check):
                run_check_on_files(
                    func="check_broken_urls",
                    files_paths=files,
                    config=Config(max_workers=max_workers, per_host_delay=0.0),
                    progress_callback=lambda: None,
                )
            done.set()

        thread = threading.Thread(target=run)
        thread.start()
        time.sleep(0.3)  # let dispatch race ahead while every check() call is blocked
        with lock:
            observed = len(calls)
        release.set()
        thread.join(timeout=5)
        assert done.is_set()
        return observed

    low = dispatched_before_block(max_workers=1, prefix="low")
    high = dispatched_before_block(max_workers=6, prefix="high")

    assert high > low
