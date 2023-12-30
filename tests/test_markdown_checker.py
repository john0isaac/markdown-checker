"""
Module to check paths in markdown files.
"""

import subprocess

def check_broken_paths():
    """
    Function to check for broken paths.
    """
    print("check_broken_paths was called")
    subprocess.run(["markdown-checker", "-d", "./tests/resources/", "-f", "check_broken_paths"], check=False)

def check_paths_tracking():
    """
    Function to check paths tracking.
    """
    print("check_paths_tracking was called")
    subprocess.run(["markdown-checker", "-d", "./tests/resources/", "-f", "check_paths_tracking"], check=False)

def check_urls_tracking():
    """
    Function to check URLs tracking.
    """
    print("check_urls_tracking was called")
    subprocess.run(["markdown-checker", "-d", "./tests/resources/", "-f", "check_urls_tracking"], check=False)

def check_urls_locale():
    """
    Function to check URLs locale.
    """
    print("check_urls_locale was called")
    subprocess.run(["markdown-checker", "-d", "./tests/resources/", "-f", "check_urls_locale"], check=False)

mydict = {1:check_broken_paths, 2:check_paths_tracking, 3:check_urls_tracking, 4:check_urls_locale}

try:
    choices = list(map(int,input("Do you want to: \n(1) Run check_broken_paths \n(2) Run check_paths_tracking \n(3) Run check_urls_tracking \n(4) Run check_urls_locale \n").split()))
except ValueError:
    print("Please input number")

for choice in choices:
    if 0 < choice and choice < 5:
        mydict[choice]()
    else:
        print("That is not between 1 and 4! Try again:")
