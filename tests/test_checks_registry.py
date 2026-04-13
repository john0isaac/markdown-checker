import pytest

from markdown_checker.checks import REGISTRY
from markdown_checker.checks.base import BaseCheck


def test_registry_contains_all_checks():
    """Registry contains all expected check names."""
    expected = {
        "check_broken_paths",
        "check_broken_urls",
        "check_urls_tracking",
        "check_paths_tracking",
        "check_urls_locale",
        "check_paths_locale",
    }
    assert set(REGISTRY.keys()) == expected


@pytest.mark.parametrize("name", list(REGISTRY.keys()))
def test_registry_values_are_base_check_instances(name):
    """Each registry entry is a BaseCheck instance."""
    assert isinstance(REGISTRY[name], BaseCheck)


@pytest.mark.parametrize("name", list(REGISTRY.keys()))
def test_registry_check_name_matches_key(name):
    """Each registry key matches the check's name attribute."""
    assert REGISTRY[name].name == name


@pytest.mark.parametrize("name", list(REGISTRY.keys()))
def test_registry_check_has_link_type(name):
    """Each registry entry declares a link_type."""
    assert REGISTRY[name].link_type in ("paths", "urls")
