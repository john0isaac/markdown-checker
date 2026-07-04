from pathlib import Path

import pytest

from markdown_checker.models.path import MarkdownPath
from markdown_checker.models.url import MarkdownURL
from markdown_checker.reports.format_output import format_issues_table
from markdown_checker.reports.format_output import format_links


@pytest.fixture
def sample_urls():
    return [
        MarkdownURL(link="https://example.com/broken", line_number=10, file_path=Path("file.md"), issue="is broken"),
        MarkdownURL(
            link="https://example.com/also-broken", line_number=20, file_path=Path("file.md"), issue="is broken"
        ),
    ]


@pytest.fixture
def sample_paths():
    return [
        MarkdownPath(link="./missing.md", line_number=5, file_path=Path("file.md"), issue="is broken"),
    ]


def test_format_links_returns_html_table(sample_urls):
    """Returns an HTML table string with link details."""
    result = format_links(sample_urls)
    assert "<table>" in result
    assert "</table>" in result
    assert "<thead>" in result
    assert "<tbody>" in result


def test_format_links_contains_all_links(sample_urls):
    """Includes every provided link in the output."""
    result = format_links(sample_urls)
    for url in sample_urls:
        assert url.link in result


def test_format_links_contains_line_numbers(sample_urls):
    """Includes line numbers for each link."""
    result = format_links(sample_urls)
    assert "`10`" in result
    assert "`20`" in result


def test_format_links_numbering(sample_urls):
    """Numbers links sequentially starting from 1."""
    result = format_links(sample_urls)
    assert "<td>1</td>" in result
    assert "<td>2</td>" in result


def test_format_links_single_link(sample_paths):
    """Formats a single link correctly."""
    result = format_links(sample_paths)
    assert "./missing.md" in result
    assert "<td>1</td>" in result


def test_format_links_ends_with_pipe_newline(sample_urls):
    """Output ends with the table closing pipe and newline."""
    result = format_links(sample_urls)
    assert result.endswith("|\n")


def test_format_links_local_mode_has_file_links(sample_urls):
    """In non-CI mode, line numbers are rendered as file links."""
    result = format_links(sample_urls, output_mode="local")
    assert "file.md#L10" in result


def test_format_links_ci_mode_no_file_links(sample_urls):
    """In CI mode without a repo_url, line numbers are plain text without file links."""
    result = format_links(sample_urls, output_mode="ci")
    assert "file.md#L" not in result


def test_format_links_ci_mode_with_repo_url_has_clickable_links(sample_urls):
    """In CI mode with a repo_url, line numbers are rendered as clickable repo links."""
    result = format_links(sample_urls, output_mode="ci", repo_url="https://github.com/owner/repo/blob/sha")
    assert "[`10`](https://github.com/owner/repo/blob/sha/file.md#L10)" in result
    assert "[`20`](https://github.com/owner/repo/blob/sha/file.md#L20)" in result


def test_format_links_ci_mode_repo_url_relativizes_absolute_paths(monkeypatch, tmp_path):
    """In CI mode, absolute paths under the cwd are relativized before joining to repo_url."""
    monkeypatch.chdir(tmp_path)
    links = [
        MarkdownURL(
            link="https://example.com/broken", line_number=3, file_path=tmp_path / "docs" / "a.md", issue="is broken"
        ),
    ]
    result = format_links(links, output_mode="ci", repo_url="https://github.com/owner/repo/blob/sha")
    assert "[`3`](https://github.com/owner/repo/blob/sha/docs/a.md#L3)" in result


def test_format_links_ci_mode_repo_url_skips_paths_outside_cwd(monkeypatch, tmp_path):
    """In CI mode, absolute paths outside the cwd fall back to plain text."""
    monkeypatch.chdir(tmp_path)
    outside = Path("/somewhere/else/file.md")
    links = [
        MarkdownURL(link="https://example.com/broken", line_number=3, file_path=outside, issue="is broken"),
    ]
    result = format_links(links, output_mode="ci", repo_url="https://github.com/owner/repo/blob/sha")
    assert "https://github.com/owner/repo/blob/sha" not in result
    assert "`3`" in result


def test_format_links_empty_list():
    """Returns a valid table structure even with an empty list."""
    result = format_links([])
    assert "<table>" in result
    assert "</table>" in result


def test_format_issues_table_local_mode_has_file_links(sample_urls):
    """In non-CI mode, file paths are rendered as clickable links."""
    result = format_issues_table([(Path("file.md"), sample_urls)], output_mode="local")
    assert "[`file.md`](file.md)" in result


def test_format_issues_table_ci_mode_no_repo_url(sample_urls):
    """In CI mode without a repo_url, file paths are plain text without links."""
    result = format_issues_table([(Path("file.md"), sample_urls)], output_mode="ci")
    assert "[`file.md`]" not in result
    assert "`file.md`" in result


def test_format_issues_table_ci_mode_with_repo_url_has_clickable_links(sample_urls):
    """In CI mode with a repo_url, file paths are rendered as clickable repo links."""
    result = format_issues_table(
        [(Path("file.md"), sample_urls)], output_mode="ci", repo_url="https://github.com/owner/repo/blob/sha"
    )
    assert "[`file.md`](https://github.com/owner/repo/blob/sha/file.md)" in result
