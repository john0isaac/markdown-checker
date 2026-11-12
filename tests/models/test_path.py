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
        ("./docs/guide.md?foo=bar", "./docs/guide.md"),
        ("./docs/guide.md?foo=bar#section", "./docs/guide.md"),
        ("./docs/guide.md?v=1.2", "./docs/guide.md"),
        ("./docs/guide.md?v=1.2#section", "./docs/guide.md"),
        ("./docs/guide.md#step-1.2", "./docs/guide.md"),
        ("LICENSE#L10", "LICENSE"),
        ("./docs/README", "./docs/README"),
        ("../missing/LICENSE", "../missing/LICENSE"),
        ("docs/v1.0/missing", "docs/v1.0/missing"),
        ("./my%20file.md#section", "./my file.md"),
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


def test_exists_with_missing_extensionless_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Returns False for a missing file without an extension instead of resolving to the directory."""
    monkeypatch.chdir(tmp_path)
    parent = tmp_path / "parent.md"
    path = MarkdownPath(link="./LICENSE", line_number=1, file_path=parent)
    assert path.exists() is False


def test_exists_root_relative_resolves_against_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Resolves /-prefixed links against the working directory (repository root)."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "guide.md").write_text("# Guide")
    parent = tmp_path / "sub" / "parent.md"
    monkeypatch.chdir(tmp_path)
    path = MarkdownPath(link="/docs/guide.md", line_number=1, file_path=parent)
    assert path.exists() is True
    assert path.get_full_path() == tmp_path.resolve() / "docs" / "guide.md"


def test_exists_with_percent_encoded_name(tmp_path: Path):
    """Decodes percent-encoded characters such as %20 before checking existence."""
    (tmp_path / "my file.md").write_text("# Hello")
    parent = tmp_path / "parent.md"
    path = MarkdownPath(link="./my%20file.md", line_number=1, file_path=parent)
    assert path.exists() is True


def test_exists_with_fragment(tmp_path: Path):
    """Returns True for paths with fragment anchors when the base file exists."""
    target = tmp_path / "readme.md"
    target.write_text("# Section")
    parent = tmp_path / "parent.md"
    path = MarkdownPath(link="./readme.md#section", line_number=1, file_path=parent)
    assert path.exists() is True


def test_exists_with_query_string(tmp_path: Path):
    """Returns True for paths with a query string when the base file exists."""
    target = tmp_path / "readme.md"
    target.write_text("# Section")
    parent = tmp_path / "parent.md"
    path = MarkdownPath(link="./readme.md?foo=bar", line_number=1, file_path=parent)
    assert path.exists() is True


def test_exists_with_dot_in_query_string(tmp_path: Path):
    """Returns True when the query string itself contains a dot."""
    target = tmp_path / "readme.md"
    target.write_text("# Section")
    parent = tmp_path / "parent.md"
    path = MarkdownPath(link="./readme.md?v=1.2", line_number=1, file_path=parent)
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
