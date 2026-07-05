"""Click-based command-line entry point (the ``markdown-checker`` command)."""

import os
import platform
from pathlib import Path
from typing import Any

import click

from markdown_checker import __version__
from markdown_checker.checker import run_check_on_files
from markdown_checker.models.config import Config
from markdown_checker.reports import build_report
from markdown_checker.reports import get_renderer
from markdown_checker.reports import RENDERERS
from markdown_checker.reports import ReportContext
from markdown_checker.reports import ReportFormat
from markdown_checker.reports import write_report
from markdown_checker.reports.renderers.annotations import GitHubAnnotationsRenderer
from markdown_checker.reports.renderers.console import ConsoleRenderer
from markdown_checker.utils.github_env import get_github_repo_blob_url
from markdown_checker.utils.list_files import get_files_paths_list
from markdown_checker.utils.pyproject_config import resolve_default_map


class PyprojectCommand(click.Command):
    """Command that seeds ``ctx.default_map`` from ``[tool.markdown-checker]`` in pyproject.toml."""

    def make_context(
        self,
        info_name: str | None,
        args: list[str],
        parent: click.Context | None = None,
        **extra: Any,
    ) -> click.Context:
        if "default_map" not in extra:
            extra["default_map"] = resolve_default_map(args, self)
        return super().make_context(info_name, args, parent, **extra)


class ListOfStrings(click.Option):
    """
    Helper class to parse a comma-separated list of strings from the command line.

    Ref: https://stackoverflow.com/questions/47631914/how-to-pass-several-list-of-arguments-to-click-option
    """

    def type_cast_value(self, ctx, value) -> list[str]:  # type: ignore[no-untyped-def]
        try:
            if isinstance(value, str):
                return list(filter(None, value.split(",")))
            elif isinstance(value, list):
                return value
            else:
                raise Exception
        except Exception as err:
            raise click.BadParameter(str(value)) from err


@click.command(cls=PyprojectCommand)
@click.argument(
    "src",
    nargs=-1,
    type=click.Path(path_type=Path, exists=True, file_okay=True, dir_okay=True, readable=True),
    metavar="SRC ...",
    required=False,
)
@click.option(
    "-d",
    "--dir",
    type=click.Path(path_type=Path, exists=True, file_okay=False, dir_okay=True, readable=True),
    help="Path to the root directory to check.",
    required=False,
)
@click.option(
    "-f",
    "--func",
    type=click.Choice(
        [
            "check_broken_paths",
            "check_broken_urls",
            "check_paths_tracking",
            "check_urls_tracking",
            "check_urls_locale",
        ]
    ),
    help="Function to be executed.",
    required=True,
)
@click.option(
    "-ext",
    "--extensions",
    cls=ListOfStrings,
    type=list[str],
    default=[".md", ".ipynb"],
    help="File extensions to filter the files.",
    required=False,
)
@click.option(
    "-td",
    "--tracking-domains",
    cls=ListOfStrings,
    type=list[str],
    default=["github.com", "microsoft.com", "visualstudio.com", "aka.ms", "azure.com"],
    help="List of tracking domains to check.",
    required=False,
)
@click.option(
    "-sf",
    "--skip-files",
    cls=ListOfStrings,
    type=list[str],
    default=[
        "CODE_OF_CONDUCT.md",
        "SECURITY.md",
    ],
    help="List of file names to skip check.",
    required=False,
)
@click.option(
    "-sd",
    "--skip-domains",
    cls=ListOfStrings,
    type=list[str],
    default=[],
    help="List of domains to skip check.",
    required=False,
)
@click.option(
    "-suc",
    "--skip-urls-containing",
    cls=ListOfStrings,
    type=list[str],
    default=[],
    help="List of urls to skip check.",
    required=False,
)
@click.option(
    "-gu",
    "--guide-url",
    type=str,
    help="Full url of your contributing guide.",
    required=False,
)
@click.option(
    "-to",
    "--timeout",
    type=click.IntRange(0, 50),
    default=20,
    help="Timeout in seconds for the requests.",
    required=False,
)
@click.option(
    "-rt",
    "--retries",
    type=click.IntRange(0, 10),
    default=3,
    help="Number of retries for the requests.",
    required=False,
)
@click.option(
    "--retry-on-429/--no-retry-on-429",
    default=True,
    help="Honour Retry-After headers when a 429 response is received.",
)
@click.option(
    "-frd",
    "--fallback-retry-delay",
    type=click.IntRange(0, 300),
    default=30,
    help="Fallback delay in seconds when a 429 response has no Retry-After header.",
    required=False,
)
@click.option(
    "-mw",
    "--max-workers",
    type=click.IntRange(min=1),
    default=None,
    help="Maximum number of concurrent URL-check workers. Defaults to 10, "
    "or the number of available CPUs when running in GitHub Actions.",
    required=False,
)
@click.option(
    "-phd",
    "--per-host-delay",
    type=click.FloatRange(0.0, 10.0),
    default=0.5,
    help="Minimum delay in seconds between requests to the same host.",
    required=False,
)
@click.option(
    "-o",
    "--output-file-name",
    type=str,
    default="comment",
    help="Name of the output file, without extension. Use '-' to write to stdout.",
    required=False,
)
@click.option(
    "-rf",
    "--report-format",
    type=click.Choice(sorted(RENDERERS)),
    default="markdown",
    help="Report format to generate when errors are found.",
    required=False,
)
@click.option(
    "-c",
    "--config",
    "config_file",
    type=click.Path(path_type=Path, exists=True, dir_okay=False, readable=True),
    expose_value=False,
    is_eager=True,
    help="TOML file to read [tool.markdown-checker] configuration from, instead of discovering pyproject.toml.",
)
@click.option(
    "--isolated",
    is_flag=True,
    expose_value=False,
    is_eager=True,
    help="Ignore pyproject.toml configuration entirely.",
)
@click.version_option(
    version=__version__,
    message=(
        f"%(prog)s, %(version)s\n"
        f"Python ({platform.python_implementation()}) {platform.python_version()} {platform.architecture()[0]}\n"
        f"{platform.system()} {platform.release()}"
    ),
)
@click.pass_context
def main(
    ctx: click.Context,
    src: tuple[Path, ...],
    dir: Path | None,
    func: str,
    guide_url: str | None,
    extensions: list[str],
    skip_files: list[str],
    skip_domains: list[str],
    skip_urls_containing: list[str],
    tracking_domains: list[str],
    timeout: int,
    retries: int,
    retry_on_429: bool,
    fallback_retry_delay: int,
    max_workers: int | None,
    per_host_delay: float,
    output_file_name: str,
    report_format: ReportFormat,
) -> None:
    """A markdown link validation reporting tool.

    Validates the markdown/notebook files under SRC (one or more files or
    directories) or --dir, using the check selected by --func:
    ``check_broken_paths``, ``check_broken_urls``, ``check_paths_tracking``,
    ``check_urls_tracking``, or ``check_urls_locale``.

    When issues are found, error-level issues are written as a report (see
    --report-format and --output-file-name) and the command exits with
    status 1; warning-level issues (e.g. rate-limited or unverifiable URLs)
    are printed but never fail the run. With no issues, it exits 0.

    Every option may also be set in a ``[tool.markdown-checker]`` table in
    pyproject.toml (see --config/--isolated); command-line values always
    take precedence.
    """
    if max_workers is None:
        if os.getenv("GITHUB_ACTIONS") == "true":
            max_workers = max(1, os.cpu_count() or 10)
        else:
            max_workers = 10

    if src:
        files_paths = []
        for p in src:
            if p.is_dir():
                _, dir_files = get_files_paths_list(p, extensions)
                files_paths.extend(dir_files)
            elif p.suffix.lower() in extensions:
                files_paths.append(p)
    elif dir is not None:
        _, files_paths = get_files_paths_list(dir, extensions)
    else:
        raise click.UsageError("Either SRC or --dir must be provided.")

    # remove files from skip_files list
    files_paths = [file_path for file_path in files_paths if file_path.name not in skip_files]

    config = Config(
        skip_domains=skip_domains,
        skip_urls_containing=skip_urls_containing,
        tracking_domains=tracking_domains,
        timeout=timeout,
        retries=retries,
        retry_on_429=retry_on_429,
        fallback_retry_delay=fallback_retry_delay,
        max_workers=max_workers,
        per_host_delay=per_host_delay,
        output_mode="ci" if os.getenv("CI", "false") == "true" else "local",
    )
    repo_url = get_github_repo_blob_url() if config.output_mode == "ci" else None

    with click.progressbar(length=len(files_paths), label="Checking", hidden=config.output_mode == "ci") as bar:
        check_result = run_check_on_files(
            func=func,
            files_paths=files_paths,
            config=config,
            progress_callback=lambda: bar.update(1),
        )

    click.echo(
        click.style(f"\n🔍 Checked {check_result.links_checked} links in {len(files_paths)} files.", fg="blue"),
        err=False,
    )

    if check_result.issues:
        report_context = ReportContext(
            check_name=func,
            output_mode=config.output_mode,
            repo_url=repo_url,
            guide_url=guide_url,
            tool_version=__version__,
        )
        report = build_report(check_result, context=report_context, files_checked=len(files_paths))

        if report.has_errors:
            renderer = get_renderer(report_format)
            out_path = None if output_file_name == "-" else Path(f"{output_file_name}{renderer.file_extension}")
            write_report(renderer.render(report), output_path=out_path)
            click.echo(click.style(f"😭 Found {report.error_count} issues in the following files:", fg="red"), err=True)

        if report.has_warnings:
            click.echo(
                click.style(f"⚠ {report.warning_count} links had warnings:", fg="yellow"),
                err=True,
            )

        terminal_renderer = GitHubAnnotationsRenderer() if config.output_mode == "ci" else ConsoleRenderer()
        for message, level in terminal_renderer.render_lines(report):
            click.echo(click.style(message, fg="yellow" if level == "warning" else "red"), err=True)

        ctx.exit(1 if report.has_errors else 0)

    click.echo(click.style("All files are compliant with the guidelines. 🎉", fg="green"), err=False)
    ctx.exit(0)
