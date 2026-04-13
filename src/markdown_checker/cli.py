import os
import platform
import sys
from pathlib import Path

import click

from markdown_checker.checker import detect_issues
from markdown_checker.models.base import MarkdownLinkBase
from markdown_checker.reports.markdown import MarkdownGenerator
from markdown_checker.utils.format_output import format_links
from markdown_checker.utils.list_files import get_files_paths_list
from markdown_checker.utils.spinner import spinner


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
        except Exception:
            raise click.BadParameter(str(value))


@click.command()
@click.option(
    "-d",
    "--dir",
    type=click.Path(path_type=Path, exists=True, file_okay=False, dir_okay=True, readable=True),
    help="Path to the root directory to check.",
    required=True,
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
    default=["https://www.microsoft.com/en-us/security/blog", "video-embed.html"],
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
    default=15,
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
    "-o",
    "--output-file-name",
    type=str,
    default="comment",
    help="Name of the output file.",
    required=False,
)
@click.argument(
    "src",
    nargs=-1,
    type=click.Path(path_type=Path, exists=True, file_okay=True, dir_okay=True, readable=True),
    is_eager=True,
    metavar="SRC ...",
    required=False,
)
@click.version_option(
    message=(f"%(prog)s, %(version)s\nPython ({platform.python_implementation()}) {platform.python_version()}"),
)
def main(
    src: tuple[Path, ...],
    dir: Path,
    func: str,
    guide_url: str | None,
    extensions: list[str],
    skip_files: list[str],
    skip_domains: list[str],
    skip_urls_containing: list[str],
    tracking_domains: list[str],
    timeout: int,
    retries: int,
    output_file_name: str,
) -> None:
    """A markdown link validation reporting tool."""
    _ = src or (Path("./"),)  # default to current directory
    _, files_paths = get_files_paths_list(dir, extensions)

    # remove files from skip_files list
    files_paths = [file_path for file_path in files_paths if file_path.name not in skip_files]

    formatted_output = ""
    all_files_issues: list[MarkdownLinkBase] = []
    links_checked_count = 0
    github_ci = os.getenv("CI", "false")

    for file_path in files_paths:
        detected_issues, links_count = detect_issues(
            func=func,
            file_path=file_path,
            skip_urls_containing=skip_urls_containing,
            skip_domains=skip_domains,
            tracking_domains=tracking_domains,
            timeout=timeout,
            retries=retries,
        )
        links_checked_count += links_count
        if len(detected_issues) > 0:
            if github_ci == "true":
                formatted_output += f"| `{file_path}` |" + format_links(detected_issues)
            else:
                formatted_output += f"| [`{file_path}`]({file_path}) |" + format_links(detected_issues)
            all_files_issues.extend(detected_issues)

    click.echo(
        click.style(f"\n🔍 Checked {links_checked_count} links in {len(files_paths)} files.", fg="blue"), err=False
    )

    if len(all_files_issues) > 0:
        formatted_output = "| File Full Path | Issues |\n|--------|--------|\n" + formatted_output
        generator = MarkdownGenerator(contributing_guide_url=guide_url, output_file_name=output_file_name)
        generator.generate(func, formatted_output)
        click.echo(click.style(f"😭 Found {len(all_files_issues)} issues in the following files:", fg="red"), err=True)
        for markdown_path in all_files_issues:
            if github_ci == "true":
                # Ref: https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/workflow-commands-for-github-actions#setting-a-warning-message
                click.echo(
                    click.style(
                        f"::error file={markdown_path.file_path},line={markdown_path.line_number}::"
                        f"File {markdown_path.file_path}, line {markdown_path.line_number}, "
                        f"Link {markdown_path} {markdown_path.issue}.",
                        fg="red",
                    ),
                    err=True,
                )
            else:
                click.echo(
                    click.style(
                        f"\tFile '{markdown_path.file_path.resolve()}', line {markdown_path.line_number}"
                        f"\n{markdown_path} {markdown_path.issue}.\n",
                        fg="red",
                    ),
                    err=True,
                )
        sys.exit(1)

    click.echo(click.style("All files are compliant with the guidelines. 🎉", fg="green"), err=False)
    sys.exit(0)


def main_with_spinner() -> None:
    with spinner():
        main()
