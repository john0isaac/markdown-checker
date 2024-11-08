# Release History

All notable changes to this project will be documented in this file.

## [v0.0.0] Date

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

## [v0.2.2] 8 Nov 2024

- Change Broken URLs flagging to always try head and get request on any URL before flagging it as broken.

## [v0.2.1] 7 Aug 2024

- Fix command line list[str] type issue and use Click.IntRange for retries and timeout.

## [v0.2.0] 7 Aug 2024

- Redesign the package.
- Port to using Click instead of arg_parser.
- Expose options for external users to allow for more customization.
- Increase coverage for paths by including paths that start with `/` or nothing.
- Add retires for URLs before flagging them as broken.
- Preform head request on URL which falls back to get if both not working flag as broken after retries count finishes.
- Analyze all web URLs except the ones in skip_domains list.
- Change Syntax of terminal comments to improve readability.
- Add Spinner to indicate that the tool is working (Not compatible with all terminals)
- Add documentation for the new features.
- Use multiprocessing for checking broken urls reducing the execution time by 50%.
- Add support for GitHub automatic annotations.

## [v0.1.5] 8 Jul 2024

- Increase timeout for requests to check web urls alive or not. https://github.com/john0isaac/markdown-checker/pull/52

## [v0.1.4] 6 May 2024

- Improve Dev Experience. https://github.com/john0isaac/markdown-checker/pull/28
- Better Typing. https://github.com/john0isaac/markdown-checker/pull/37
- Add ruff, black, mypy and workflows to check them on all supported python versions.
- Add pre-commit.
- Change packaging strategy to setuptools with pyproject.toml.
- Add docs in read the docs https://markdown-checker.readthedocs.io/en/latest/

## [v0.1.3] 15 March 2024

- Change lessons to files
- Remove ID's from the end of Relative Paths

## [v0.1.2] 06 March 2024

-  Improve-package by @john0isaac in https://github.com/john0isaac/markdown-checker/pull/21
- Skipped vs code redirect urls
- fixed typos

## [v0.1.1] 06 March 2024

- fix: add requests to required packages by @john0isaac in https://github.com/john0isaac/markdown-checker/pull/19

## [v0.1.0] 06 March 2024

- add development requirements and install in devcontainer by @john0isaac in https://github.com/john0isaac/markdown-checker/pull/13
- format with ruff and black by @john0isaac in https://github.com/john0isaac/markdown-checker/pull/14
- improve output of checker by @john0isaac in https://github.com/john0isaac/markdown-checker/pull/15
- feat: broken urls by @john0isaac in https://github.com/john0isaac/markdown-checker/pull/16
- Skip microsoft security blog by @john0isaac in https://github.com/john0isaac/markdown-checker/pull/17

## [v0.0.9] 05 March 2024

- fix: skip video urls
- feat: add devcontainer

## [v0.0.8] 30 December 2023

- feat: separate into modules
- feat: generate markdown file
- define tests to execute functions
- docs: add instructions for local development

## [v0.0.7] 26 November 2023

- Rename get_input_args to inputs module with no change.
- Improve paths reading using recursion.
- Improve script output format.

## [v0.0.5] 22 November 2023

- Add description to package.
- Improve package metadata.
- Configure GitHub Actions on release.
- Add Contributing guidance, code of conduct, and templates for issues and pull requests.

## [v0.0.4] 21 November 2023

- Initial Release.
