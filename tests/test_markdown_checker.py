import markdown_checker
from markdown_checker import __version__
from markdown_checker import Config
from markdown_checker import main
from markdown_checker import MarkdownLinkBase
from markdown_checker import MarkdownPath
from markdown_checker import MarkdownURL


def test_version_is_a_non_empty_string():
    """__version__ is exposed and non-empty."""
    assert isinstance(__version__, str)
    assert __version__


def test_package_exports_expected_names():
    """The top-level package re-exports its public API."""
    assert set(markdown_checker.__all__) == {
        "Config",
        "MarkdownLinkBase",
        "MarkdownPath",
        "MarkdownURL",
        "__version__",
        "main",
    }


def test_package_exports_are_the_expected_objects():
    """Each exported name resolves to the object from its defining module."""
    assert markdown_checker.Config is Config
    assert markdown_checker.MarkdownLinkBase is MarkdownLinkBase
    assert markdown_checker.MarkdownPath is MarkdownPath
    assert markdown_checker.MarkdownURL is MarkdownURL
    assert markdown_checker.main is main
