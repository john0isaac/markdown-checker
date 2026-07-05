"""
Module to load CLI defaults from ``[tool.markdown-checker]`` in ``pyproject.toml``.
"""

import difflib
from pathlib import Path
from typing import Any

import click
import tomllib

SECTION = "markdown-checker"

_META_OPTIONS = {"config_file", "isolated"}


def find_pyproject(start: Path) -> Path | None:
    """
    Find the nearest ``pyproject.toml`` walking up from *start*.

    Args:
        start: Directory to start the search from.

    Returns:
        The first ``pyproject.toml`` found, or ``None`` if none exists up to the filesystem root.
    """
    for directory in (start, *start.parents):
        candidate = directory / "pyproject.toml"
        if candidate.is_file():
            return candidate
    return None


def load_config_section(path: Path) -> dict[str, Any]:
    """
    Read the ``[tool.markdown-checker]`` table from *path*.

    Args:
        path: Path to a TOML file.

    Returns:
        A mapping of raw (hyphenated) keys to their configured values. Empty if the table is
        absent.

    Raises:
        click.UsageError: If the file cannot be parsed as TOML.
    """
    try:
        with path.open("rb") as fh:
            data = tomllib.load(fh)
    except tomllib.TOMLDecodeError as err:
        raise click.UsageError(f"Error parsing {path}: {err}") from err
    section = data.get("tool", {}).get(SECTION, {})
    if not isinstance(section, dict):
        raise click.UsageError(f"[tool.{SECTION}] in {path} must be a table.")
    return section


def _normalize(config: dict[str, Any]) -> dict[str, Any]:
    """Convert hyphenated TOML keys to the underscored parameter names Click expects."""
    return {key.replace("-", "_"): value for key, value in config.items()}


def _reject_unknown_keys(config: dict[str, Any], command: click.Command, path: Path) -> None:
    """
    Raise a ``click.UsageError`` if *config* contains keys that are not valid options.

    Args:
        config: Raw (hyphenated) keys read from the TOML file.
        command: The Click command whose parameters define the allowed key set.
        path: Path to the TOML file, used in the error message.

    Raises:
        click.UsageError: If any key in *config* does not correspond to a known option.
    """
    known = {param.name for param in command.params if param.name} - _META_OPTIONS
    known_hyphenated = {name.replace("_", "-") for name in known}
    unknown = sorted(set(config) - known_hyphenated)
    if not unknown:
        return

    suggestions: dict[str, list[str]] = {}
    for key in unknown:
        matches = difflib.get_close_matches(key, known_hyphenated, n=1)
        if matches:
            suggestions[key] = matches

    message = f"Unknown key(s) in [tool.{SECTION}] of {path}: {', '.join(unknown)}."
    if suggestions:
        hints = ", ".join(f"{key} -> {matches[0]}" for key, matches in suggestions.items())
        message += f" Did you mean: {hints}? (keys use hyphens, matching the long CLI flags)"
    raise click.UsageError(message)


def _prescan(args: list[str]) -> tuple[bool, Path | None]:
    """
    Scan raw CLI *args* for ``--isolated`` and ``-c``/``--config`` without full Click parsing.

    Args:
        args: The raw command-line arguments (excluding the program name).

    Returns:
        A tuple of ``(isolated, explicit_config_path)``.
    """
    isolated = False
    explicit_path: Path | None = None
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--isolated":
            isolated = True
        elif arg in ("-c", "--config"):
            if i + 1 < len(args):
                explicit_path = Path(args[i + 1])
                i += 1
        elif arg.startswith("--config="):
            explicit_path = Path(arg.split("=", 1)[1])
        i += 1
    return isolated, explicit_path


def resolve_default_map(args: list[str], command: click.Command) -> dict[str, Any] | None:
    """
    Resolve the ``default_map`` to seed a Click context with, from ``pyproject.toml``.

    Args:
        args: The raw command-line arguments (excluding the program name).
        command: The Click command whose parameters define the allowed key set.

    Returns:
        A mapping suitable for ``click.Context(default_map=...)``, or ``None`` if configuration
        should not be applied (``--isolated``, no config file found, or an empty table).
    """
    isolated, explicit_path = _prescan(args)
    if isolated:
        return None

    path = explicit_path or find_pyproject(Path.cwd())
    if path is None:
        return None

    config = load_config_section(path)
    if not config:
        return None

    _reject_unknown_keys(config, command, path)
    return _normalize(config)
