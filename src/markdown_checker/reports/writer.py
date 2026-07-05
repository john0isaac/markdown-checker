"""
Writes rendered report strings to a file or stdout.
"""

import sys
from pathlib import Path


def write_report(rendered: str, *, output_path: Path | None) -> None:
    """
    Write a rendered report to `output_path`, or to stdout when `output_path`
    is `None`.

    Args:
        rendered: The rendered report body, as returned by a `ReportRenderer`.
        output_path: File path to write to, or `None` to write to stdout.
    """
    if output_path is None:
        sys.stdout.write(rendered)
        return
    output_path.write_text(rendered, encoding="utf-8")
