"""
Module providing automatic checks functionality to markdown files
following some Guidelines
"""

import argparse


def get_input_args() -> argparse.Namespace:
    """
    Retrieves and parses the 2 command line arguments provided by the user when
    they run the program from a terminal window. This function uses Python's
    argparse module to created and defined these 2 command line arguments. If
    the user fails to provide some or all of the 2 arguments, then the default
    values are used for the missing arguments.
    Command Line Arguments:
      1. Tutorials Path as --dir
      2. Function to be executed as --func
    This function returns these arguments as an ArgumentParser object.
    Parameters:
     None - simply using argparse module to create & store command line arguments
    Returns:
     parse_args() -data structure that stores the command line arguments object
    """
    # Parse using ArgumentParser
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-d",
        "--dir",
        type=str,
        default="./",
        help="path to the root directory",
        required=True,
    )

    parser.add_argument(
        "-f",
        "--func",
        type=str,
        required=True,
        help="function to be executed",
        choices=[
            "check_broken_paths",
            "check_broken_urls",
            "check_paths_tracking",
            "check_urls_tracking",
            "check_urls_locale",
        ],
    )

    parser.add_argument(
        "-gu",
        "--guide-url",
        type=str,
        default="https://github.com/john0isaac/markdown-checker/blob/main/CONTRIBUTING.md",
        help="full url of your contributing guide",
        required=True,
    )

    return parser.parse_args()
