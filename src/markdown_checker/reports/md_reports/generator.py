import pathlib
from typing import Union

from markdown_checker.reports.generator_base import GeneratorBase


class MarkdownGenerator(GeneratorBase):
    current_dir = pathlib.Path(__file__).parent
    check_broken_paths_template = open(current_dir / "templates/paths/broken.md").read()
    check_broken_urls_template = open(current_dir / "templates/urls/broken.md").read()
    check_paths_tracking_template = open(current_dir / "templates/paths/tracking.md").read()
    check_urls_tracking_template = open(current_dir / "templates/urls/tracking.md").read()
    check_urls_locale_template = open(current_dir / "templates/urls/locale.md").read()
    templates = {
        "check_broken_paths": check_broken_paths_template,
        "check_broken_urls": check_broken_urls_template,
        "check_paths_tracking": check_paths_tracking_template,
        "check_urls_tracking": check_urls_tracking_template,
        "check_urls_locale": check_urls_locale_template,
    }

    def __init__(
        self,
        contributing_guide_url: Union[str, None] = None,
        output_file_name: str = "comment",
    ) -> None:
        self.output_file_name = output_file_name
        self.contributing_guide_line = (
            (f" For more details, check our [Contributing Guide]({contributing_guide_url}).\n\n")
            if contributing_guide_url
            else "\n\n"
        )

    def _write_file(self, generated_text: str) -> None:
        """Write the formatted output to a markdown file"""
        with open(f"{self.output_file_name}.md", "w", encoding="utf-8") as file:
            file.write(generated_text)

    def _generate_text(self, function_name: str, formatted_output: str) -> str:
        """Generate markdown text based on the formatted output, function name, and contributing guide URL.

        Args:
            formatted_output (str): The formatted output to be written to the markdown file.
            function_name (str): The name of the function to determine the header for the markdown file.

        Raises:
            ValueError: If an invalid function name is provided.

        """
        try:
            formatted_output = self.templates[function_name] + self.contributing_guide_line + formatted_output
            return formatted_output
        except KeyError:
            raise ValueError("Invalid function name")

    def generate(self, function_name: str, formatted_output: str) -> None:
        """
        Generate a markdown report based on the formatted output.

        Args:
            function_name (str): The name of the function to determine the header for the markdown file.
            formatted_output (str): The formatted output to be written to the markdown file.
        """
        generated_text = self._generate_text(function_name=function_name, formatted_output=formatted_output)
        self._write_file(generated_text)
