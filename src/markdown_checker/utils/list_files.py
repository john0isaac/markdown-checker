"""
This module contains a function to get a list of file paths from a root directory and
its subdirectories, filtered by file extension.
"""

import os
from pathlib import Path


def get_files_paths_list(root_path: Path, extensions: list[str] = []) -> tuple[list[Path], list[Path]]:
    """
    Get a list of file paths from a root directory and its subdirectories, filtered by file extension.

    Args:
        - root_path (Path): The root directory to start the search.
        - extensions (list[str]): A list of file extensions to filter the search.

    Returns:
        - tuple[list[Path], list[Path]]: A tuple containing a list of subdirectories and a list of file paths.
    """

    sub_folders: list[Path] = []
    files_paths: list[Path] = []

    for f in os.scandir(root_path):
        if f.is_dir():
            sub_folders.append(Path(f.path))
        if f.is_file():
            if os.path.splitext(f.name)[1].lower() in extensions:
                files_paths.append(Path(f.path))

    for directory in list(sub_folders):
        sub_dir_sub_folders, sub_dir_file_paths = get_files_paths_list(directory, extensions)
        sub_folders.extend(sub_dir_sub_folders)
        files_paths.extend(sub_dir_file_paths)
    return sub_folders, files_paths
