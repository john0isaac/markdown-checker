import pathlib

from markdown_checker.reports.base import GeneratorBase


class MarkdownGenerator(GeneratorBase):
    current_dir = pathlib.Path(__file__).parent

    _TEMPLATE_PATHS: dict[str, str] = {
        "check_broken_paths": "templates/paths/broken.md",
        "check_broken_urls": "templates/urls/broken.md",
        "check_paths_tracking": "templates/paths/tracking.md",
        "check_urls_tracking": "templates/urls/tracking.md",
        "check_urls_locale": "templates/urls/locale.md",
    }

    def __init__(
        self,
        contributing_guide_url: str | None = None,
        output_file_name: str = "comment",
    ) -> None:
        self.templates: dict[str, str] = {}
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
        if function_name not in self._TEMPLATE_PATHS:
            raise ValueError("Invalid function name")

        if function_name not in self.templates:
            with open(self.current_dir / self._TEMPLATE_PATHS[function_name], encoding="utf-8") as f:
                self.templates[function_name] = f.read()

        formatted_output = self.templates[function_name] + self.contributing_guide_line + formatted_output
        return formatted_output

    def generate(self, function_name: str, formatted_output: str) -> None:
        """
        Generate a markdown report based on the formatted output.

        Args:
            function_name (str): The name of the function to determine the header for the markdown file.
            formatted_output (str): The formatted output to be written to the markdown file.
        """
        generated_text = self._generate_text(function_name=function_name, formatted_output=formatted_output)
        self._write_file(generated_text)
