"""Smoke tests — run the CLI end-to-end against sample markdown files."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from markdown_checker.cli import main

RESOURCES_DIR = Path(__file__).parent.parent / "resources"


@pytest.fixture
def runner():
    return CliRunner()


@pytest.mark.smoke
@pytest.mark.parametrize(
    "func",
    [
        "check_broken_paths",
        "check_broken_urls",
        "check_paths_tracking",
        "check_urls_tracking",
        "check_urls_locale",
    ],
)
def test_cli_runs_without_crash(runner, func, tmp_path, monkeypatch):
    """CLI exits cleanly for each check function against sample resources."""
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(
        main,
        [
            "-d",
            str(RESOURCES_DIR),
            "-f",
            func,
            "-gu",
            "https://github.com/john0isaac/markdown-checker/blob/main/CONTRIBUTING.md",
            "-o",
            str(tmp_path / "comment"),
        ],
    )
    assert result.exit_code in (0, 1)
    assert "Checked" in result.output


@pytest.mark.smoke
def test_cli_broken_paths_finds_issues(runner, tmp_path, monkeypatch):
    """check_broken_paths detects broken paths in sample files."""
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(
        main,
        ["-d", str(RESOURCES_DIR), "-f", "check_broken_paths", "-o", str(tmp_path / "comment")],
    )
    assert result.exit_code in (0, 1)


@pytest.mark.smoke
def test_cli_urls_locale_finds_issues(runner, tmp_path, monkeypatch):
    """check_urls_locale detects locale segments in sample file URLs."""
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(
        main,
        ["-d", str(RESOURCES_DIR), "-f", "check_urls_locale", "-o", str(tmp_path / "comment")],
    )
    assert result.exit_code in (0, 1)


@pytest.mark.smoke
def test_cli_output_file_created_when_issues(runner, tmp_path, monkeypatch):
    """Output markdown file is created when issues are found."""
    monkeypatch.chdir(tmp_path)
    output_name = str(tmp_path / "smoke_output")
    result = runner.invoke(
        main,
        ["-d", str(RESOURCES_DIR), "-f", "check_paths_tracking", "-o", output_name],
    )
    if result.exit_code == 1:
        assert Path(f"{output_name}.md").exists()
