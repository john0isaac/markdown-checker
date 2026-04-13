from pathlib import Path

import click
import pytest
from click.testing import CliRunner

from markdown_checker.cli import ListOfStrings, main


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def resources_dir():
    return Path(__file__).parent / "resources"


# --- ListOfStrings ---


def test_list_of_strings_parses_csv():
    """Parses comma-separated values into a list."""
    opt = ListOfStrings(["-t", "--test"], type=list[str])
    result = opt.type_cast_value(None, "a,b,c")
    assert result == ["a", "b", "c"]


def test_list_of_strings_handles_list_input():
    """Returns list input as-is."""
    opt = ListOfStrings(["-t", "--test"], type=list[str])
    result = opt.type_cast_value(None, ["a", "b"])
    assert result == ["a", "b"]


def test_list_of_strings_filters_empty():
    """Filters out empty strings from CSV."""
    opt = ListOfStrings(["-t", "--test"], type=list[str])
    result = opt.type_cast_value(None, "a,,b,")
    assert result == ["a", "b"]


def test_list_of_strings_invalid_type_raises():
    """Raises BadParameter for non-string non-list input."""
    opt = ListOfStrings(["-t", "--test"], type=list[str])
    with pytest.raises(click.BadParameter):
        opt.type_cast_value(None, 12345)


# --- CLI main ---


def test_cli_check_broken_paths(runner, resources_dir):
    """Runs check_broken_paths on test resources without crashing."""
    result = runner.invoke(main, ["-d", str(resources_dir), "-f", "check_broken_paths"])
    assert result.exit_code == 0
    assert "Checked" in result.output


def test_cli_check_urls_tracking(runner, resources_dir, tmp_path, monkeypatch):
    """Runs check_urls_tracking on test resources without crashing."""
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(main, ["-d", str(resources_dir), "-f", "check_urls_tracking"])
    # exit code 1 is expected when issues are found (sample files have URLs without tracking IDs)
    assert result.exit_code in (0, 1)
    assert "Checked" in result.output


def test_cli_check_urls_locale(runner, resources_dir):
    """Runs check_urls_locale on test resources."""
    result = runner.invoke(main, ["-d", str(resources_dir), "-f", "check_urls_locale"])
    assert result.exit_code == 0
    assert "Checked" in result.output


def test_cli_check_paths_tracking(runner, resources_dir):
    """Runs check_paths_tracking on test resources."""
    result = runner.invoke(main, ["-d", str(resources_dir), "-f", "check_paths_tracking"])
    assert result.exit_code == 0
    assert "Checked" in result.output


def test_cli_missing_dir(runner):
    """Fails with error when --dir is missing."""
    result = runner.invoke(main, ["-f", "check_broken_paths"])
    assert result.exit_code != 0


def test_cli_invalid_func(runner, resources_dir):
    """Fails with error when --func is invalid."""
    result = runner.invoke(main, ["-d", str(resources_dir), "-f", "nonexistent"])
    assert result.exit_code != 0


def test_cli_custom_extensions(runner, resources_dir):
    """Runs with custom extensions filter."""
    result = runner.invoke(main, ["-d", str(resources_dir), "-f", "check_broken_paths", "-ext", ".md"])
    assert result.exit_code == 0


def test_cli_skip_files(runner, resources_dir):
    """Runs with skip-files option."""
    result = runner.invoke(main, ["-d", str(resources_dir), "-f", "check_broken_paths", "-sf", "sample1.md"])
    assert result.exit_code == 0


def test_cli_custom_timeout(runner, resources_dir):
    """Runs with custom timeout value."""
    result = runner.invoke(main, ["-d", str(resources_dir), "-f", "check_broken_paths", "-to", "5"])
    assert result.exit_code == 0


def test_cli_custom_retries(runner, resources_dir):
    """Runs with custom retries value."""
    result = runner.invoke(main, ["-d", str(resources_dir), "-f", "check_broken_paths", "-rt", "1"])
    assert result.exit_code == 0


def test_cli_guide_url(runner, resources_dir, tmp_path, monkeypatch):
    """Runs with guide URL and output file name options."""
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(
        main,
        [
            "-d",
            str(resources_dir),
            "-f",
            "check_broken_paths",
            "-gu",
            "https://example.com/CONTRIBUTING.md",
            "-o",
            str(tmp_path / "test_output"),
        ],
    )
    assert result.exit_code == 0


def test_cli_version(runner):
    """Displays version information."""
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "1.0.0" in result.output


def test_cli_ci_mode(runner, resources_dir, monkeypatch, tmp_path):
    """In CI mode, file paths are formatted differently."""
    monkeypatch.setenv("CI", "true")
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(
        main,
        ["-d", str(resources_dir), "-f", "check_broken_paths", "-o", str(tmp_path / "ci_output")],
    )
    assert result.exit_code == 0
