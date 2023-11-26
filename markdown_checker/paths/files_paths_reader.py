"""
This module contains a function to get a list of file paths from a root directory and
its subdirectories, filtered by file extension.

The main function in this module is `get_files_paths_list`.

Functions:
- get_files_paths_list(root_path: str, extension: list = None) -> list
"""

import os

def get_files_paths_list(root_path: str, extensions: list = None) -> list:
    """
    function returns a list of files in a directory and its subdirectories,
    filtered by file extensions.

    Keyword arguments:
    root_path (str): The root directory from which to start the search.
    extensions (list, optional): A list of file extensions to filter by.
    Defaults to [".md", ".ipynb"].

    Returns:
    list: A list of file paths that match the given file extensions.
    """
    if extensions is None:
        extensions = [".md", ".ipynb"]

    sub_folders, files_paths = [], []

    for f in os.scandir(root_path):
        if f.is_dir():
            sub_folders.append(f.path)
        if f.is_file():
            if os.path.splitext(f.name)[1].lower() in extensions:
                files_paths.append(f.path)

    for directory in list(sub_folders):
        sf, f = get_files_paths_list(directory, extensions)
        sub_folders.extend(sf)
        files_paths.extend(f)
    return sub_folders, files_paths
