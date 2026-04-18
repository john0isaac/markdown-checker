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


# --- SRC positional argument ---


def test_cli_src_single_file(runner, resources_dir):
    """Runs check on a single file passed as SRC."""
    sample = resources_dir / "sample1.md"
    result = runner.invoke(main, [str(sample), "-f", "check_broken_paths"])
    assert result.exit_code == 0
    assert "Checked" in result.output
    assert "1 files" in result.output


def test_cli_src_multiple_files(runner, resources_dir):
    """Runs check on multiple files passed as SRC."""
    s1 = resources_dir / "sample1.md"
    s2 = resources_dir / "sample2.md"
    result = runner.invoke(main, [str(s1), str(s2), "-f", "check_broken_paths"])
    assert result.exit_code == 0
    assert "Checked" in result.output
    assert "2 files" in result.output


def test_cli_src_directory(runner, resources_dir):
    """Passing a directory as SRC recursively discovers files."""
    result = runner.invoke(main, [str(resources_dir), "-f", "check_broken_paths"])
    assert result.exit_code == 0
    assert "Checked" in result.output


def test_cli_src_mixed_file_and_dir(runner, resources_dir, tmp_path):
    """Passing both a file and a directory as SRC combines results."""
    extra = tmp_path / "extra.md"
    extra.write_text("# Extra\n[link](https://example.com)\n")
    result = runner.invoke(main, [str(extra), str(resources_dir), "-f", "check_broken_paths"])
    assert result.exit_code == 0
    assert "Checked" in result.output


def test_cli_src_filters_by_extension(runner, tmp_path):
    """SRC files not matching --extensions are ignored."""
    md_file = tmp_path / "valid.md"
    md_file.write_text("# Hello\n")
    txt_file = tmp_path / "ignored.txt"
    txt_file.write_text("# Not checked\n")
    result = runner.invoke(main, [str(md_file), str(txt_file), "-f", "check_broken_paths", "-ext", ".md"])
    assert result.exit_code == 0
    assert "1 files" in result.output


def test_cli_src_takes_precedence_over_dir(runner, resources_dir, tmp_path):
    """When SRC is provided, --dir is ignored."""
    sample = resources_dir / "sample1.md"
    result = runner.invoke(main, [str(sample), "-d", str(resources_dir), "-f", "check_broken_paths"])
    assert result.exit_code == 0
    assert "1 files" in result.output


def test_cli_no_src_no_dir_fails(runner):
    """Fails when neither SRC nor --dir is provided."""
    result = runner.invoke(main, ["-f", "check_broken_paths"])
    assert result.exit_code != 0
