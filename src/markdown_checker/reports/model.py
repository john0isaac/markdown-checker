"""
Format-agnostic report model.

`Report` (and the `ReportIssue` / `FileReport` / `ReportContext` types it is
made of) is the single pivot between the check-running tool and report
rendering: `build_report()` is the only place that converts tool-specific
`CheckResult` data into this structure, and every renderer consumes only
`Report` from here on.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from markdown_checker.checker import CheckResult

Level = Literal["error", "warning"]
ReportFormat = Literal["markdown", "json", "github-annotations", "console"]


@dataclass(frozen=True, slots=True)
class ReportIssue:
    """A single finding, decoupled from the runtime `MarkdownLinkBase` object."""

    link: str
    line_number: int
    file_path: Path
    message: str
    level: Level


@dataclass(frozen=True, slots=True)
class FileReport:
    """All findings for one file, pre-split by level."""

    file_path: Path
    errors: tuple[ReportIssue, ...] = ()
    warnings: tuple[ReportIssue, ...] = ()


@dataclass(frozen=True, slots=True)
class ReportContext:
    """Run-level metadata that any renderer may use."""

    check_name: str
    output_mode: Literal["ci", "local"] = "local"
    repo_url: str | None = None
    guide_url: str | None = None
    tool_name: str = "markdown-checker"
    tool_version: str = ""


@dataclass(frozen=True, slots=True)
class Report:
    """A complete, format-agnostic report for a single check run."""

    context: ReportContext
    files: tuple[FileReport, ...] = ()
    links_checked: int = 0
    files_checked: int = 0

    @property
    def error_count(self) -> int:
        """Total number of error-level issues across all files."""
        return sum(len(file_report.errors) for file_report in self.files)

    @property
    def warning_count(self) -> int:
        """Total number of warning-level issues across all files."""
        return sum(len(file_report.warnings) for file_report in self.files)

    @property
    def has_errors(self) -> bool:
        """True if any file has at least one error-level issue."""
        return self.error_count > 0

    @property
    def has_warnings(self) -> bool:
        """True if any file has at least one warning-level issue."""
        return self.warning_count > 0


def build_report(
    check_result: "CheckResult",
    *,
    context: ReportContext,
    files_checked: int,
) -> Report:
    """
    Convert checker output (`CheckResult` of `MarkdownLinkBase` issues) into
    the format-agnostic `Report`.

    Args:
        check_result: The result returned by `run_check_on_files`.
        context: Run-level metadata to attach to the report.
        files_checked: Total number of files that were checked.

    Returns:
        A `Report` with issues split into errors/warnings per file.
    """
    files: list[FileReport] = []
    for file_path, issues in check_result.issues:
        errors = tuple(
            ReportIssue(
                link=issue.link,
                line_number=issue.line_number,
                file_path=issue.file_path,
                message=issue.issue,
                level="error",
            )
            for issue in issues
            if issue.issue_level == "error"
        )
        warnings = tuple(
            ReportIssue(
                link=issue.link,
                line_number=issue.line_number,
                file_path=issue.file_path,
                message=issue.issue,
                level="warning",
            )
            for issue in issues
            if issue.issue_level == "warning"
        )
        if errors or warnings:
            files.append(FileReport(file_path=file_path, errors=errors, warnings=warnings))

    return Report(
        context=context,
        files=tuple(files),
        links_checked=check_result.links_checked,
        files_checked=files_checked,
    )
