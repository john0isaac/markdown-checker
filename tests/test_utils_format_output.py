from pathlib import Path

import pytest

from markdown_checker.models.path import MarkdownPath
from markdown_checker.models.url import MarkdownURL
from markdown_checker.utils.format_output import format_links


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


def test_format_links_local_mode_has_file_links(sample_urls, monkeypatch):
    """In non-CI mode, line numbers are rendered as file links."""
    monkeypatch.delenv("CI", raising=False)
    result = format_links(sample_urls)
    assert "file.md#L10" in result


def test_format_links_ci_mode_no_file_links(sample_urls, monkeypatch):
    """In CI mode, line numbers are plain text without file links."""
    monkeypatch.setenv("CI", "true")
    result = format_links(sample_urls)
    assert "file.md#L" not in result


def test_format_links_empty_list():
    """Returns a valid table structure even with an empty list."""
    result = format_links([])
    assert "<table>" in result
    assert "</table>" in result
