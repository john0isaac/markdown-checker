from pathlib import Path

import pytest

from markdown_checker.checker import _PATH_CHECKS, detect_issues


def test_detect_issues_unknown_func_raises():
    """Raises ValueError for unknown check function names."""
    with pytest.raises(ValueError, match="Unknown check function"):
        detect_issues(
            func="nonexistent",
            file_path=Path("test.md"),
            skip_urls_containing=[],
            skip_domains=[],
            tracking_domains=[],
            timeout=5,
            retries=1,
        )


def test_detect_issues_empty_file(tmp_path):
    """Returns empty list and zero count for a file with no links."""
    md = tmp_path / "empty.md"
    md.write_text("# No links\n")
    issues, count = detect_issues(
        func="check_broken_paths",
        file_path=md,
        skip_urls_containing=[],
        skip_domains=[],
        tracking_domains=[],
        timeout=5,
        retries=1,
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
        skip_urls_containing=[],
        skip_domains=[],
        tracking_domains=[],
        timeout=5,
        retries=1,
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
        skip_urls_containing=[],
        skip_domains=[],
        tracking_domains=[],
        timeout=5,
        retries=1,
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
        skip_urls_containing=[],
        skip_domains=[],
        tracking_domains=[],
        timeout=5,
        retries=1,
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
        skip_urls_containing=[],
        skip_domains=[],
        tracking_domains=["learn.microsoft.com"],
        timeout=5,
        retries=1,
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
        skip_urls_containing=[],
        skip_domains=[],
        tracking_domains=[],
        timeout=5,
        retries=1,
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
        skip_urls_containing=[],
        skip_domains=[],
        tracking_domains=[],
        timeout=5,
        retries=1,
    )
    assert count == 2


def test_detect_issues_returns_url_count_for_url_checks(tmp_path):
    """Links count is URL count for URL-based checks."""
    md = tmp_path / "test.md"
    md.write_text("[p](./a.md)\n[u1](https://a.com/page)\n[u2](https://b.com/page)\n")
    _, count = detect_issues(
        func="check_urls_locale",
        file_path=md,
        skip_urls_containing=[],
        skip_domains=[],
        tracking_domains=[],
        timeout=5,
        retries=1,
    )
    assert count == 2


def test_path_checks_set():
    """_PATH_CHECKS contains the expected check names."""
    assert "check_broken_paths" in _PATH_CHECKS
    assert "check_paths_tracking" in _PATH_CHECKS
    assert "check_paths_locale" in _PATH_CHECKS
