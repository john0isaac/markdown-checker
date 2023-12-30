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
