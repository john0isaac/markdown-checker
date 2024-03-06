"""
Module providing automatic checks functionality to markdown files 
following some Guidelines
"""

from markdown_checker.links.link_operations import (
    get_links_from_file,
    get_paths_from_links,
    get_urls_from_links,
    check_paths_exists,
    check_url_locale,
    check_url_tracking,
)


def check_broken_links(file_path: str, link_type: str, check_type: str) -> str:
    """function that checks if urls and hyperlinks are broken

    Keyword arguments:
    file_path -- a path to text file to check
    link_type -- path or url
    check_type -- broken or tracking or locale
    Return: broken links and associated file path
    """
    all_links = get_links_from_file(file_path)

    # check if file has links
    if len(all_links) > 0:
        formatted_output = f"|<code>{file_path}</code>|"
        if link_type == "path":
            paths = get_paths_from_links(all_links)
            if check_type == "broken" and len(paths) > 0:
                broken_path = check_paths_exists(file_path, paths)
                if len(broken_path) > 0:
                    formatted_output += f"<code>{broken_path}</code>|\n"
                    return formatted_output
            elif check_type == "tracking" and len(paths) > 0:
                tracking_id_paths = check_url_tracking(paths)
                if len(tracking_id_paths) > 0:
                    formatted_output += f"<code>{tracking_id_paths}</code>|\n"
                    return formatted_output
        elif link_type == "url":
            urls = get_urls_from_links(all_links)
            if check_type == "tracking" and len(urls) > 0:
                tracking_id_urls = check_url_tracking(urls)
                if len(tracking_id_urls) > 0:
                    formatted_output += f"<code>{tracking_id_urls}</code>|\n"
                    return formatted_output
            elif check_type == "locale" and len(urls) > 0:
                country_locale_urls = check_url_locale(urls)
                if len(country_locale_urls) > 0:
                    formatted_output += f"<code>{country_locale_urls}</code>|\n"
                    return formatted_output
