from pathlib import Path

from markdown_checker.utils.list_files import get_files_paths_list


def test_returns_tuple_of_lists(tmp_path: Path):
    """Returns a tuple of (subdirectories, file_paths)."""
    result = get_files_paths_list(tmp_path, [".md"])
    assert isinstance(result, tuple)
    assert len(result) == 2


def test_finds_md_files(tmp_path: Path):
    """Finds markdown files in the root directory."""
    (tmp_path / "file.md").write_text("content")
    (tmp_path / "other.txt").write_text("content")
    _, files = get_files_paths_list(tmp_path, [".md"])
    assert len(files) == 1
    assert files[0].name == "file.md"


def test_finds_files_recursively(tmp_path: Path):
    """Finds files in subdirectories recursively."""
    subdir = tmp_path / "sub"
    subdir.mkdir()
    (subdir / "nested.md").write_text("content")
    _, files = get_files_paths_list(tmp_path, [".md"])
    assert len(files) == 1
    assert files[0].name == "nested.md"


def test_returns_subdirectories(tmp_path: Path):
    """Returns all subdirectories found during traversal."""
    (tmp_path / "dir1").mkdir()
    (tmp_path / "dir2").mkdir()
    dirs, _ = get_files_paths_list(tmp_path, [".md"])
    assert len(dirs) == 2


def test_multiple_extensions(tmp_path: Path):
    """Filters by multiple file extensions."""
    (tmp_path / "a.md").write_text("content")
    (tmp_path / "b.ipynb").write_text("content")
    (tmp_path / "c.txt").write_text("content")
    _, files = get_files_paths_list(tmp_path, [".md", ".ipynb"])
    assert len(files) == 2


def test_empty_extensions_returns_no_files(tmp_path: Path):
    """Returns no files when extensions list is empty."""
    (tmp_path / "file.md").write_text("content")
    _, files = get_files_paths_list(tmp_path, [])
    assert files == []


def test_empty_directory(tmp_path: Path):
    """Returns empty lists for an empty directory."""
    dirs, files = get_files_paths_list(tmp_path, [".md"])
    assert dirs == []
    assert files == []


def test_case_insensitive_extension(tmp_path: Path):
    """Matches extensions case-insensitively."""
    (tmp_path / "FILE.MD").write_text("content")
    _, files = get_files_paths_list(tmp_path, [".md"])
    assert len(files) == 1


def test_deeply_nested(tmp_path: Path):
    """Finds files in deeply nested directory structures."""
    deep = tmp_path / "a" / "b" / "c"
    deep.mkdir(parents=True)
    (deep / "deep.md").write_text("content")
    _, files = get_files_paths_list(tmp_path, [".md"])
    assert len(files) == 1
    assert files[0].name == "deep.md"


def test_returns_path_objects(tmp_path: Path):
    """All returned items are Path objects."""
    (tmp_path / "file.md").write_text("content")
    (tmp_path / "sub").mkdir()
    dirs, files = get_files_paths_list(tmp_path, [".md"])
    for d in dirs:
        assert isinstance(d, Path)
    for f in files:
        assert isinstance(f, Path)
