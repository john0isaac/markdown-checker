## Advanced Usage

To further customize your experience with the Markdown Checker, you can utilize additional command-line interface (CLI) options.

## Command Line Options

### `-d`, `--dir`
- **Type**: `click.Path`
- **Description**: Path to the root directory to check.
- **Required**: Yes

### `-ext`, `--extensions`
- **Type**: `list[str]`
- **Description**: File extensions to filter the files.
- **Default**: 
    - `.md`
    - `.ipynb`
- **Required**: Yes

### `-td`, `--tracking-domains`
- **Type**: `list[str]`
- **Description**: List of tracking domains to check if they have a tracking id or not.
- **Default**: 
    - `github.com`
    - `microsoft.com`
    - `visualstudio.com`
    - `aka.ms`
    - `azure.com`
- **Required**: Yes

### `-sf`, `--skip-files`
- **Type**: `list[str]`
- **Description**: List of file names to skip check.
- **Default**: 
    - `CODE_OF_CONDUCT.md`
    - `SECURITY.md`
- **Required**: Yes

### `-sd`, `--skip-domains`
- **Type**: `list[str]`
- **Description**: List of domains to skip checking if their urls are working or not.
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
- **Required**: Yes

### `-to`, `--timeout`
- **Type**: `int`
- **Description**: Timeout in seconds for the requests before retrying.
- **Default**: `10`
- **Required**: No

### `-rt`, `--retries`
- **Type**: `int`
- **Description**: Number of retries for the requests before flagging a url as broken.
- **Default**: `3`
- **Required**: No

### `-o`, `--output-file-name`
- **Type**: `str`
- **Description**: Name of the output file.
- **Default**: `comments`
- **Required**: Yes


## Other Options

### `--version`
- **Type**: `bool`
- **Description**: Show the version and exit.
- **Required**: No

### `--help`
- **Type**: `bool`
- **Description**: Show the help message and exit.
- **Required**: No
