How to Configure via pyproject.toml
=====================================

Goal: stop repeating CLI flags in every command or CI workflow step by
setting defaults once in ``pyproject.toml``.

Add a configuration table
----------------------------

Add a ``[tool.markdown-checker]`` table to your project's
``pyproject.toml``. Keys are hyphenated and mirror the long option names:

.. code-block:: toml

    [tool.markdown-checker]
    func = "check_broken_urls"
    dir = "."
    extensions = [".md", ".ipynb"]
    skip-files = ["CODE_OF_CONDUCT.md", "SECURITY.md"]
    tracking-domains = ["github.com", "microsoft.com", "visualstudio.com", "aka.ms", "azure.com"]
    guide-url = "https://github.com/john0isaac/markdown-checker/blob/main/CONTRIBUTING.md"
    max-workers = 10
    report-format = "markdown"

With this in place, running plain ``markdown-checker`` picks up every value
above - including ``--func``, which is normally required.

Understand precedence
------------------------

1. A value passed on the command line always wins.
2. Otherwise, the value from ``pyproject.toml`` is used.
3. Otherwise, the built-in default applies.

Use a specific config file
------------------------------

To read from a file other than the nearest ``pyproject.toml`` (discovered by
walking up from the current directory), use ``-c``/``--config``:

.. code-block:: bash

    markdown-checker -c ./ci/markdown-checker.toml -f check_broken_paths .

Ignore configuration for one run
------------------------------------

Use ``--isolated`` to ignore every ``pyproject.toml`` for a single
invocation, falling back to CLI flags and built-in defaults only:

.. code-block:: bash

    markdown-checker --isolated -f check_broken_paths .

Verify it worked
------------------

Run ``markdown-checker --help`` from your project root - if a required
option like ``--func`` is satisfied without passing it explicitly, discovery
is working. An unknown key under ``[tool.markdown-checker]`` is a hard
error, so a typo will surface immediately rather than being silently ignored.

See :doc:`../reference/configuration` for the full key reference.
