[![PyPi](https://img.shields.io/pypi/v/markdown-checker)](https://pypi.org/project/markdown-checker/)
[![Documentation Status](https://readthedocs.org/projects/markdown-checker/badge/?version=latest)](https://markdown-checker.readthedocs.io/en/latest/?badge=latest)
[![Downloads](https://img.shields.io/pypi/dm/markdown-checker)](https://pypi.org/project/markdown-checker/)

[![GitHub issues](https://img.shields.io/badge/issue_tracking-github-blue.svg)](https://github.com/john0isaac/markdown-checker/issues)
[![Contributing](https://img.shields.io/badge/PR-Welcome-%23FF8300.svg?)](https://github.com/john0isaac/markdown-checker/pulls)

markdown-checker is a markdown link validation reporting tool. It provides a couple of functions to validate relative paths and web URLs.

[test](./sdvjn.md)

## Installation

Install the package:

```bash
pip install markdown-checker
```

### Documentation

- [Full documentation](https://markdown-checker.readthedocs.io/en/latest/).

## 1, 2, 3 - How To

1. Run `pip install markdown-checker`.
2. Run `markdown-checker -d {src} -f {func} -gu {url}`. Replace `{src}` with the directory you want to analyze, `{func}` with the available functions like `check_broken_paths`, `{gu}` with your contribution guidance full URL.
3. The output will be displayed in the terminal and in a `comments.md` file.

For more customizations read the docs.

## Using `markdown-checker` in GitHub Actions

You can run this tool within a GitHub workflow using the [action-check-markdown](https://github.com/marketplace/actions/check-markdown) GitHub action.

The action will automatically post the output of the tool to your GitHub pull request as a comment.

# Usage

The library provides the following functions:

- [Usage](#usage)
  - [`check_broken_paths`](#check_broken_paths)
  - [`check_broken_urls`](#check_broken_urls)
  - [`check_urls_locale`](#check_urls_locale)
  - [`check_paths_tracking`](#check_paths_tracking)
  - [`check_urls_tracking`](#check_urls_tracking)

## `check_broken_paths`

This function ensures that any relative path in your files are working.

Example:

```bash
markdown-checker -d . -f check_broken_paths -gu https://github.com/john0isaac/markdown-checker/blob/main/CONTRIBUTING.md
```

## `check_broken_urls`

This function ensures that any web URL in your files is working and returning 200 status code.

Example:

```bash
markdown-checker -d . -f check_broken_urls -gu https://github.com/john0isaac/markdown-checker/blob/main/CONTRIBUTING.md
```

## `check_urls_locale`

This function checks if country specific locale is present in URLs.

Example:

```bash
markdown-checker -d . -f check_urls_locale -gu https://github.com/john0isaac/markdown-checker/blob/main/CONTRIBUTING.md
```

## `check_paths_tracking`

This function ensures that any relative path has tracking in it.

Example:

```bash
markdown-checker -d . -f check_paths_tracking -gu https://github.com/john0isaac/markdown-checker/blob/main/CONTRIBUTING.md
```

## `check_urls_tracking`

This function ensures that any URL has tracking in it.

Example:

```bash
markdown-checker -d . -f check_urls_tracking -gu https://github.com/john0isaac/markdown-checker/blob/main/CONTRIBUTING.md
```
