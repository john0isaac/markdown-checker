from pathlib import Path

import pytest

from markdown_checker.utils.extract_links import MarkdownLinks, get_links_from_md_file


def test_get_links_from_md_file_returns_markdown_links(sample1_path: Path):
    """Returns a MarkdownLinks dataclass."""
    result = get_links_from_md_file(sample1_path)
    assert isinstance(result, MarkdownLinks)


def test_extracts_urls_from_sample(sample1_path: Path):
    """Extracts HTTP/HTTPS URLs from markdown link syntax."""
    result = get_links_from_md_file(sample1_path)
    assert len(result.urls) > 0
    for url in result.urls:
        assert url.link.startswith("http")


def test_extracts_paths_from_file_with_relative_paths(tmp_path: Path):
    """Extracts relative file paths from markdown link syntax."""
    md = tmp_path / "test.md"
    md.write_text("[link](./some/file.md)\n[link2](../other/file.txt)\n")
    result = get_links_from_md_file(md)
    assert len(result.paths) == 2
    assert result.paths[0].link == "./some/file.md"
    assert result.paths[1].link == "../other/file.txt"


def test_no_links_returns_empty(tmp_path: Path):
    """Returns empty lists when the file has no links."""
    md = tmp_path / "empty.md"
    md.write_text("# No links here\nJust text.\n")
    result = get_links_from_md_file(md)
    assert result.urls == []
    assert result.paths == []


def test_line_numbers_are_correct(tmp_path: Path):
    """Associates each extracted link with its correct line number."""
    md = tmp_path / "lines.md"
    md.write_text("line1\n[url](https://example.com)\nline3\n[path](./file.md)\n")
    result = get_links_from_md_file(md)
    assert result.urls[0].line_number == 2
    assert result.paths[0].line_number == 4


def test_file_path_is_stored(tmp_path: Path):
    """Stores the source file path on each extracted link."""
    md = tmp_path / "source.md"
    md.write_text("[link](https://example.com)\n")
    result = get_links_from_md_file(md)
    assert result.urls[0].file_path == md


def test_multiple_links_on_same_line(tmp_path: Path):
    """Extracts multiple links from a single line."""
    md = tmp_path / "multi.md"
    md.write_text("[a](https://a.com) and [b](https://b.com)\n")
    result = get_links_from_md_file(md)
    assert len(result.urls) == 2


def test_ignores_non_link_parentheses(tmp_path: Path):
    """Does not extract text in parentheses that is not a markdown link."""
    md = tmp_path / "nolink.md"
    md.write_text("This is (not a link) and neither is this (one).\n")
    result = get_links_from_md_file(md)
    assert result.urls == []
    assert result.paths == []


def test_markdown_links_dataclass():
    """MarkdownLinks dataclass stores urls and paths lists."""
    links = MarkdownLinks(urls=[], paths=[])
    assert links.urls == []
    assert links.paths == []


@pytest.mark.parametrize(
    "link_text, expect_url, expect_path",
    [
        ("[link](https://example.com/page)", True, False),
        ("[link](http://example.com/page)", True, False),
        ("[link](./docs/file.md)", False, True),
        ("[link](../README.md)", False, True),
    ],
)
def test_url_vs_path_classification(tmp_path: Path, link_text: str, expect_url: bool, expect_path: bool):
    """Correctly classifies links as URLs or paths."""
    md = tmp_path / "classify.md"
    md.write_text(link_text + "\n")
    result = get_links_from_md_file(md)
    assert (len(result.urls) > 0) == expect_url
    assert (len(result.paths) > 0) == expect_path
