# markdown-checker

Markdown link validation reporting tool. It provides a couple of functions to validate relative paths and web urls.

## Requirements

You will need the following prerequisites in order to use this library:

- Python >= 3.8
- [requests](https://pypi.org/project/requests/)

## Installation

```bash
pip install markdown-checker
```

## 1, 2, 3 - How To

1. Run `pip install markdown-checker`.
2. Run `markdown-checker -d {src} -f {func} -gu {url}`. Replace `{src}` with the directory you want to analyze, `{func}` with the available functions like `check_broken_paths`, `{gu}` with your contribution guidance full URL.
3. The output will be displayed in the terminal and in a `comments.md` file.
