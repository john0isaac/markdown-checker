from pathlib import Path

import click
import pytest

from markdown_checker.utils.pyproject_config import _prescan
from markdown_checker.utils.pyproject_config import _reject_unknown_keys
from markdown_checker.utils.pyproject_config import find_pyproject
from markdown_checker.utils.pyproject_config import load_config_section
from markdown_checker.utils.pyproject_config import resolve_default_map


@click.command()
@click.option("-f", "--func", required=True)
@click.option("-to", "--timeout", type=int, default=20)
@click.option("-sf", "--skip-files", multiple=True)
def _dummy_command() -> None:
    pass


def test_find_pyproject_in_start_dir(tmp_path: Path):
    """Finds a pyproject.toml directly inside the start directory."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[tool.markdown-checker]\nfunc = 'check_broken_paths'\n")
    assert find_pyproject(tmp_path) == pyproject


def test_find_pyproject_walks_up(tmp_path: Path):
    """Walks up parent directories to find the nearest pyproject.toml."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[tool.markdown-checker]\n")
    nested = tmp_path / "a" / "b" / "c"
    nested.mkdir(parents=True)
    assert find_pyproject(nested) == pyproject


def test_find_pyproject_returns_none_when_absent(tmp_path: Path, monkeypatch):
    """Returns None when no pyproject.toml exists up to the filesystem root."""
    nested = tmp_path / "a" / "b"
    nested.mkdir(parents=True)

    original_is_file = Path.is_file
    monkeypatch.setattr(
        Path,
        "is_file",
        lambda self: False if self.name == "pyproject.toml" else original_is_file(self),
    )

    assert find_pyproject(nested) is None


def test_load_config_section_reads_table(tmp_path: Path):
    """Reads the [tool.markdown-checker] table."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[tool.markdown-checker]\ntimeout = 5\nskip-files = ['a.md']\n")
    assert load_config_section(pyproject) == {"timeout": 5, "skip-files": ["a.md"]}


def test_load_config_section_missing_table_returns_empty(tmp_path: Path):
    """Returns an empty dict when the table is absent."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[tool.other]\nfoo = 1\n")
    assert load_config_section(pyproject) == {}


def test_load_config_section_invalid_toml_raises(tmp_path: Path):
    """Raises click.UsageError for invalid TOML syntax."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("not valid [[[ toml")
    with pytest.raises(click.UsageError):
        load_config_section(pyproject)


def test_load_config_section_non_table_raises(tmp_path: Path):
    """Raises click.UsageError when [tool.markdown-checker] is not a table."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[tool]\nmarkdown-checker = 'oops'\n")
    with pytest.raises(click.UsageError):
        load_config_section(pyproject)


def test_reject_unknown_keys_passes_for_known_keys():
    """Does not raise when all keys are known options."""
    _reject_unknown_keys({"timeout": 5, "skip-files": ["a.md"]}, _dummy_command, Path("pyproject.toml"))


def test_reject_unknown_keys_raises_for_unknown_key():
    """Raises click.UsageError listing the unknown key."""
    with pytest.raises(click.UsageError, match="portable"):
        _reject_unknown_keys({"portable": 5}, _dummy_command, Path("pyproject.toml"))


def test_reject_unknown_keys_suggests_hyphenated_key():
    """Suggests the hyphenated form when the user wrote an underscored key."""
    with pytest.raises(click.UsageError, match="skip-files"):
        _reject_unknown_keys({"skip_files": ["a.md"]}, _dummy_command, Path("pyproject.toml"))


def test_prescan_detects_isolated_flag():
    """Detects --isolated among raw args."""
    isolated, path = _prescan(["--isolated", "-f", "check_broken_paths"])
    assert isolated is True
    assert path is None


def test_prescan_detects_config_flag_with_space():
    """Detects -c/--config PATH as two separate args."""
    isolated, path = _prescan(["--config", "custom.toml", "-f", "check_broken_paths"])
    assert isolated is False
    assert path == Path("custom.toml")


def test_prescan_detects_short_config_flag():
    """Detects -c PATH."""
    _, path = _prescan(["-c", "custom.toml"])
    assert path == Path("custom.toml")


def test_prescan_detects_config_flag_with_equals():
    """Detects --config=PATH."""
    _, path = _prescan(["--config=custom.toml"])
    assert path == Path("custom.toml")


def test_prescan_returns_defaults_when_absent():
    """Returns (False, None) when neither flag is present."""
    isolated, path = _prescan(["-f", "check_broken_paths"])
    assert isolated is False
    assert path is None


def test_resolve_default_map_returns_none_when_isolated(tmp_path: Path, monkeypatch):
    """Returns None when --isolated is passed, even if a valid pyproject.toml exists."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text("[tool.markdown-checker]\ntimeout = 5\n")
    assert resolve_default_map(["--isolated"], _dummy_command) is None


def test_resolve_default_map_returns_none_without_pyproject(tmp_path: Path, monkeypatch):
    """Returns None when no pyproject.toml is discoverable."""
    monkeypatch.chdir(tmp_path)
    assert resolve_default_map([], _dummy_command) is None


def test_resolve_default_map_returns_none_for_empty_table(tmp_path: Path, monkeypatch):
    """Returns None when [tool.markdown-checker] is present but empty."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text("[tool.markdown-checker]\n")
    assert resolve_default_map([], _dummy_command) is None


def test_resolve_default_map_normalizes_keys(tmp_path: Path, monkeypatch):
    """Normalizes hyphenated keys to underscored parameter names."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text("[tool.markdown-checker]\nskip-files = ['a.md']\ntimeout = 5\n")
    assert resolve_default_map([], _dummy_command) == {"skip_files": ["a.md"], "timeout": 5}


def test_resolve_default_map_uses_explicit_config_path(tmp_path: Path, monkeypatch):
    """Uses the file given via --config instead of discovery."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text("[tool.markdown-checker]\ntimeout = 999\n")
    custom = tmp_path / "custom.toml"
    custom.write_text("[tool.markdown-checker]\ntimeout = 7\n")
    assert resolve_default_map(["--config", str(custom)], _dummy_command) == {"timeout": 7}


def test_resolve_default_map_raises_for_unknown_key(tmp_path: Path, monkeypatch):
    """Raises click.UsageError when the config contains an unknown key."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text("[tool.markdown-checker]\ntimout = 5\n")
    with pytest.raises(click.UsageError):
        resolve_default_map([], _dummy_command)
