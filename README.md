[![PyPi](https://img.shields.io/pypi/v/markdown-checker)](https://pypi.org/project/markdown-checker/)
[![Downloads](https://img.shields.io/pypi/dm/markdown-checker)](https://pypi.org/project/markdown-checker/)

[![GitHub issues](https://img.shields.io/badge/issue_tracking-github-blue.svg)](https://github.com/john0isaac/markdown-checker/issues)
[![Contributing](https://img.shields.io/badge/PR-Welcome-%23FF8300.svg?)](https://github.com/john0isaac/markdown-checker/pulls)

markdown-checker is a markdown validation reporting tool.

# How To

1. Run `pip install markdown-checker`.
2. Run `markdown-checker -d {src} -f {func} -gu {url}`. Replace `{src}` with the directory you want to analyze, {func} with the available functions like check_broken_paths, {gu} with your contribution guidance full URL.
3. The output will be displayed in the terminal and in a `comments.md` file.

# Using markdown-checker in GitHub Actions

The tool has been designed to be run within a GitHub workflow using the [action-check-markdown](https://github.com/marketplace/actions/check-markdown) GitHub action. The action will automatically post the output of the tool to your GitHub pull request as a comment.

# Supported Functions

## Check broken relative paths
This function ensures that any relative path in your files is working.

Example:

```bash
markdown-checker -d . -f check_broken_paths -gu https://github.com/john0isaac/markdown-checker/blob/main/CONTRIBUTING.md
```

## Check broken URLs
This function ensures that any web URL in your files is working and returning 200 status code.

Example:

```bash
markdown-checker -d . -f check_broken_urls -gu https://github.com/john0isaac/markdown-checker/blob/main/CONTRIBUTING.md
```

## Check country locale present in URLs
This function ensures that any relative path in your files is working.

Example:

```bash
markdown-checker -d . -f check_urls_locale -gu https://github.com/john0isaac/markdown-checker/blob/main/CONTRIBUTING.md
```

## Check Contributor ID missing from paths
This function ensures that any relative path has tracking in it.

Example:

```bash
markdown-checker -d . -f check_paths_tracking -gu https://github.com/john0isaac/markdown-checker/blob/main/CONTRIBUTING.md
```

## Check Contributor ID missing from URLs
This function ensures that any URL has tracking in it.

Example:

```bash
markdown-checker -d . -f check_urls_tracking -gu https://github.com/john0isaac/markdown-checker/blob/main/CONTRIBUTING.md
```
