How to Select Which Files Are Checked
=====================================

Goal: control exactly which files markdown-checker looks at.

Check a directory or specific files
--------------------------------------

Pass one or more paths as positional ``SRC`` arguments - this is the
preferred way to select what to check. Each argument may be a file or a
directory (directories are searched recursively):

.. code-block:: bash

    # A whole directory
    markdown-checker . -f check_broken_paths

    # Specific files and directories together
    markdown-checker README.md docs/ -f check_broken_paths

``-d``/``--dir`` is kept only for backward compatibility and accepts a
single directory; prefer ``SRC`` for new commands and workflows:

.. code-block:: bash

    markdown-checker -d . -f check_broken_paths

Either ``SRC`` or ``-d``/``--dir`` must be given; providing neither is a
usage error.

Filter by file extension
--------------------------

By default, only ``.md`` and ``.ipynb`` files are considered. Use
``-ext``/``--extensions`` to change that:

.. code-block:: bash

    # Only markdown files, no notebooks
    markdown-checker . -f check_broken_paths --extensions=.md

See :doc:`../reference/cli` for the exact comma-separated list syntax.

Skip specific files by name
------------------------------

Use ``-sf``/``--skip-files`` to exclude files by name (not path), regardless
of which directory they're in:

.. code-block:: bash

    markdown-checker . -f check_broken_paths --skip-files=CHANGELOG.md,LICENSE.md

The default skip list is ``CODE_OF_CONDUCT.md,SECURITY.md`` - pass your own
list to replace it (it is not merged with the default).

Verify it worked
------------------

The "Checked N links in M files" summary line reports how many files were
actually scanned; confirm ``M`` matches what you expect before relying on
the result.
