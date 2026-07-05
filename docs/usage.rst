Usage
=====

The library provides the following functions.

.. contents:: Available checks
    :local:

``check_broken_paths``
----------------------

This function ensures that any relative path in your files is working.

Example
~~~~~~~

.. code-block:: bash

    markdown-checker -d . -f check_broken_paths -gu https://github.com/john0isaac/markdown-checker/blob/main/docs/CONTRIBUTING.rst

``check_broken_urls``
---------------------

This function ensures that any web URL in your files is working and returns a
200 status code.

Example
~~~~~~~

.. code-block:: bash

    markdown-checker -d . -f check_broken_urls -gu https://github.com/john0isaac/markdown-checker/blob/main/docs/CONTRIBUTING.rst

``check_urls_locale``
---------------------

This function checks whether a country-specific locale is present in URLs.

Example
~~~~~~~

.. code-block:: bash

    markdown-checker -d . -f check_urls_locale -gu https://github.com/john0isaac/markdown-checker/blob/main/docs/CONTRIBUTING.rst

``check_paths_tracking``
------------------------

This function ensures that any relative path has tracking in it.

Example
~~~~~~~

.. code-block:: bash

    markdown-checker -d . -f check_paths_tracking -gu https://github.com/john0isaac/markdown-checker/blob/main/docs/CONTRIBUTING.rst

``check_urls_tracking``
-----------------------

This function ensures that any URL has tracking in it.

Example
~~~~~~~

.. code-block:: bash

    markdown-checker -d . -f check_urls_tracking -gu https://github.com/john0isaac/markdown-checker/blob/main/docs/CONTRIBUTING.rst

Configuration
-------------

Every CLI option can also be set in a ``[tool.markdown-checker]`` table in
``pyproject.toml``, so you don't have to repeat flags in every command or
workflow file. Keys are hyphenated and mirror the long option names:

.. code-block:: toml

    [tool.markdown-checker]
    func = "check_broken_urls"
    dir = "."
    extensions = [".md", ".ipynb"]
    skip-files = ["CODE_OF_CONDUCT.md", "SECURITY.md"]
    skip-domains = []
    tracking-domains = ["github.com", "microsoft.com", "visualstudio.com", "aka.ms", "azure.com"]
    guide-url = "https://github.com/john0isaac/markdown-checker/blob/main/docs/CONTRIBUTING.rst"
    timeout = 20
    retries = 3
    retry-on-429 = true
    max-workers = 10
    report-format = "markdown"

Precedence is: a value passed on the command line always wins, then the value
from ``pyproject.toml``, then the built-in default. An option that is required
(``-f``/``--func``) can be satisfied entirely from ``pyproject.toml``.

Use ``-c``/``--config PATH`` to read from a specific TOML file instead of the
nearest ``pyproject.toml``, or ``--isolated`` to ignore configuration files
entirely for a single run.

Want to do more?
----------------

Check out the :doc:`Advanced Usage <advanced>` page.
