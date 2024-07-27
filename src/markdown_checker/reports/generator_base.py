from abc import ABC, abstractmethod
from pathlib import Path


class GeneratorBase(ABC):
    """Base class for all report generators."""

    current_dir: Path
    check_broken_paths_template: str
    check_broken_urls_template: str
    check_paths_tracking_template: str
    check_urls_tracking_template: str
    check_urls_locale_template: str
    templates: dict[str, str]

    @abstractmethod
    def _write_file(self, generated_text: str) -> None:
        """Write the formatted output to a file."""
        raise NotImplementedError

    @abstractmethod
    def _generate_text(self, function_name: str, formatted_output: str) -> str:
        """
        Generate text based on the formatted output, function name, and contributing guide URL.

        Args:
            formatted_output (str): The formatted output to be written to the file.
            function_name (str): The name of the function to determine the header for the file.
        """
        raise NotImplementedError

    @abstractmethod
    def generate(self, function_name: str, formatted_output: str) -> None:
        """Generate a report based on the formatted output."""
        raise NotImplementedError
