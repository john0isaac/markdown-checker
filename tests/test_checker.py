from pathlib import Path

import pytest

from markdown_checker.checker import detect_issues, run_check_on_files
from markdown_checker.models.config import Config


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
