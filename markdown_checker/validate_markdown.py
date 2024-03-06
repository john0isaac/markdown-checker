#!/usr/bin/env python3
"""
Module providing automatic checks functionality to markdown files
following some Guidelines
"""

from markdown_checker.check_markdown import check_broken_links
from markdown_checker.generators.md_generator import generate_md
from markdown_checker.inputs.input_arguments import get_input_args
from markdown_checker.paths.files_paths_reader import get_files_paths_list


def main() -> None:
    """Main program get inputs and run checks"""

    # get input arguments directory, function to run
    in_arg = get_input_args()

    _, files_paths = get_files_paths_list(in_arg.dir)

    pass_list = [
        "./CODE_OF_CONDUCT.md",
        "./SECURITY.md",
        ".\CODE_OF_CONDUCT.md",
        ".\SECURITY.md",
    ]
    files_paths = [file_path for file_path in files_paths if file_path not in pass_list]

    formatted_output = ""

    # iterate over the files to validate the content
    for file_path in files_paths:
        if "check_broken_paths" in in_arg.func:
            broken_paths = check_broken_links(file_path, "path", "broken")
            if broken_paths:
                formatted_output += broken_paths
        if "check_paths_tracking" in in_arg.func:
            paths_tracking = check_broken_links(file_path, "path", "tracking")
            if paths_tracking:
                formatted_output += paths_tracking
        if "check_urls_tracking" in in_arg.func:
            urls_tracking = check_broken_links(file_path, "url", "tracking")
            if urls_tracking:
                formatted_output += urls_tracking
        if "check_urls_locale" in in_arg.func:
            urls_locale = check_broken_links(file_path, "url", "locale")
            if urls_locale:
                formatted_output += urls_locale
        if "check_broken_urls" in in_arg.func:
            broken_urls = check_broken_links(file_path, "url", "broken")
            if broken_urls:
                formatted_output += broken_urls
    if formatted_output != "":
        formatted_output = (
            "| File Full Path | Issues |\n|--------|--------|\n" + formatted_output
        )
        print(formatted_output)
        generate_md(formatted_output, in_arg.func, in_arg.guide_url)


if __name__ == "__main__":
    main()
