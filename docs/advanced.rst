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

``--retry-on-429`` / ``--no-retry-on-429``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Type
  ``bool``
Description
  When enabled, the checker honours the ``Retry-After`` response header on
  ``429 Too Many Requests`` (and any other non-success, non-redirect response
  that carries the header). The indicated wait time is used instead of the
  normal exponential backoff. Disable with ``--no-retry-on-429`` to fall back
  to standard retry behaviour.
Default
  Enabled (``--retry-on-429``)
Required
  No.

Usage examples
^^^^^^^^^^^^^^

.. code-block:: bash

  # Enabled (default)
  markdown-checker -d . -f check_broken_urls --retry-on-429

  # Disabled
  markdown-checker -d . -f check_broken_urls --no-retry-on-429

``-frd``, ``--fallback-retry-delay``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Type
  ``Click.IntRange``
Description
  Number of seconds to wait before retrying when a ``429`` response is
  received but carries no ``Retry-After`` header. Only applies when
  ``--retry-on-429`` is enabled.
Default
  ``30``
Range
  ``0-300``
Required
  No.

Usage examples
^^^^^^^^^^^^^^

.. code-block:: bash

  # Use a custom fallback delay of 45 seconds
  markdown-checker -d . -f check_broken_urls --fallback-retry-delay=45

  # Short-form alias
  markdown-checker -d . -f check_broken_urls -frd 45

``-mw``, ``--max-workers``
~~~~~~~~~~~~~~~~~~~~~~~~~~

Type
  ``Click.IntRange``
Description
  Maximum number of concurrent URL-check workers.
Default
  ``10``, or the number of available CPUs when running in GitHub Actions
  (``$GITHUB_ACTIONS=true``).
Range
  ``1`` or greater.
Required
  No.

Usage examples
^^^^^^^^^^^^^^

.. code-block:: bash

  # Use a custom worker count
  markdown-checker -d . -f check_broken_urls --max-workers=20

  # Short-form alias
  markdown-checker -d . -f check_broken_urls -mw 20

``-phd``, ``--per-host-delay``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Type
  ``Click.FloatRange``
Description
  Minimum delay in seconds between requests to the same host.
Default
  ``0.5``
Range
  ``0.0-10.0``
Required
  No.

Usage examples
^^^^^^^^^^^^^^

.. code-block:: bash

  # Use a custom per-host delay of 1 second
  markdown-checker -d . -f check_broken_urls --per-host-delay=1.0

  # Short-form alias
  markdown-checker -d . -f check_broken_urls -phd 1.0

``-o``, ``--output-file-name``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Type
  ``str``
Description
  Name of the output file, without extension. Use ``-`` to write the report
  to stdout instead of a file.
Default
  ``comment``
Required
  No.

``-rf``, ``--report-format``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Type
  ``click.Choice``
Description
  Report format to generate when errors are found. The renderer's own file
  extension is appended to ``--output-file-name`` (e.g. ``comment.md`` for
  ``markdown``, ``comment.json`` for ``json``).
Choices
  ``markdown``, ``json``, ``github-annotations``, ``console``
Default
  ``markdown``
Required
  No.

Usage examples
^^^^^^^^^^^^^^

.. code-block:: bash

  # Default: writes comment.md
  markdown-checker -d . -f check_broken_urls

  # Machine-readable JSON report, written to report.json
  markdown-checker -d . -f check_broken_urls -rf json -o report

  # Write the rendered report to stdout instead of a file
  markdown-checker -d . -f check_broken_urls -rf json -o -

URL Check Outcomes
------------------

When ``check_broken_urls`` runs, each URL is evaluated by
``MarkdownURL.check()``, which returns a ``URLCheckResult`` with one of five
statuses.

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Status
     - Meaning
   * - ``alive``
     - A ``2xx`` HTTP response was received. The link is healthy.
   * - ``broken``
     - All retries returned non-``2xx`` responses (e.g. ``404 Not Found``).
       The link is reported as an issue.
   * - ``rate_limited``
     - No hard HTTP failure was observed, and at least one retry encountered
       ``429 Too Many Requests`` (with or without a ``Retry-After`` header).
       The link is reported as a **warning-level issue**
       (``issue_level="warning"``). It does not cause the CLI to exit with a
       non-zero code.
   * - ``transient_error``
     - No hard HTTP failure or rate-limit response was observed, and the
       attempts failed with network-level exceptions (e.g. DNS failure,
       connection timeout). The link is reported as a **warning-level issue**
       and does not cause the CLI to exit with a non-zero code.
   * - ``unverifiable``
     - Both HEAD and GET returned ``401 Unauthorized`` or ``403 Forbidden``.
       The server is reachable but is blocking automated access (e.g.
       Cloudflare bot protection). The real status of the resource cannot be
       determined. The link is reported as a **warning-level issue** and does
       not cause the CLI to exit with a non-zero code.

Rate limiting and access errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When one or more URLs are rate-limited, unverifiable, or cannot be reached due
to transient network failures, the CLI prints a yellow warning summary followed
by one warning line per affected link, after the error-level issues (if any).

In local mode::

  🔍 Checked 42 links in 10 files.
  ⚠ 3 links had warnings:
    File '/path/to/file.md', line 12
  https://example.com/api was skipped due to rate limiting.

    File '/path/to/file.md', line 15
  https://stackoverflow.com/a/123 could not be verified (access was forbidden by the server).

In CI mode (``$CI=true``), GitHub Actions ``::warning::`` annotations are
emitted instead::

  🔍 Checked 42 links in 10 files.
  ::warning file=path/to/file.md,line=12::File path/to/file.md, line 12, Link https://example.com/api was skipped due to rate limiting.
  ::warning file=path/to/file.md,line=15::File path/to/file.md, line 15, Link https://stackoverflow.com/a/123 could not be verified (access was forbidden by the server).

Warning-level issues do **not** cause the CLI to exit with a non-zero code.
Only error-level issues (broken links) cause a non-zero exit.

If a run mixes rate-limited responses with transient network failures, the
outcome is reported as ``rate_limited`` unless a hard HTTP failure is also
observed. Any hard HTTP failure causes the final outcome to be ``broken``.

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
