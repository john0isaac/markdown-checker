#!/usr/bin/env python3
"""
Module providing automatic checks functionality to markdown files 
following some Guidelines
"""
import os
from markdown_checker.get_input_args.get_input_args import get_input_args
from markdown_checker.markdown_checker import get_lessons_paths, check_broken_links

def main() -> None:
    """Main program get inputs and run checks"""

    # get input arguments directory, function to run
    in_arg = get_input_args()

    lessons = get_lessons_paths(in_arg.dir)

    # iterate over the files to validate the content
    for lesson_folder_name, lessons_array in lessons.items():
        for lesson_file_name in lessons_array:
            file_path = os.path.join(
                in_arg.dir,
                lesson_folder_name,
                lesson_file_name)
            if in_arg.dir == lesson_folder_name:
                file_path = os.path.join(lesson_folder_name, lesson_file_name)
            if "check_broken_paths" in in_arg.func:
                formatted_output = check_broken_links(file_path, "path" , "broken")
                if formatted_output:
                    print(formatted_output)
            if "check_paths_tracking" in in_arg.func:
                formatted_output = check_broken_links(file_path, "path" , "tracking")
                if formatted_output:
                    print(formatted_output)
            if "check_urls_tracking" in in_arg.func:
                formatted_output = check_broken_links(file_path, "url" , "tracking")
                if formatted_output:
                    print(formatted_output)
            if "check_urls_locale" in in_arg.func:
                formatted_output = check_broken_links(file_path, "url" , "locale")
                if formatted_output:
                    print(formatted_output)

if __name__ == "__main__":
    main()
