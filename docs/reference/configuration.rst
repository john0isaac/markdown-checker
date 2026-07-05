Configuration File Reference
================================

markdown-checker reads defaults from a ``[tool.markdown-checker]`` table in
``pyproject.toml``. Keys are hyphenated and mirror the long CLI option
names. See :doc:`../howto/pyproject-config` for a task-oriented walkthrough.

Precedence
------------

1. Command-line flags.
2. ``[tool.markdown-checker]`` in the resolved ``pyproject.toml`` (or the
   file passed via ``-c``/``--config``).
3. Built-in defaults (see :doc:`cli`).

``--isolated`` skips step 2 entirely.

Discovery
-----------

Without ``-c``/``--config``, markdown-checker walks up from the current
directory and uses the first ``pyproject.toml`` it finds, whether or not it
contains a ``[tool.markdown-checker]`` table.

Unknown keys under ``[tool.markdown-checker]`` are a hard error - this
catches typos immediately rather than silently ignoring them.

Keys
------

.. list-table::
   :header-rows: 1
   :widths: 30 25 45

   * - Key
     - CLI flag
     - Type
   * - ``func``
     - ``--func``
     - string
   * - ``dir``
     - ``--dir``
     - string (path)
   * - ``extensions``
     - ``--extensions``
     - array of strings
   * - ``tracking-domains``
     - ``--tracking-domains``
     - array of strings
   * - ``skip-files``
     - ``--skip-files``
     - array of strings
   * - ``skip-domains``
     - ``--skip-domains``
     - array of strings
   * - ``skip-urls-containing``
     - ``--skip-urls-containing``
     - array of strings
   * - ``guide-url``
     - ``--guide-url``
     - string
   * - ``timeout``
     - ``--timeout``
     - integer
   * - ``retries``
     - ``--retries``
     - integer
   * - ``retry-on-429``
     - ``--retry-on-429``/``--no-retry-on-429``
     - boolean
   * - ``fallback-retry-delay``
     - ``--fallback-retry-delay``
     - integer
   * - ``max-workers``
     - ``--max-workers``
     - integer
   * - ``per-host-delay``
     - ``--per-host-delay``
     - float
   * - ``output-file-name``
     - ``--output-file-name``
     - string
   * - ``report-format``
     - ``--report-format``
     - string

Example
---------

.. code-block:: toml

    [tool.markdown-checker]
    func = "check_broken_urls"
    dir = "."
    extensions = [".md", ".ipynb"]
    skip-files = ["CODE_OF_CONDUCT.md", "SECURITY.md"]
    skip-domains = []
    tracking-domains = ["github.com", "microsoft.com", "visualstudio.com", "aka.ms", "azure.com"]
    guide-url = "https://github.com/john0isaac/markdown-checker/blob/main/CONTRIBUTING.md"
    timeout = 20
    retries = 3
    retry-on-429 = true
    max-workers = 10
    report-format = "markdown"
