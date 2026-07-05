[![PyPi](https://img.shields.io/pypi/v/markdown-checker)](https://pypi.org/project/markdown-checker/)
[![Documentation Status](https://readthedocs.org/projects/markdown-checker/badge/?version=latest)](https://markdown-checker.readthedocs.io/en/latest/?badge=latest)
[![Downloads](https://img.shields.io/pypi/dm/markdown-checker)](https://pypi.org/project/markdown-checker/)

[![GitHub issues](https://img.shields.io/badge/issue_tracking-github-blue.svg)](https://github.com/john0isaac/markdown-checker/issues)
[![Contributing](https://img.shields.io/badge/PR-Welcome-%23FF8300.svg?)](https://github.com/john0isaac/markdown-checker/pulls)

markdown-checker is a markdown link validation reporting tool for `.md` and
`.ipynb` files. It flags broken relative paths, broken web URLs, missing
locale segments, and missing tracking IDs, then writes the findings as a
report your CI can post back to a pull request.

## Features

- Five built-in checks: broken relative paths, broken web URLs, locale
  segments in URLs, and tracking IDs on URLs and paths.
- Concurrent URL checking with cross-file deduplication, per-host rate
  pacing, and `Retry-After`/429 handling, so large repositories don't
  trip host rate limits.
- Four report formats: `markdown`, `json`, `github-annotations`, and
  `console`.
- Error vs. warning severity - rate-limited or unverifiable links are
  reported but never fail your CI.
- Configuration via a `[tool.markdown-checker]` table in `pyproject.toml`,
  so you don't have to repeat flags in every command or workflow file.

## Installation

```bash
pip install markdown-checker
```

## Quickstart

```bash
markdown-checker . -f check_broken_paths
```

```text
🔍 Checked 42 links in 10 files.
All files are compliant with the guidelines. 🎉
```

When issues are found, a `comment.md` report is written and the command
exits with a non-zero status:

```text
🔍 Checked 42 links in 10 files.
😭 Found 1 issues in the following files:
    File 'docs/index.md', line 5
./missing.md is broken.
```

## Using `markdown-checker` in GitHub Actions

Run this tool within a GitHub workflow using the
[action-check-markdown](https://github.com/marketplace/actions/check-markdown)
GitHub Action, which posts the report as a pull request comment:

```yaml
- uses: john0isaac/action-check-markdown@v1.1.0
  with:
    github-token: ${{ secrets.GITHUB_TOKEN }}
    command: check_broken_paths
    directory: ./
    guide-url: "https://github.com/<owner>/<repo>/blob/main/CONTRIBUTING.md"
```

See the [GitHub Actions how-to](https://markdown-checker.readthedocs.io/en/latest/howto/github-actions/)
for the full workflow, including running `check_broken_urls` (not yet
supported by the wrapper action) directly as a step.

## Documentation

- [Tutorial](https://markdown-checker.readthedocs.io/en/latest/tutorial/) - install and run your first check.
- [How-to guides](https://markdown-checker.readthedocs.io/en/latest/howto/) - configuration, rate limiting, report formats, CI.
- [CLI reference](https://markdown-checker.readthedocs.io/en/latest/reference/cli/) - every command-line option.
- [API reference](https://markdown-checker.readthedocs.io/en/latest/api/) - for programmatic use.
- [Full documentation](https://markdown-checker.readthedocs.io/en/latest/).

## Contributing

Contributions are welcome - see the
[Contributing guide](https://markdown-checker.readthedocs.io/en/latest/CONTRIBUTING/).

## License

[MIT](https://github.com/john0isaac/markdown-checker/blob/main/LICENSE)
