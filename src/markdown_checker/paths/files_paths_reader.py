"""
This module contains a function to get a list of file paths from a root directory and
its subdirectories, filtered by file extension.

The main function in this module is `get_files_paths_list`.

Functions:
- get_files_paths_list(root_path: str, extension: list = []) -> list
"""

import os


def get_files_paths_list(root_path: str, extensions: list[str] = []) -> tuple[list[str], list[str]]:
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
    if len(extensions) == 0:
        extensions = [".md", ".ipynb"]

    sub_folders: list[str] = []
    files_paths: list[str] = []

    for f in os.scandir(root_path):
        if f.is_dir():
            sub_folders.append(f.path)
        if f.is_file():
            if os.path.splitext(f.name)[1].lower() in extensions:
                files_paths.append(f.path)

    for directory in list(sub_folders):
        sub_dir_sub_folders, sub_dir_file_paths = get_files_paths_list(directory, extensions)
        sub_folders.extend(sub_dir_sub_folders)
        files_paths.extend(sub_dir_file_paths)
    return sub_folders, files_paths
