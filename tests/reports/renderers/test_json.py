import json

from markdown_checker.reports.renderers.json import JsonRenderer


def test_json_renderer_produces_valid_json(sample_report):
    """JsonRenderer output parses as JSON with expected structure."""
    data = json.loads(JsonRenderer().render(sample_report))
    assert data["check"] == "check_broken_urls"
    assert data["summary"] == {"files_checked": 1, "links_checked": 2, "errors": 1, "warnings": 1}
    assert data["files"][0]["path"] == "docs/usage.rst"
    links = {issue["link"] for issue in data["files"][0]["issues"]}
    assert links == {"https://broken.example.com", "https://warn.example.com"}


def test_json_renderer_includes_tool_version(sample_report):
    """JsonRenderer includes tool metadata from the report context."""
    data = json.loads(JsonRenderer().render(sample_report))
    assert data["tool"]["version"] == "1.2.1"


def test_json_renderer_respects_custom_indent(sample_report):
    """A custom indent is honored when rendering."""
    default_result = JsonRenderer().render(sample_report)
    custom_result = JsonRenderer(indent=4).render(sample_report)
    assert default_result != custom_result
    assert json.loads(default_result) == json.loads(custom_result)
