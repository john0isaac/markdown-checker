# Usage

The library provides the following functions:

[Usage](#usage):

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

## Want to do more? Check out the [Advanced Usage](./advanced.md) page.
