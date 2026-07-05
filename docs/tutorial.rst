Tutorial: Your First Link Check
================================

This tutorial walks you through installing markdown-checker and running it
against a small sample project, so you can see exactly what it does before
reaching for the how-to guides or reference pages.

Prerequisites
--------------

- Python 3.11 or later.

Install
-------

.. code-block:: bash

    pip install markdown-checker

Confirm it installed correctly:

.. code-block:: bash

    markdown-checker --version

1. Create a sample project
---------------------------

Create a new directory and add two files: a markdown file with one working
link and one broken link, and the file it links to.

``docs-sample/index.md``:

.. code-block:: markdown

    # Sample Project

    See the [usage guide](./usage.md) for instructions.

    See the [missing guide](./missing.md) for more details.

``docs-sample/usage.md``:

.. code-block:: markdown

    # Usage

    Nothing to see here yet.

2. Check for broken paths
--------------------------

Run the ``check_broken_paths`` check against the directory:

.. code-block:: bash

    markdown-checker docs-sample -f check_broken_paths

You'll see output similar to:

.. code-block:: text

    🔍 Checked 2 links in 2 files.
    😭 Found 1 issues in the following files:
        File 'docs-sample/index.md', line 5
    ./missing.md is broken.

Because an error-level issue was found, markdown-checker also writes a
``comment.md`` file in the current directory with the same information as a
Markdown table, and the command exits with status ``1``:

.. code-block:: bash

    echo $?
    # 1

Fix the broken link (or create ``docs-sample/missing.md``) and re-run the
command. With no issues, you'll see:

.. code-block:: text

    🔍 Checked 2 links in 2 files.
    All files are compliant with the guidelines. 🎉

and the command exits ``0``. No ``comment.md`` is written when there are no
issues.

3. Check URLs
-------------

Add a URL to ``docs-sample/index.md``:

.. code-block:: markdown

    See the [markdown-checker repository](https://github.com/john0isaac/markdown-checker).

Run the ``check_broken_urls`` check instead:

.. code-block:: bash

    markdown-checker docs-sample -f check_broken_urls

This time each URL is actually requested over the network. If a URL returns
an error status, it's reported the same way broken paths are; if a host
rate-limits or blocks the request, it's reported as a **warning** instead of
an error and does not fail the run. See
:doc:`explanation/url-checking` for why.

4. Read the report
-------------------

Open ``comment.md`` from step 2 (or re-trigger an issue to regenerate it).
It's a Markdown document with:

- A short header describing which check ran.
- An optional line linking to your contributing guide, if you passed
  ``--guide-url``.
- A table with one row per broken link: its file, the link itself, and the
  line number it was found on.

This is the same file the `action-check-markdown
<https://github.com/marketplace/actions/check-markdown>`_ GitHub Action
posts as a pull request comment - see
:doc:`howto/github-actions`.

Where next?
-----------

- :doc:`howto/index` for task-oriented guides (selecting files, configuring
  via ``pyproject.toml``, tuning rate limits, choosing report formats,
  running in GitHub Actions).
- :doc:`reference/checks` for exactly what each of the five checks flags.
- :doc:`reference/cli` for every command-line option.
- :doc:`explanation/index` to understand how URL checking and link
  detection work under the hood.
