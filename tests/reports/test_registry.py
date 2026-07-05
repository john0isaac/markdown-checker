import pytest

from markdown_checker.reports.base import ReportRenderer
from markdown_checker.reports.registry import get_renderer
from markdown_checker.reports.registry import RENDERERS
from markdown_checker.reports.renderers.json import JsonRenderer


def test_registry_contains_expected_formats():
    """RENDERERS contains all built-in formats."""
    assert set(RENDERERS.keys()) == {"markdown", "json", "github-annotations", "console"}


@pytest.mark.parametrize("name", list(RENDERERS.keys()))
def test_registry_values_are_renderer_subclasses(name):
    """Each registry entry subclasses ReportRenderer."""
    assert issubclass(RENDERERS[name], ReportRenderer)


@pytest.mark.parametrize("name", list(RENDERERS.keys()))
def test_registry_format_name_matches_key(name):
    """Each registry key matches the renderer's format_name attribute."""
    assert RENDERERS[name].format_name == name


def test_get_renderer_returns_instance():
    """get_renderer instantiates the renderer class by name."""
    renderer = get_renderer("json")
    assert isinstance(renderer, JsonRenderer)


def test_get_renderer_forwards_options():
    """get_renderer forwards keyword arguments to the renderer constructor."""
    renderer = get_renderer("json", indent=4)
    assert isinstance(renderer, JsonRenderer)
    assert renderer.indent == 4


def test_get_renderer_unknown_format_raises():
    """get_renderer raises ValueError for unknown format names."""
    with pytest.raises(ValueError, match="Unknown report format"):
        get_renderer("nonexistent")
