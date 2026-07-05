How to Choose a Report Format
================================

Goal: pick the right ``--report-format`` for how you plan to consume the
results.

Write the default Markdown report
------------------------------------

With no flags, error-level issues are written to ``comment.md`` in the
current directory - the format used by the `action-check-markdown
<https://github.com/marketplace/actions/check-markdown>`_ GitHub Action to
post a pull request comment:

.. code-block:: bash

    markdown-checker . -f check_broken_paths

Write a different file name
--------------------------------

.. code-block:: bash

    markdown-checker . -f check_broken_paths -o report

This writes ``report.md`` (the renderer's file extension is appended
automatically).

Print to stdout instead of a file
--------------------------------------

Use ``-`` as the output file name:

.. code-block:: bash

    markdown-checker . -f check_broken_paths -o -

Generate machine-readable JSON
----------------------------------

Use ``-rf json`` to get a structured report - including both errors and
warnings, unlike the Markdown format:

.. code-block:: bash

    markdown-checker . -f check_broken_urls -rf json -o report

Then process it with ``jq`` or any JSON tool:

.. code-block:: bash

    jq '.summary, .files[].issues[]' report.json

Emit GitHub Actions annotations
------------------------------------

If you're calling ``markdown-checker`` directly from a workflow step
(rather than through the wrapper action), use ``-rf github-annotations`` to
get ``::error``/``::warning`` lines that GitHub renders inline on the diff:

.. code-block:: bash

    markdown-checker . -f check_broken_urls -rf github-annotations -o -

See :doc:`github-actions` for a full workflow example.

See :doc:`../reference/report-formats` for the exact shape of each format's
output.
