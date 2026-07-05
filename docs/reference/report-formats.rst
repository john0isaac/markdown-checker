Report Format Reference
==========================

Set with ``-rf``/``--report-format``; see :doc:`../howto/report-formats`
for task-oriented guidance on choosing one.

.. list-table::
   :header-rows: 1
   :widths: 20 15 15 50

   * - Format
     - Value
     - Extension
     - Includes warnings?
   * - Markdown
     - ``markdown``
     - ``.md``
     - No (errors only)
   * - JSON
     - ``json``
     - ``.json``
     - Yes
   * - GitHub annotations
     - ``github-annotations``
     - ``.txt``
     - Yes
   * - Console
     - ``console``
     - ``.txt``
     - Yes

Markdown (default)
---------------------

A per-check header (e.g. "Check Broken URLs"), an optional line linking to
``--guide-url``, and an HTML table of **error-level issues only** with
columns: file path, link, line number. This is the format the
`action-check-markdown <https://github.com/marketplace/actions/check-markdown>`_
action posts as a pull request comment.

JSON
------

A structured document including both errors and warnings:

.. code-block:: json

    {
      "tool": {"name": "markdown-checker", "version": "1.2.0"},
      "check": "check_broken_urls",
      "summary": {
        "files_checked": 10,
        "links_checked": 42,
        "errors": 1,
        "warnings": 2
      },
      "files": [
        {
          "path": "docs/index.md",
          "issues": [
            {
              "link": "https://example.com/gone",
              "line": 8,
              "level": "error",
              "message": "is broken"
            }
          ]
        }
      ]
    }

GitHub annotations
---------------------

One line per issue (errors and warnings), in the format GitHub Actions
recognises as a workflow annotation:

.. code-block:: text

    ::error file=docs/index.md,line=8::File docs/index.md, line 8, Link https://example.com/gone is broken.
    ::warning file=docs/index.md,line=12::File docs/index.md, line 12, Link https://example.com/api was skipped due to rate limiting.

Console
---------

Plain, human-readable text blocks - one per issue, errors and warnings both
included:

.. code-block:: text

    File '/abs/path/docs/index.md', line 8
    https://example.com/gone is broken.

This is also what's printed to the terminal automatically in local
(non-CI) mode, independent of ``--report-format``.
