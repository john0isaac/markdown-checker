from pathlib import Path

import pytest

from markdown_checker.reports.base import GeneratorBase
from markdown_checker.reports.markdown import MarkdownGenerator


def test_markdown_generator_is_generator_base():
    """MarkdownGenerator is a subclass of GeneratorBase."""
    assert issubclass(MarkdownGenerator, GeneratorBase)


def test_default_output_file_name():
    """Default output file name is 'comment'."""
    gen = MarkdownGenerator()
    assert gen.output_file_name == "comment"


def test_custom_output_file_name():
    """Custom output file name is set correctly."""
    gen = MarkdownGenerator(output_file_name="report")
    assert gen.output_file_name == "report"


def test_contributing_guide_url_included():
    """Contributing guide URL is included in the guide line."""
    gen = MarkdownGenerator(contributing_guide_url="https://example.com/CONTRIBUTING.md")
    assert "https://example.com/CONTRIBUTING.md" in gen.contributing_guide_line


def test_contributing_guide_url_none():
    """No contributing guide line when URL is None."""
    gen = MarkdownGenerator(contributing_guide_url=None)
    assert gen.contributing_guide_line == "\n\n"


def test_templates_loaded():
    """Templates are lazy-loaded: empty at init, populated on first use."""
    gen = MarkdownGenerator()
    assert gen.templates == {}

    expected_keys = {
        "check_broken_paths",
        "check_broken_urls",
        "check_paths_tracking",
        "check_urls_tracking",
        "check_urls_locale",
    }
    assert set(MarkdownGenerator._TEMPLATE_PATHS.keys()) == expected_keys


@pytest.mark.parametrize(
    "func_name",
    [
        "check_broken_paths",
        "check_broken_urls",
        "check_paths_tracking",
        "check_urls_tracking",
        "check_urls_locale",
    ],
)
def test_generate_text_prepends_template(func_name):
    """Generated text starts with the template for the given function."""
    gen = MarkdownGenerator()
    result = gen._generate_text(func_name, "some output")
    assert gen.templates[func_name] in result
    assert "some output" in result


def test_generate_text_invalid_function_raises():
    """Raises ValueError for unknown function names."""
    gen = MarkdownGenerator()
    with pytest.raises(ValueError, match="Invalid function name"):
        gen._generate_text("nonexistent_check", "output")


def test_write_file_creates_file(tmp_path, monkeypatch):
    """Writes generated text to a markdown file."""
    monkeypatch.chdir(tmp_path)
    gen = MarkdownGenerator(output_file_name=str(tmp_path / "test_output"))
    gen._write_file("# Test Content")
    output_file = Path(f"{tmp_path}/test_output.md")
    assert output_file.exists()
    assert output_file.read_text(encoding="utf-8") == "# Test Content"


def test_generate_creates_output_file(tmp_path, monkeypatch):
    """Full generate flow creates the output markdown file."""
    monkeypatch.chdir(tmp_path)
    gen = MarkdownGenerator(output_file_name=str(tmp_path / "result"))
    gen.generate("check_broken_paths", "| File | Issues |\n")
    output_file = Path(f"{tmp_path}/result.md")
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "| File | Issues |" in content


def test_templates_are_non_empty():
    """All templates contain content."""
    gen = MarkdownGenerator()
    for key in MarkdownGenerator._TEMPLATE_PATHS:
        gen._generate_text(key, "dummy")
    for key, template in gen.templates.items():
        assert len(template) > 0, f"Template for {key} is empty"
    assert len(gen.templates) == len(MarkdownGenerator._TEMPLATE_PATHS)
