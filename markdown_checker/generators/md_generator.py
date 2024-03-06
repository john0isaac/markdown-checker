CHECK_BROKEN_PATHS = """# Check Broken Paths

We have automatically detected the following broken relative paths in your lessons. Review and fix the paths to resolve this issue.

Check the file paths and associated broken paths inside them."""
CHECK_BROKEN_URLS = """# Check Broken URLs

We have automatically detected the following broken URLs in your lessons. Review and fix the paths to resolve this issue.

Check the file paths and associated broken urls inside them."""
CHECK_PATHS_TRACKING = """# Check Missing Tracking from Paths

We have automatically detected missing tracking id from the following relative paths in your lessons. Review and add tracking to paths to resolve this issue.

Check the file paths and associated paths inside them."""
CHECK_URLS_TRACKING = """# Check Missing Tracking from URLs

We have automatically detected missing tracking id from the following URLs in your lessons. Review and add tracking to URLs to resolve this issue.

Check the file paths and associated URLs inside them."""
CHECK_URLS_LOCALE = """# Check Country Locale in URLs

We have automatically detected added country locale to URLs in your lessons. Review and remove country specific locale from URLs to resolve this issue.

Check the file paths and associated URLs inside them."""


def write_md_file(generated_md: str) -> None:
    """Write the formatted output to a markdown file"""
    with open("comment.md", "w", encoding="utf-8") as file:
        file.write(generated_md)


def generate_md(
    formatted_output: str, function_name: str, contributing_guide_url: str
) -> None:
    """Generate markdown file based on the formatted output, function name, and contributing guide URL.

    Args:
        formatted_output (str): The formatted output to be written to the markdown file.
        function_name (str): The name of the function to determine the header for the markdown file.
        contributing_guide_url (str): The URL of the contributing guide to be included in the markdown file.

    Raises:
        ValueError: If an invalid function name is provided.

    """
    contributing_guide_line = f" For more details, check our [Contributing Guide]({contributing_guide_url}).\n\n"
    if function_name == "check_broken_paths":
        formatted_output = (
            CHECK_BROKEN_PATHS + contributing_guide_line + formatted_output
        )
    elif function_name == "check_broken_urls":
        formatted_output = (
            CHECK_BROKEN_URLS + contributing_guide_line + formatted_output
        )
    elif function_name == "check_paths_tracking":
        formatted_output = (
            CHECK_PATHS_TRACKING + contributing_guide_line + formatted_output
        )
    elif function_name == "check_urls_tracking":
        formatted_output = (
            CHECK_URLS_TRACKING + contributing_guide_line + formatted_output
        )
    elif function_name == "check_urls_locale":
        formatted_output = (
            CHECK_URLS_LOCALE + contributing_guide_line + formatted_output
        )
    else:
        raise ValueError("Invalid function name")

    write_md_file(formatted_output)
