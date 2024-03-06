"""
Module to check paths in markdown files.
"""

import subprocess


def check_broken_paths():
    """
    Function to check for broken paths.
    """
    print("check_broken_paths was called")
    subprocess.run(
        [
            "markdown-checker",
            "-d",
            "./tests/resources/",
            "-f",
            "check_broken_paths",
            "-gu",
            "https://github.com/john0isaac/markdown-checker/blob/main/CONTRIBUTING.md",
        ],
        check=False,
    )


def check_broken_urls():
    """
    Function to check for broken paths.
    """
    print("check_broken_urls was called")
    subprocess.run(
        [
            "markdown-checker",
            "-d",
            "./tests/resources/",
            "-f",
            "check_broken_urls",
            "-gu",
            "https://github.com/john0isaac/markdown-checker/blob/main/CONTRIBUTING.md",
        ],
        check=False,
    )


def check_paths_tracking():
    """
    Function to check paths tracking.
    """
    print("check_paths_tracking was called")
    subprocess.run(
        [
            "markdown-checker",
            "-d",
            "./tests/resources/",
            "-f",
            "check_paths_tracking",
            "-gu",
            "https://github.com/john0isaac/markdown-checker/blob/main/CONTRIBUTING.md",
        ],
        check=False,
    )


def check_urls_tracking():
    """
    Function to check URLs tracking.
    """
    print("check_urls_tracking was called")
    subprocess.run(
        [
            "markdown-checker",
            "-d",
            "./tests/resources/",
            "-f",
            "check_urls_tracking",
            "-gu",
            "https://github.com/john0isaac/markdown-checker/blob/main/CONTRIBUTING.md",
        ],
        check=False,
    )


def check_urls_locale():
    """
    Function to check URLs locale.
    """
    print("check_urls_locale was called")
    subprocess.run(
        [
            "markdown-checker",
            "-d",
            "./tests/resources/",
            "-f",
            "check_urls_locale",
            "-gu",
            "https://github.com/john0isaac/markdown-checker/blob/main/CONTRIBUTING.md",
        ],
        check=False,
    )


mydict = {
    1: check_broken_paths,
    2: check_broken_urls,
    3: check_paths_tracking,
    4: check_urls_tracking,
    5: check_urls_locale,
}

try:
    choices = list(
        map(
            int,
            input(
                "Do you want to: \n(1) Run check_broken_paths \n(2) Run check_broken_urls \n(3) Run check_paths_tracking \n(4) Run check_urls_tracking \n(5) Run check_urls_locale \n"
            ).split(),
        )
    )
except ValueError:
    print("Please input number")

for choice in choices:
    if 0 < choice and choice < 6:
        mydict[choice]()
    else:
        print("That is not between 1 and 5! Try again:")
