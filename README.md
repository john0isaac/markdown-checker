# markdown-checker

A Markdown Validation Reporting Tool.

# How To
1. Run `pip install markdown-checker`.
2. Run `markdown-checker -d {src} -f {func}`. Replace `{src}` with the directory you want to analyse and {func} with the available functions like check_broken_paths.
3. The output will be displayed in the terminal.

# Using markdown-checker in GitHub Actions
The tool has been designed to be run within a GitHub workflow using the [action-check-markdown](https://github.com/marketplace/actions/action-check-markdown) GitHub action. The action will automatically post the output of the tool to your GitHub pull request as a comment.
