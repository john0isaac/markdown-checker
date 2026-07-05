import pytest

from markdown_checker.checks.broken_paths import BrokenPathsCheck
from markdown_checker.models.path import MarkdownPath
from markdown_checker.utils.extract_links import MarkdownLinks


@pytest.fixture
def check():
    return BrokenPathsCheck()


def test_name():
    """Check name matches registry key."""
    assert BrokenPathsCheck.name == "check_broken_paths"


def test_no_paths_returns_empty(check, make_markdown_links):
    """Returns empty list when there are no paths to check."""
    links = make_markdown_links()
    result = check.run(links)
    assert result == []


def test_existing_path_not_reported(check, tmp_path):
    """Existing paths are not reported as broken."""
    target = tmp_path / "exists.md"
    target.write_text("# exists")
    parent = tmp_path / "parent.md"
    path = MarkdownPath(link="./exists.md", line_number=1, file_path=parent)
    links = MarkdownLinks(urls=[], paths=[path])
    result = check.run(links)
    assert result == []


def test_missing_path_reported(check, tmp_path):
    """Missing paths are reported with 'is broken' issue."""
    parent = tmp_path / "parent.md"
    path = MarkdownPath(link="./nonexistent.md", line_number=5, file_path=parent)
    links = MarkdownLinks(urls=[], paths=[path])
    result = check.run(links)
    assert len(result) == 1
    assert result[0].issue == "is broken"
    assert result[0].link == "./nonexistent.md"


def test_mixed_existing_and_missing(check, tmp_path):
    """Only reports missing paths, not existing ones."""
    target = tmp_path / "exists.md"
    target.write_text("content")
    parent = tmp_path / "parent.md"
    existing = MarkdownPath(link="./exists.md", line_number=1, file_path=parent)
    missing = MarkdownPath(link="./missing.md", line_number=2, file_path=parent)
    links = MarkdownLinks(urls=[], paths=[existing, missing])
    result = check.run(links)
    assert len(result) == 1
    assert result[0].link == "./missing.md"


def test_urls_are_ignored(check, make_markdown_url, make_markdown_links):
    """URLs in the links are not checked by BrokenPathsCheck."""
    links = make_markdown_links(urls=[make_markdown_url("https://example.com")])
    result = check.run(links)
    assert result == []
