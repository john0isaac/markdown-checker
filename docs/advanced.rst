Advanced Usage
==============

To further customize your experience with Markdown Checker, you can use
additional command-line interface options.

.. contents:: On this page
  :local:

Working with List Parameters
----------------------------

Several CLI options accept lists of values, including ``--skip-domains``,
``--skip-files``, ``--extensions``, ``--tracking-domains``, and
``--skip-urls-containing``.

How to provide multiple values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use comma-separated values without spaces:

.. code-block:: bash

  markdown-checker -d . -f check_broken_urls --skip-domains=example.com,test.com

Important formatting rules
~~~~~~~~~~~~~~~~~~~~~~~~~~

- Values must be separated by commas with no spaces.
- Do not use square brackets.
- Do not add spaces after commas.
- Quotes are optional but not required.

Examples of correct and incorrect usage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Wrong: ``--skip-domains=[example.com,test.com]``. Square brackets are not
  allowed.
- Wrong: ``--skip-domains=example.com, test.com``. Spaces are not allowed.
- Wrong: ``--skip-domains example.com test.com``. Use ``=`` and commas.
- Correct: ``--skip-domains=example.com,test.com``.
- Correct: ``--skip-domains="example.com,test.com"``. Quotes are optional.

Command Line Options
--------------------

``SRC ...``
~~~~~~~~~~~

Type
  ``click.Path``
Description
  Source files or directories to check.
Required
  No. Either ``SRC`` or ``--dir`` must be provided.

``-d``, ``--dir``
~~~~~~~~~~~~~~~~~

Type
  ``click.Path``
Description
  Path to the root directory to check.
Required
  No. Either ``SRC`` or ``--dir`` must be provided.

``-f``, ``--func``
~~~~~~~~~~~~~~~~~~

Type
  ``click.Choice``
Description
  Function to execute.
Choices
  ``check_broken_paths``, ``check_broken_urls``, ``check_paths_tracking``,
  ``check_urls_tracking``, ``check_urls_locale``
Required
  Yes.

``-ext``, ``--extensions``
~~~~~~~~~~~~~~~~~~~~~~~~~~

Type
  ``list[str]``
Description
  File extensions used to filter the files.
Default
  ``.md``, ``.ipynb``
Required
  No.

Usage examples
^^^^^^^^^^^^^^

.. code-block:: bash

  # Single value
  markdown-checker -d . -f check_broken_paths --extensions=.md

  # Multiple values (comma-separated, no spaces)
  markdown-checker -d . -f check_broken_paths --extensions=.md,.ipynb,.txt

``-td``, ``--tracking-domains``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Type
  ``list[str]``
Description
  List of tracking domains to check.
Default
  ``github.com``, ``microsoft.com``, ``visualstudio.com``, ``aka.ms``,
  ``azure.com``
Required
  No.

Usage examples
^^^^^^^^^^^^^^

.. code-block:: bash

  # Single value
  markdown-checker -d . -f check_urls_tracking --tracking-domains=github.com

  # Multiple values (comma-separated, no spaces)
  markdown-checker -d . -f check_urls_tracking --tracking-domains=github.com,microsoft.com

``-sf``, ``--skip-files``
~~~~~~~~~~~~~~~~~~~~~~~~~

Type
  ``list[str]``
Description
  List of file names to skip.
Default
  ``CODE_OF_CONDUCT.md``, ``SECURITY.md``
Required
  No.

Usage examples
^^^^^^^^^^^^^^

.. code-block:: bash

  # Single value
  markdown-checker -d . -f check_broken_paths --skip-files=README.md

  # Multiple values (comma-separated, no spaces)
  markdown-checker -d . -f check_broken_paths --skip-files=README.md,CHANGELOG.md,LICENSE.md

``-sd``, ``--skip-domains``
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Type
  ``list[str]``
Description
  List of domains to skip during checking.
Default
  ``[]``
Required
  No.

Usage examples
^^^^^^^^^^^^^^

.. code-block:: bash

  # Single value
  markdown-checker -d . -f check_broken_urls --skip-domains=example.com

  # Multiple values (comma-separated, no spaces)
  markdown-checker -d . -f check_broken_urls --skip-domains=example.com,test.com

``-suc``, ``--skip-urls-containing``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Type
  ``list[str]``
Description
  List of URL substrings to skip.
Default
  ``[]``
Required
  No.

Usage examples
^^^^^^^^^^^^^^

.. code-block:: bash

  # Single value
  markdown-checker -d . -f check_broken_urls --skip-urls-containing=/embed/

  # Multiple values (comma-separated, no spaces)
  markdown-checker -d . -f check_broken_urls --skip-urls-containing=/embed/,/preview/,video-embed.html

``-gu``, ``--guide-url``
~~~~~~~~~~~~~~~~~~~~~~~~

Type
  ``str``
Description
  Full URL of your contributing guide.
Required
  No.

``-to``, ``--timeout``
~~~~~~~~~~~~~~~~~~~~~~

Type
  ``Click.IntRange``
Description
  Timeout in seconds for requests before retrying.
Default
  ``20``
Range
  ``0-50``
Required
  No.

``-rt``, ``--retries``
~~~~~~~~~~~~~~~~~~~~~~

Type
  ``Click.IntRange``
Description
  Number of retries before flagging a URL as broken.
Default
  ``3``
Range
  ``0-10``
Required
  No.

``-o``, ``--output-file-name``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Type
  ``str``
Description
  Name of the output file.
Default
  ``comment``
Required
  No.

Other Options
-------------

``--version``
~~~~~~~~~~~~~

Type
  ``bool``
Description
  Show the version and exit.
Required
  No.

``--help``
~~~~~~~~~~

Type
  ``bool``
Description
  Show the help message and exit.
Required
  No.
