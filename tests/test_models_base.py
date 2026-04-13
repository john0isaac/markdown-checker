from pathlib import Path

import pytest

from markdown_checker.models.path import MarkdownPath

# MarkdownLinkBase is abstract, so we test through MarkdownPath (a concrete subclass).


@pytest.mark.parametrize(
    "link, expected",
    [
        ("https://learn.microsoft.com/en-us/azure", True),
        ("https://example.com/fr-fr/docs", True),
        ("https://example.com/pt-br/page", True),
        ("https://example.com/docs/page", False),
        ("https://example.com/azure", False),
        ("./en-us/docs/guide.md", True),
        ("./docs/guide.md", False),
    ],
)
def test_has_locale(link: str, expected: bool):
    """Detects locale segments like /en-us/ in links."""
    obj = MarkdownPath(link=link, line_number=1, file_path=Path("test.md"))
    assert obj.has_locale() == expected


@pytest.mark.parametrize(
    "link, expected",
    [
        ("https://learn.microsoft.com/azure?WT.mc_id=test123", True),
        ("https://learn.microsoft.com/azure?wt.mc_id=test123", True),
        ("https://learn.microsoft.com/azure&WT.mc_id=test123", True),
        ("https://learn.microsoft.com/azure", False),
        ("https://learn.microsoft.com/azure?ref=other", False),
        ("./docs/guide.md?WT.mc_id=abc", True),
        ("./docs/guide.md", False),
    ],
)
def test_has_tracking(link: str, expected: bool):
    """Detects tracking IDs (WT.mc_id) in links."""
    obj = MarkdownPath(link=link, line_number=1, file_path=Path("test.md"))
    assert obj.has_tracking() == expected


def test_str_returns_link():
    """__str__ returns the link string."""
    obj = MarkdownPath(link="./docs/guide.md", line_number=1, file_path=Path("test.md"))
    assert str(obj) == "./docs/guide.md"


def test_repr_returns_link():
    """__repr__ contains the link string."""
    obj = MarkdownPath(link="./docs/guide.md", line_number=1, file_path=Path("test.md"))
    assert "./docs/guide.md" in repr(obj)


def test_default_issue_is_empty():
    """Default issue field is an empty string."""
    obj = MarkdownPath(link="./docs/guide.md", line_number=1, file_path=Path("test.md"))
    assert obj.issue == ""


def test_issue_can_be_set():
    """Issue field can be set on construction."""
    obj = MarkdownPath(link="./docs/guide.md", line_number=1, file_path=Path("test.md"), issue="is broken")
    assert obj.issue == "is broken"
