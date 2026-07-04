import os
import platform
from pathlib import Path

import click

from markdown_checker.checker import run_check_on_files
from markdown_checker.models.config import Config
from markdown_checker.reports.format_output import format_issues_table
from markdown_checker.reports.markdown import MarkdownGenerator
from markdown_checker.utils.github_env import get_github_repo_blob_url
from markdown_checker.utils.list_files import get_files_paths_list


class ListOfStrings(click.Option):
    """
    Helper class to parse a comma-separated list of strings from the command line.

    Ref: https://stackoverflow.com/questions/47631914/how-to-pass-several-list-of-arguments-to-click-option
    """

    def type_cast_value(self, ctx, value) -> list[str]:  # type: ignore
        try:
            if isinstance(value, str):
                return list(filter(None, value.split(",")))
            elif isinstance(value, list):
                return value
            else:
                raise Exception
        except Exception as err:
            raise click.BadParameter(str(value)) from err


@click.command()
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
    help="Name of the output file.",
    required=False,
)
@click.version_option(
    message=(f"%(prog)s, %(version)s\nPython ({platform.python_implementation()}) {platform.python_version()}"),
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
) -> None:
    """A markdown link validation reporting tool."""
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
        error_by_file = []
        rendered_issues = []
        error_count = 0
        warning_count = 0

        for path, issues in check_result.issues:
            file_errors = []
            resolved_path = path.resolve() if config.output_mode == "local" else None
            for issue in issues:
                is_warning = issue.issue_level == "warning"
                if issue.issue_level == "error":
                    error_count += 1
                    file_errors.append(issue)
                else:
                    warning_count += 1
                if config.output_mode == "ci":
                    level = "warning" if is_warning else "error"
                    rendered_issues.append(
                        (
                            f"::{level} file={issue.file_path},line={issue.line_number}::"
                            f"File {issue.file_path}, line {issue.line_number}, "
                            f"Link {issue} {issue.issue}.",
                            "yellow" if is_warning else "red",
                        )
                    )
                else:
                    rendered_issues.append(
                        (
                            f"\tFile '{resolved_path}', line {issue.line_number}\n{issue} {issue.issue}.\n",
                            "yellow" if is_warning else "red",
                        )
                    )
            if file_errors:
                error_by_file.append((path, file_errors))

        if error_count:
            formatted_output = format_issues_table(error_by_file, config.output_mode, repo_url)
            generator = MarkdownGenerator(contributing_guide_url=guide_url, output_file_name=output_file_name)
            generator.generate(func, formatted_output)
            click.echo(click.style(f"😭 Found {error_count} issues in the following files:", fg="red"), err=True)

        if warning_count:
            click.echo(
                click.style(f"⚠ {warning_count} links had warnings:", fg="yellow"),
                err=True,
            )

        for message, color in rendered_issues:
            click.echo(click.style(message, fg=color), err=True)

        ctx.exit(1 if error_count else 0)

    click.echo(click.style("All files are compliant with the guidelines. 🎉", fg="green"), err=False)
    ctx.exit(0)
