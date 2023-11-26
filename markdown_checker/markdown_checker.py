"""
Module providing automatic checks functionality to markdown files 
following some Guidelines
"""
import os
import re

# Helper Functions

def check_broken_links(file_path : str, link_type : str , check_type: str) -> str:
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
                if len (broken_path) > 0:
                    formatted_output += f'<code>{broken_path}</code>|\n'
                    return formatted_output
            elif check_type == "tracking" and len(paths) > 0:
                tracking_id_paths = check_url_tracking(paths)
                if len(tracking_id_paths) > 0:
                    formatted_output += f'<code>{tracking_id_paths}</code>|\n'
                    return formatted_output
        elif link_type == "url":
            urls = get_urls_from_links(all_links)
            if check_type == "tracking" and len(urls) > 0:
                tracking_id_urls = check_url_tracking(urls)
                if len(tracking_id_urls) > 0:
                    formatted_output += f'<code>{tracking_id_urls}</code>|\n'
                    return formatted_output
            elif check_type == "locale" and len(urls) > 0:
                country_locale_urls = check_url_locale(urls)
                if len(country_locale_urls) > 0:
                    formatted_output += f'<code>{country_locale_urls}<\code>|\n'
                    return formatted_output

def get_links_from_file(file_path: str) -> list:
    """function to get an array of markdown links from a file
    flags markdown links captures the part inside () that comes right after []
    """
    all_links = []
    with open(file_path, 'r',  encoding="utf-8") as file:
        data = file.read()
        link_pattern = re.compile(r'\]\((.*?)\)| \)')
        matches = re.finditer(link_pattern, data)
        for matched_group in matches:
            if matched_group.group(1):
                all_links.append(matched_group.group(1))
    return all_links

def get_urls_from_links(all_links: list) -> list:
    """function to get an array of urls from a list"""
    urls = []
    url_pattern = re.compile(r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9]{1,6}\b([-a-zA-Z0-9@:%_\+.~#?&\/\/=]*)')
    allowed_list = ['github.com', 'microsoft.com', 'visualstudio.com', 'aka.ms', 'azure.com']
    for link in all_links:
        matches = re.findall(url_pattern, link)
        
        if matches and any(allowed in link.lower() for allowed in allowed_list):
            urls.append(link)
    return urls

def get_paths_from_links(all_links: list) -> list:
    """function to get relative paths from a list
    flags paths that start with ./ or ../
    """
    paths = []
    path_pattern = re.compile(r'(\.{1,2}\/)+([A-Za-z0-9-]+\/)*(.+\.[A-Za-z]+)')

    for link in all_links:
        link = link.split(" ")[0]
        matches = re.findall(path_pattern, link)
        if matches:
            paths.append(link)
    return paths

def check_paths_exists(file_path : str, paths : list) -> list:
    """function checks if a path exist if not return non existent paths
    flags any relative path that can't be accessed
    """
    broken_path = []
    for path in paths:
        path = re.sub(r'(\?|\&)(WT|wt)\.mc_id=.*', '', path)
        if not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(file_path), path))):
            broken_path.append(path)
    return broken_path

def check_url_locale(urls : list) -> list:
    """function checks if a url has country locale
    flags urls that have ==> /en-us/
    """
    country_locale = []
    for url in urls:
        locale_pattern = re.compile(r'\/[a-z]{2}-[a-z]{2}\/')
        matches = re.findall(locale_pattern, url)
        if matches:
            country_locale.append(url)
    return country_locale

def check_url_tracking(urls : list) -> list:
    """function checks if a url has tracking id
    flags urls missing ==> (? or &) plus WT.mc_id= or wt.mc_id=
    """
    tracking_id = []
    for url in urls:
        tracking_pattern = re.compile(r'(\?|\&)(WT|wt)\.mc_id=')
        matches = re.findall(tracking_pattern, url)
        if not matches:
            tracking_id.append(url)
    return tracking_id

# DEPRECATED
def get_urls_from_file(file_path: str) -> list:
    """function to get an array of urls from a file"""
    urls = []
    with open(file_path, 'r',  encoding="utf-8") as file:
        data = file.read()
        url_pattern = re.compile(r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9]{1,6}\b([-a-zA-Z0-9@:%_\+.~#?&\/\/=]*)')
        matches = re.finditer(url_pattern, data)
        for matched_group in matches:
            urls.append(matched_group.group())
    return urls

def get_paths_from_file(file_path: str) -> list:
    """function to get relative paths from a file"""
    paths = []
    with open(file_path, 'r',  encoding="utf-8") as file:
        data = file.read()
        path_pattern = re.compile(r'(\.{1,2}\/)+([A-Za-z0-9-]+\/)*([A-Za-z0-9]+\.[A-Za-z]+)')
        matches = re.finditer(path_pattern, data)
        for matched_group in matches:
            paths.append(matched_group.group())
    return paths