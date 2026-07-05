from pallets_sphinx_themes import get_version
from pallets_sphinx_themes import ProjectLink

# Project --------------------------------------------------------------

project = "markdown-checker"
copyright = "2023 John Aziz"
author = "John Aziz"
release, version = get_version("markdown-checker")

# General --------------------------------------------------------------

default_role = "code"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinxcontrib.log_cabinet",
    "sphinx_tabs.tabs",
    "sphinx_copybutton",
    "pallets_sphinx_themes",
]
autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_preserve_defaults = True
autodoc_default_options = {
    "no-value": True,
}
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_use_rtype = False
extlinks = {
    "issue": ("https://github.com/john0isaac/markdown-checker/issues/%s", "#%s"),
    "pr": ("https://github.com/john0isaac/markdown-checker/pull/%s", "#%s"),
    "ghsa": (
        "https://github.com/john0isaac/markdown-checker/security/advisories/GHSA-%s",
        "GHSA-%s",
    ),
}
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
}

# HTML -----------------------------------------------------------------

html_theme = "werkzeug"
html_theme_options = {"index_sidebar_logo": False}
html_context = {
    "project_links": [
        ProjectLink("Donate", "https://github.com/sponsors/john0isaac/"),
        ProjectLink("PyPI Releases", "https://pypi.org/project/markdown-checker/"),
        ProjectLink("Source Code", "https://github.com/john0isaac/markdown-checker/"),
        ProjectLink("Issue Tracker", "https://github.com/john0isaac/markdown-checker/issues/"),
    ]
}
html_sidebars = {
    "index": ["project.html", "localtoc.html", "searchbox.html", "ethicalads.html"],
    "**": ["localtoc.html", "relations.html", "searchbox.html", "ethicalads.html"],
}
singlehtml_sidebars = {"index": ["project.html", "localtoc.html", "ethicalads.html"]}
html_title = f"{project} Documentation ({version})"
html_show_sourcelink = False
