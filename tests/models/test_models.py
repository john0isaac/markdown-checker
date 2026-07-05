from markdown_checker import models


def test_models_package_exports_expected_names():
    """The models package re-exports the public link and config API."""
    assert set(models.__all__) == {
        "Config",
        "DEFAULT_HEADERS",
        "create_http_client",
        "MarkdownLinkBase",
        "MarkdownPath",
        "MarkdownURL",
        "URLCheckResult",
    }


def test_models_package_exports_are_importable():
    """Every name in __all__ is accessible as an attribute of the package."""
    for name in models.__all__:
        assert hasattr(models, name)
