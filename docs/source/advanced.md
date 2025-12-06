<!-- markdownlint-disable MD041 -->
## Advanced Usage

To further customize your experience with the Markdown Checker, you can utilize additional command-line interface (CLI) options.

## Command Line Options

### `-d`, `--dir`

- **Type**: `click.Path`
- **Description**: Path to the root directory to check.
- **Required**: Yes

### `-f`, `--func`

- **Type**: `click.Choice`
- **Description**: Function to be executed.
- **Choices**:
  - `check_broken_paths`
  - `check_broken_urls`
  - `check_paths_tracking`
  - `check_urls_tracking`
  - `check_urls_locale`
- **Required**: Yes

### `-ext`, `--extensions`

- **Type**: `list[str]`
- **Description**: File extensions to filter the files.
- **Default**:
  - `.md`
  - `.ipynb`
- **Required**: No

### `-td`, `--tracking-domains`

- **Type**: `list[str]`
- **Description**: List of tracking domains to check.
- **Default**:
  - `github.com`
  - `microsoft.com`
  - `visualstudio.com`
  - `aka.ms`
  - `azure.com`
- **Required**: No

### `-sf`, `--skip-files`

- **Type**: `list[str]`
- **Description**: List of file names to skip check.
- **Default**:
  - `CODE_OF_CONDUCT.md`
  - `SECURITY.md`
- **Required**: No

### `-sd`, `--skip-domains`

- **Type**: `list[str]`
- **Description**: List of domains to skip checking.
- **Default**: `[]`
- **Required**: No

### `-suc`, `--skip-urls-containing`

- **Type**: `list[str]`
- **Description**: List of strings to skip checking if their urls are working or not.
- **Default**:
  - `https://www.microsoft.com/en-us/security/blog`
  - `video-embed.html`
- **Required**: No

### `-gu`, `--guide-url`

- **Type**: `str`
- **Description**: Full URL of your contributing guide.
- **Required**: No

### `-to`, `--timeout`

- **Type**: `Click.IntRange`
- **Description**: Timeout in seconds for the requests before retrying.
- **Default**: `15`
- **Range**: `0-50`
- **Required**: No

### `-rt`, `--retries`

- **Type**: `Click.IntRange`
- **Description**: Number of retries for the requests before flagging a url as broken.
- **Default**: `3`
- **Range**: `0-10`
- **Required**: No

### `-o`, `--output-file-name`

- **Type**: `str`
- **Description**: Name of the output file.
- **Default**: `comment`
- **Required**: No

### `SRC ...`

- **Type**: `click.Path`
- **Description**: Source files or directories to check.
- **Required**: No

## Other Options

### `--version`

- **Type**: `bool`
- **Description**: Show the version and exit.
- **Required**: No

### `--help`

- **Type**: `bool`
- **Description**: Show the help message and exit.
- **Required**: No
