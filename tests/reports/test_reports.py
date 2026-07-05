from markdown_checker import reports


def test_reports_package_exports_expected_names():
    """The reports package re-exports the public model, registry, and renderer API."""
    expected = {
        "RENDERERS",
        "ConsoleRenderer",
        "FileReport",
        "GitHubAnnotationsRenderer",
        "JsonRenderer",
        "MarkdownRenderer",
        "Report",
        "ReportContext",
        "ReportFormat",
        "ReportIssue",
        "ReportRenderer",
        "build_report",
        "get_renderer",
        "write_report",
    }
    assert set(reports.__all__) == expected


def test_reports_package_exports_are_importable():
    """Every name in __all__ is accessible as an attribute of the package."""
    for name in reports.__all__:
        assert hasattr(reports, name)
