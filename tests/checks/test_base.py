from pathlib import Path

import pytest

from markdown_checker.checks.base import BaseCheck
from markdown_checker.models import MarkdownLinkBase
from markdown_checker.models.path import MarkdownPath
from markdown_checker.utils.extract_links import MarkdownLinks


class _DummyCheck(BaseCheck[MarkdownLinkBase]):
    """Minimal concrete BaseCheck used to exercise the default submit/collect."""

    name = "dummy_check"
    link_type = "paths"

    def run(self, links, config=None, service=None):
        for path in links.paths:
            path.issue = "is broken"
        return list(links.paths)


def _paths(*links: str) -> MarkdownLinks:
    return MarkdownLinks(
        urls=[],
        paths=[MarkdownPath(link=link, line_number=1, file_path=Path("test.md")) for link in links],
    )


def test_submit_default_runs_synchronously():
    """The default submit() runs the check synchronously and returns its result."""
    check = _DummyCheck()
    pending = check.submit(links=_paths("./missing.md"))
    assert len(pending) == 1
    assert pending[0].link == "./missing.md"


def test_collect_default_returns_pending_unchanged():
    """The default collect() returns the pending token as-is."""
    check = _DummyCheck()
    pending = ["already resolved"]
    assert check.collect(pending) == pending


def test_submit_then_collect_round_trip():
    """submit() followed by collect() returns the same result as run()."""
    check = _DummyCheck()
    pending = check.submit(links=_paths("./a.md", "./b.md"))
    result = check.collect(pending)
    assert len(result) == 2


def test_base_check_cannot_be_instantiated_directly():
    """BaseCheck is abstract and cannot be instantiated on its own."""
    with pytest.raises(TypeError):
        BaseCheck()
