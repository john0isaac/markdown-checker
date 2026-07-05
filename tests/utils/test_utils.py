from markdown_checker import utils


def test_utils_package_exports_expected_names():
    """The utils package re-exports the public helper API."""
    assert set(utils.__all__) == {
        "MarkdownLinks",
        "Spinner",
        "find_pyproject",
        "get_files_paths_list",
        "get_github_repo_blob_url",
        "get_links_from_md_file",
        "load_config_section",
        "resolve_default_map",
        "spinner",
    }


def test_utils_package_exports_are_importable():
    """Every name in __all__ is accessible as an attribute of the package."""
    for name in utils.__all__:
        assert hasattr(utils, name)
