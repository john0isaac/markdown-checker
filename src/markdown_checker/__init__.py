#!/usr/bin/env python3
"""
Module providing automatic checks functionality to markdown files
following some Guidelines
"""

import concurrent.futures
import os
import platform
import sys
from pathlib import Path
from typing import Union

import click

from markdown_checker.paths import MarkdownPath
from markdown_checker.reports.md_reports.generator import MarkdownGenerator
from markdown_checker.urls import MarkdownURL
from markdown_checker.utils.extract_links import get_links_from_md_file
from markdown_checker.utils.format_output import format_links
from markdown_checker.utils.list_files import get_files_paths_list
from markdown_checker.utils.spinner import spinner


def check_url(url: MarkdownURL, skip_domains: list[str], skip_urls_containing: list[str], timeout: int, retries: int):
    if any(url.host_name().lower() in domain.lower() for domain in skip_domains) or any(
        url.link in substring for substring in skip_urls_containing
    ):
        return None
    if not url.is_alive(timeout=timeout, retries=retries):
        url.issue = "is broken"
        return url
    return None


def detect_issues(
    func: str,
    file_path: Path,
    skip_urls_containing: list[str],
    skip_domains: list[str],
    tracking_domains: list[str],
    timeout: int,
    retries: int,
) -> tuple[list[Union[MarkdownPath, MarkdownURL]], int]:
    """
    Function to detect issues in the markdown file based on the function

    Args:
        func (str): Function to be executed
        file_path (Path): Path to the markdown file
        skip_urls_containing (list[str]): List of urls to skip check
        skip_domains (list[str]): List of domains to skip check
        tracking_domains (list[str]): List of tracking domains to check
        timeout (int): Timeout in seconds for the requests
        retries (int): Number of retries for the requests

    Returns:
        Detected issues and links count.
    """
    detected_issues: list[Union[MarkdownPath, MarkdownURL]] = []
    links_count = 0
    # Step 1: Extract all Links from file path
    all_links = get_links_from_md_file(file_path)
    if len(all_links.paths) == 0 and len(all_links.urls) == 0:
        return detected_issues, links_count
    # Step 2: Check for issues based on the function
    if func == "check_broken_paths":
        for path in all_links.paths:
            if not path.exists():
                path.issue = "is broken"
                detected_issues.append(path)
        links_count += len(all_links.paths)
    elif func == "check_broken_urls":
        # currently these domains are known to have restrictions on the requests
        skip_domains.extend(
            [
                "platform.openai.com",
                "help.openai.com",
                "beta.openai.com",
                "marketplace.visualstudio.com",
                "huggingface.co",
                "en.wikipedia.org",
                "twitter.com",
                "www.linkedin.com",
                "make.powerautomate.com",
                "make.powerapps.com",
                "www.midjourney.com",
                "vscode.dev",
                "rodtrent.substack.com",
                "example.com",
                "www.nuget.org",
                "www.docker.com",
                "build.nvidia.com",
                "dotnet.microsoft.com",
                "www.gemini.com",
                "upload.wikimedia.org",
            ]
        )
        with concurrent.futures.ProcessPoolExecutor() as executor:
            results = list(
                executor.map(
                    check_url,
                    all_links.urls,
                    [skip_domains] * len(all_links.urls),
                    [skip_urls_containing] * len(all_links.urls),
                    [timeout] * len(all_links.urls),
                    [retries] * len(all_links.urls),
                )
            )
        detected_issues.extend(filter(None, results))
        links_count += len(all_links.urls)
    elif func == "check_urls_tracking":
        for url in all_links.urls:
            if any(url.host_name().lower() in domain.lower() for domain in skip_domains) or any(
                url.link in substring for substring in skip_urls_containing
            ):
                continue
            if any(url.host_name().lower() in domain.lower() for domain in tracking_domains) and not url.has_tracking():
                url.issue = "is missing tracking id"
                detected_issues.append(url)
        links_count += len(all_links.urls)
    elif func == "check_paths_tracking":
        for path in all_links.paths:
            if not path.has_tracking():
                path.issue = "is missing tracking id"
                detected_issues.append(path)
        links_count += len(all_links.paths)
    elif func == "check_urls_locale":
        # if you remove locale from these domains, it will fail
        skip_domains.extend(
            [
                "www.nvidia.com",
            ]
        )
        for url in all_links.urls:
            if any(url.host_name().lower() in domain.lower() for domain in skip_domains) or any(
                url.link in substring for substring in skip_urls_containing
            ):
                continue
            if url.has_locale():
                url.issue = "has locale"
                detected_issues.append(url)
        links_count += len(all_links.urls)
    elif func == "check_paths_locale":
        for path in all_links.paths:
            if path.has_locale():
                path.issue = "has locale"
                detected_issues.append(path)
        links_count += len(all_links.paths)
    return detected_issues, links_count


@click.command()
@click.option(
    "-d",
    "--dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True),
    help="Path to the root directory to check.",
    required=True,
)
@click.option(
    "-ext",
    "--extensions",
    type=list[str],
    default=[".md", ".ipynb"],
    help="File extensions to filter the files.",
    required=True,
)
@click.option(
    "-td",
    "--tracking-domains",
    type=list[str],
    default=["github.com", "microsoft.com", "visualstudio.com", "aka.ms", "azure.com"],
    help="List of tracking domains to check.",
    required=True,
)
@click.option(
    "-sf",
    "--skip-files",
    type=list[str],
    default=[
        "CODE_OF_CONDUCT.md",
        "SECURITY.md",
    ],
    help="List of file names to skip check.",
    required=True,
)
@click.option(
    "-sd",
    "--skip-domains",
    type=list[str],
    default=[],
    help="List of domains to skip check.",
    required=False,
)
@click.option(
    "-suc",
    "--skip-urls-containing",
    type=list[str],
    default=["https://www.microsoft.com/en-us/security/blog", "video-embed.html"],
    help="List of urls to skip check.",
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
    "-gu",
    "--guide-url",
    type=str,
    help="Full url of your contributing guide.",
    required=True,
)
@click.option(
    "-to",
    "--timeout",
    type=int,
    default=10,
    help="Timeout in seconds for the requests.",
    required=False,
)
@click.option(
    "-rt",
    "--retries",
    type=int,
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
    required=True,
)
@click.argument(
    "src",
    nargs=-1,
    type=click.Path(exists=True, file_okay=True, dir_okay=True, readable=True),
    is_eager=True,
    metavar="SRC ...",
    required=False,
)
@click.version_option(
    message=(f"%(prog)s, %(version)s\n" f"Python ({platform.python_implementation()}) {platform.python_version()}"),
)
def main(
    src: tuple[str, ...],
    dir: str,
    func: str,
    guide_url: str,
    extensions: list[str],
    skip_files: list[str],
    skip_domains: list[str],
    skip_urls_containing: list[str],
    timeout: int,
    retries: int,
    tracking_domains: list[str],
    output_file_name: str,
) -> None:
    """A markdown link validation reporting tool."""
    _ = tuple(Path(item) for item in src) or (Path("./"),)  # default to current directory

    _, files_paths = get_files_paths_list(Path(dir), extensions)

    # remove files from skip_files list
    files_paths = [file_path for file_path in files_paths if file_path.name not in skip_files]

    formatted_output = ""
    all_files_issues: list[Union[MarkdownPath, MarkdownURL]] = []
    links_checked_count = 0

    # iterate over the files to validate the content
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
            github_ci = os.getenv("CI", "false")
            if github_ci == "true":
                click.echo(
                    click.style(
                        f"Error: {markdown_path.file_path}:{markdown_path.line_number} "
                        f"Link {markdown_path} {markdown_path.issue}.",
                        fg="red",
                    ),
                    err=True,
                )
                return
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
