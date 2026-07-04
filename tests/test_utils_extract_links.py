from pathlib import Path

import pytest

from markdown_checker.utils.extract_links import get_links_from_md_file
from markdown_checker.utils.extract_links import MarkdownLinks


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


def test_skips_links_inside_fenced_code_blocks(tmp_path: Path):
    """Links inside fenced code blocks (``` or ~~~) are ignored."""
    md = tmp_path / "fenced.md"
    md.write_text(
        "[before](https://before.com)\n"
        "```\n"
        "[inside](https://inside.com)\n"
        "[path](./inside/file.md)\n"
        "```\n"
        "[after](https://after.com)\n"
    )
    result = get_links_from_md_file(md)
    urls = [u.link for u in result.urls]
    assert "https://before.com" in urls
    assert "https://after.com" in urls
    assert "https://inside.com" not in urls
    assert len(result.paths) == 0


def test_skips_links_inside_tilde_fenced_code_blocks(tmp_path: Path):
    """Links inside ~~~ fenced code blocks are ignored."""
    md = tmp_path / "tilde.md"
    md.write_text("~~~\n[inside](https://inside.com)\n~~~\n[outside](https://outside.com)\n")
    result = get_links_from_md_file(md)
    assert len(result.urls) == 1
    assert result.urls[0].link == "https://outside.com"


def test_extracts_url_with_balanced_parentheses(tmp_path: Path):
    """URLs containing balanced parentheses are captured in full, not truncated."""
    md = tmp_path / "parens.md"
    md.write_text("[rust](https://en.wikipedia.org/wiki/Rust_(programming_language))\n")
    result = get_links_from_md_file(md)
    assert len(result.urls) == 1
    assert result.urls[0].link == "https://en.wikipedia.org/wiki/Rust_(programming_language)"


def test_extracts_bare_relative_paths(tmp_path: Path):
    """Relative paths without a leading ./ or / are extracted as paths."""
    md = tmp_path / "bare.md"
    md.write_text("[a](usage.md)\n[b](docs/usage.md)\n")
    result = get_links_from_md_file(md)
    assert [p.link for p in result.paths] == ["usage.md", "docs/usage.md"]
    assert result.urls == []


def test_title_is_stripped_from_destination(tmp_path: Path):
    """Optional link titles are not captured as part of the destination."""
    md = tmp_path / "title.md"
    md.write_text("[a](./file.md \"the title\")\n[b](https://example.com 'another')\n")
    result = get_links_from_md_file(md)
    assert result.paths[0].link == "./file.md"
    assert result.urls[0].link == "https://example.com"


def test_angle_bracket_destination_with_spaces(tmp_path: Path):
    """<...> destinations may contain spaces and are captured without the brackets."""
    md = tmp_path / "angle.md"
    md.write_text("[a](<./my file.md>)\n")
    result = get_links_from_md_file(md)
    assert result.paths[0].link == "./my file.md"


def test_skips_anchors_and_scheme_links(tmp_path: Path):
    """Anchor-only links and non-http URI schemes are neither URLs nor paths."""
    md = tmp_path / "skipped.md"
    md.write_text("[a](#section)\n[b](mailto:someone@example.com)\n[c](tel:+123456)\n")
    result = get_links_from_md_file(md)
    assert result.urls == []
    assert result.paths == []


def test_protocol_relative_link_checked_as_https_url(tmp_path: Path):
    """Protocol-relative //host links are classified as URLs with https prepended."""
    md = tmp_path / "protorel.md"
    md.write_text("[a](//example.com/page)\n")
    result = get_links_from_md_file(md)
    assert result.paths == []
    assert len(result.urls) == 1
    assert result.urls[0].link == "https://example.com/page"
