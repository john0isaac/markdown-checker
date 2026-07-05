from markdown_checker.reports import renderers


def test_renderers_package_exports_all_renderer_classes():
    """The renderers package re-exports all four concrete renderer classes."""
    assert set(renderers.__all__) == {
        "ConsoleRenderer",
        "GitHubAnnotationsRenderer",
        "JsonRenderer",
        "MarkdownRenderer",
    }


def test_renderers_package_exports_are_importable():
    """Every name in __all__ is accessible as an attribute of the package."""
    for name in renderers.__all__:
        assert hasattr(renderers, name)
