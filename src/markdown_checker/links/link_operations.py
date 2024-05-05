import os
import re


def get_links_from_file(file_path: str) -> list[str]:
    """function to get an array of markdown links from a file
    flags markdown links captures the part inside () that comes right after []
    """
    all_links = []
    with open(file_path, encoding="utf-8") as file:
        data = file.read()
        link_pattern = re.compile(r"\]\((.*?)\)| \)")
        matches = re.finditer(link_pattern, data)
        for matched_group in matches:
            if matched_group.group(1):
                all_links.append(matched_group.group(1))
    return all_links


def get_urls_from_links(all_links: list[str]) -> list[str]:
    """function to get an array of urls from a list"""
    urls = []
    url_pattern = re.compile(
        r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9]{1,6}\b([-a-zA-Z0-9@:%_\+.~#?&\/\/=]*)"
    )
    allowed_list = [
        "github.com",
        "microsoft.com",
        "visualstudio.com",
        "aka.ms",
        "azure.com",
    ]
    for link in all_links:
        matches = re.findall(url_pattern, link)

        if matches and any(allowed in link.lower() for allowed in allowed_list):
            urls.append(link)
    return urls


def get_paths_from_links(all_links: list[str]) -> list[str]:
    """function to get relative paths from a list
    flags paths that start with ./ or ../
    """
    paths = []
    path_pattern = re.compile(r"(\.{1,2}\/)+([A-Za-z0-9-]+\/)*(.+\.[A-Za-z]+)")

    for link in all_links:
        link = link.split(" ")[0]
        matches = re.findall(path_pattern, link)
        if matches:
            paths.append(link.split("#")[0])
    return paths


def check_paths_exists(file_path: str, paths: list[str]) -> list[str]:
    """function checks if a path exist if not return non existent paths
    flags any relative path that can't be accessed
    """
    broken_path = []
    for path in paths:
        path = re.sub(r"(\?|\&)(WT|wt)\.mc_id=.*", "", path)
        if not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(file_path), path))):
            broken_path.append(path)
    return broken_path


def check_url_locale(urls: list[str]) -> list[str]:
    """function checks if a url has country locale
    flags urls that have ==> /en-us/
    """
    country_locale = []
    for url in urls:
        if "video-embed.html" in url or "https://www.microsoft.com/en-us/security/blog" in url:
            continue
        locale_pattern = re.compile(r"\/[a-z]{2}-[a-z]{2}\/")
        matches = re.findall(locale_pattern, url)
        if matches:
            country_locale.append(url)
    return country_locale


def check_url_tracking(urls: list[str]) -> list[str]:
    """function checks if a url has tracking id
    flags urls missing ==> (? or &) plus WT.mc_id= or wt.mc_id=
    """
    tracking_id = []
    for url in urls:
        tracking_pattern = re.compile(r"(\?|\&)(WT|wt)\.mc_id=")
        matches = re.findall(tracking_pattern, url)
        if not matches:
            tracking_id.append(url)
    return tracking_id


def check_url_alive(urls: list[str]) -> list[str]:
    import requests  # type: ignore

    broken_urls = []
    for url in urls:
        if "https://vscode.dev/redirect?url=" in url:
            continue
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                broken_urls.append(url)
        except requests.exceptions.RequestException:
            broken_urls.append(url)
            continue
    return broken_urls


# DEPRECATED
def get_urls_from_file(file_path: str) -> list[str]:
    """function to get an array of urls from a file"""
    urls = []
    with open(file_path, encoding="utf-8") as file:
        data = file.read()
        url_pattern = re.compile(
            r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9]{1,6}\b([-a-zA-Z0-9@:%_\+.~#?&\/\/=]*)"
        )
        matches = re.finditer(url_pattern, data)
        for matched_group in matches:
            urls.append(matched_group.group())
    return urls


def get_paths_from_file(file_path: str) -> list[str]:
    """function to get relative paths from a file"""
    paths = []
    with open(file_path, encoding="utf-8") as file:
        data = file.read()
        path_pattern = re.compile(r"(\.{1,2}\/)+([A-Za-z0-9-]+\/)*([A-Za-z0-9]+\.[A-Za-z]+)")
        matches = re.finditer(path_pattern, data)
        for matched_group in matches:
            paths.append(matched_group.group())
    return paths
