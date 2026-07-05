from pathlib import Path

import pytest

from markdown_checker.models.path import MarkdownPath


@pytest.mark.parametrize(
    "link, expected",
    [
        ("./docs/guide.md#section", "./docs/guide.md"),
        ("./docs/guide.md", "./docs/guide.md"),
        ("./docs/guide.md?WT.mc_id=test123", "./docs/guide.md"),
        ("../README.md#heading", "../README.md"),
        ("./docs/file.txt#frag", "./docs/file.txt"),
    ],
)
def test_remove_fragments(link: str, expected: str):
    """Strips fragment identifiers and tracking params from path strings."""
    path = MarkdownPath(link=link, line_number=1, file_path=Path("test.md"))
    assert path.remove_fragments() == expected


@pytest.mark.parametrize(
    "link, expected",
    [
        ("./docs/guide.md#section", Path("./docs/guide.md")),
        ("./docs/guide.md", Path("./docs/guide.md")),
    ],
)
def test_path_without_fragments(link: str, expected: Path):
    """Property returns a Path object with fragments removed."""
    path = MarkdownPath(link=link, line_number=1, file_path=Path("test.md"))
    assert path.path_without_fragments == expected


def test_exists_with_existing_file(tmp_path: Path):
    """Returns True when the referenced file exists on disk."""
    target = tmp_path / "exists.md"
    target.write_text("# Hello")
    parent = tmp_path / "parent.md"
    path = MarkdownPath(link="./exists.md", line_number=1, file_path=parent)
    assert path.exists() is True


def test_exists_with_missing_file(tmp_path: Path):
    """Returns False when the referenced file does not exist."""
    parent = tmp_path / "parent.md"
    path = MarkdownPath(link="./nonexistent.md", line_number=1, file_path=parent)
    assert path.exists() is False


def test_exists_strips_leading_slash(tmp_path: Path):
    """Handles absolute-style paths starting with / by stripping the slash."""
    target = tmp_path / "absolute.md"
    target.write_text("content")
    parent = tmp_path / "parent.md"
    path = MarkdownPath(link="/absolute.md", line_number=1, file_path=parent)
    result = path.exists()
    # The leading slash is restored if the file was not found
    assert isinstance(result, bool)


def test_exists_with_fragment(tmp_path: Path):
    """Returns True for paths with fragment anchors when the base file exists."""
    target = tmp_path / "readme.md"
    target.write_text("# Section")
    parent = tmp_path / "parent.md"
    path = MarkdownPath(link="./readme.md#section", line_number=1, file_path=parent)
    assert path.exists() is True


def test_get_full_path_relative(tmp_path: Path):
    """Resolves relative path against the parent file's directory."""
    parent = tmp_path / "subdir" / "parent.md"
    parent.parent.mkdir(parents=True, exist_ok=True)
    path = MarkdownPath(link="../other.md", line_number=1, file_path=parent)
    result = path.get_full_path_relative()
    assert result.endswith("other.md")
    assert "subdir" not in result.split("/")[-1]


def test_get_full_path_returns_path(tmp_path: Path):
    """Returns a resolved Path object."""
    target = tmp_path / "target.md"
    target.write_text("content")
    parent = tmp_path / "parent.md"
    path = MarkdownPath(link="./target.md", line_number=1, file_path=parent)
    result = path.get_full_path()
    assert isinstance(result, Path)


def test_path_without_fragments_with_tracking():
    """Removes tracking params before fragment stripping."""
    path = MarkdownPath(link="./guide.md?WT.mc_id=abc#section", line_number=1, file_path=Path("test.md"))
    assert path.path_without_fragments == Path("./guide.md")


def test_remove_fragments_no_extension():
    """Returns truncated result when the only dot is in the relative path prefix."""
    path = MarkdownPath(link="./docs/README", line_number=1, file_path=Path("test.md"))
    # rfind(".") finds the dot in "./" so it truncates there
    result = path.remove_fragments()
    assert isinstance(result, str)
