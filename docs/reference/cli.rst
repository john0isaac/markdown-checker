Command-Line Options
======================

Every option can also be set via ``pyproject.toml`` - see
:doc:`configuration`. Command-line values always take precedence.

.. contents:: On this page
    :local:

``SRC ...``
------------

Type
  ``click.Path`` (positional, variadic; existing files or directories).
Default
  None.
Constraints
  Either ``SRC`` or ``-d``/``--dir`` must be provided. Preferred over
  ``-d``/``--dir`` for new commands and workflows.
Description
  One or more specific files or directories to check.

.. code-block:: bash

    markdown-checker README.md docs/ -f check_broken_paths

``-d``, ``--dir``
--------------------

Type
  ``click.Path`` (existing directory).
Default
  None.
Constraints
  Either ``SRC`` or ``-d``/``--dir`` must be provided. Kept for backward
  compatibility; accepts only a single directory, unlike ``SRC``.
Description
  Root directory to search recursively for matching files.

.. code-block:: bash

    markdown-checker -d . -f check_broken_paths

``-f``, ``--func``
--------------------

Type
  ``click.Choice``.
Default
  None.
Constraints
  Required. One of ``check_broken_paths``, ``check_broken_urls``,
  ``check_paths_tracking``, ``check_urls_tracking``, ``check_urls_locale``.
Description
  Which check to run. See :doc:`checks` for what each one does.

``-ext``, ``--extensions``
-----------------------------

Type
  ``list[str]``, comma-separated.
Default
  ``.md,.ipynb``.
Constraints
  None.
Description
  File extensions to include when searching ``SRC``/``--dir`` directories.

.. code-block:: bash

    markdown-checker . -f check_broken_paths --extensions=.md,.ipynb,.txt

``-td``, ``--tracking-domains``
-----------------------------------

Type
  ``list[str]``, comma-separated.
Default
  ``github.com,microsoft.com,visualstudio.com,aka.ms,azure.com``.
Constraints
  Only affects ``check_urls_tracking``.
Description
  Hostnames that must carry a ``wt.mc_id`` tracking parameter.

.. code-block:: bash

    markdown-checker . -f check_urls_tracking --tracking-domains=github.com,microsoft.com

``-sf``, ``--skip-files``
-----------------------------

Type
  ``list[str]``, comma-separated.
Default
  ``CODE_OF_CONDUCT.md,SECURITY.md``.
Constraints
  Matches by file name, not path.
Description
  File names to exclude from checking.

.. code-block:: bash

    markdown-checker . -f check_broken_paths --skip-files=README.md,CHANGELOG.md

``-sd``, ``--skip-domains``
-------------------------------

Type
  ``list[str]``, comma-separated.
Default
  ``[]`` (none).
Constraints
  Only affects ``check_broken_urls`` and ``check_urls_locale``. Substring
  match against the URL's hostname.
Description
  Domains to exclude from URL checks.

.. code-block:: bash

    markdown-checker . -f check_broken_urls --skip-domains=example.com,test.com

``-suc``, ``--skip-urls-containing``
----------------------------------------

Type
  ``list[str]``, comma-separated.
Default
  ``[]`` (none).
Constraints
  Only affects ``check_broken_urls`` and ``check_urls_locale``. Substring
  match against the full URL.
Description
  URL substrings to exclude from URL checks.

.. code-block:: bash

    markdown-checker . -f check_broken_urls --skip-urls-containing=/embed/,/preview/

``-gu``, ``--guide-url``
----------------------------

Type
  ``str``.
Default
  None.
Constraints
  None.
Description
  Full URL of your contributing guide, included as a link in the Markdown
  report (see :doc:`report-formats`).

``-to``, ``--timeout``
--------------------------

Type
  ``click.IntRange``.
Default
  ``20``.
Constraints
  ``0-50`` (seconds).
Description
  Per-request timeout for URL checks.

``-rt``, ``--retries``
--------------------------

Type
  ``click.IntRange``.
Default
  ``3``.
Constraints
  ``0-10``.
Description
  Number of attempts before a URL is reported as ``broken``. Does not apply
  to rate-limit/auth responses, which return immediately regardless of this
  value - see :doc:`../explanation/url-checking`.

``--retry-on-429`` / ``--no-retry-on-429``
-----------------------------------------------

Type
  ``bool`` flag.
Default
  Enabled (``--retry-on-429``).
Constraints
  Only affects URL checks.
Description
  When enabled, a 429 (or any non-success response carrying a
  ``Retry-After`` header) is reported immediately as ``rate_limited``
  instead of being retried with exponential backoff.

.. code-block:: bash

    markdown-checker . -f check_broken_urls --no-retry-on-429

``-frd``, ``--fallback-retry-delay``
----------------------------------------

Type
  ``click.IntRange``.
Default
  ``30``.
Constraints
  ``0-300`` (seconds). Only used when ``--retry-on-429`` is enabled and the
  429 response has no ``Retry-After`` header.
Description
  Seconds reported as the retry delay when a 429 carries no
  ``Retry-After`` header.

``-mw``, ``--max-workers``
------------------------------

Type
  ``click.IntRange``.
Default
  ``10``, or the number of available CPUs when ``$GITHUB_ACTIONS=true``.
Constraints
  ``1`` or greater.
Description
  Maximum number of concurrent URL-check worker threads.

.. code-block:: bash

    markdown-checker . -f check_broken_urls --max-workers=20

``-phd``, ``--per-host-delay``
----------------------------------

Type
  ``click.FloatRange``.
Default
  ``0.5``.
Constraints
  ``0.0-10.0`` (seconds).
Description
  Minimum delay enforced between two requests to the same host.

``-o``, ``--output-file-name``
----------------------------------

Type
  ``str``.
Default
  ``comment``.
Constraints
  Use ``-`` to write to stdout instead of a file.
Description
  Base name (without extension) of the report file. The renderer's
  extension is appended automatically (e.g. ``.md`` for markdown, ``.json``
  for JSON).

``-rf``, ``--report-format``
--------------------------------

Type
  ``click.Choice``.
Default
  ``markdown``.
Constraints
  One of ``console``, ``github-annotations``, ``json``, ``markdown``.
Description
  Report format written when error-level issues are found. See
  :doc:`report-formats` for the shape of each.

``-c``, ``--config``
------------------------

Type
  ``click.Path`` (existing file).
Default
  Nearest ``pyproject.toml``, discovered by walking up from the current
  directory.
Constraints
  Mutually exclusive in effect with ``--isolated``.
Description
  Read ``[tool.markdown-checker]`` from this file instead of discovering
  ``pyproject.toml``. See :doc:`configuration`.

``--isolated``
------------------

Type
  ``bool`` flag.
Default
  Disabled.
Constraints
  None.
Description
  Ignore ``pyproject.toml`` configuration entirely for this run.

``--version``
----------------

Type
  ``bool`` flag.
Description
  Show the version and exit.

``--help``
-------------

Type
  ``bool`` flag.
Description
  Show the help message and exit.
