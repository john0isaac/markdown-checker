How to Tune URL Checking for Large Repos
============================================

Goal: reduce rate-limiting and access warnings when running
``check_broken_urls`` (or ``check_urls_locale``/``check_urls_tracking``)
against a large repository with many links.

Recognise the warnings
-------------------------

Warnings never fail the run (only broken links do), but a large number of
them usually means the host is throttling or blocking the checker rather
than the links actually being broken:

.. code-block:: text

    ⚠ 3 links had warnings:
        File 'docs/index.md', line 12
    https://example.com/api was skipped due to rate limiting.

        File 'docs/index.md', line 15
    https://example.com/a/123 could not be verified (access was forbidden by the server).

See :doc:`../reference/exit-codes` for what each warning status means, and
:doc:`../explanation/url-checking` for why they happen.

Slow down requests to a single host
---------------------------------------

If many links point at the same host, increase the pacing delay between
requests to it:

.. code-block:: bash

    markdown-checker . -f check_broken_urls --per-host-delay=1.0

Reduce concurrency
--------------------

Fewer concurrent workers means fewer simultaneous requests overall,
including across different hosts:

.. code-block:: bash

    markdown-checker . -f check_broken_urls --max-workers=4

In GitHub Actions, ``--max-workers`` defaults to the number of available
CPUs rather than ``10``, which can be more aggressive on larger runners -
pass an explicit value to override it.

Adjust retries and timeouts
--------------------------------

.. code-block:: bash

    # Wait longer per request, retry hard failures more times
    markdown-checker . -f check_broken_urls --timeout=30 --retries=5

    # Wait longer before retrying a 429 with no Retry-After header
    markdown-checker . -f check_broken_urls --fallback-retry-delay=60

Give up on a host entirely
------------------------------

If a domain consistently blocks automated requests (e.g. it always returns
403), stop checking it rather than tuning around it - see
:doc:`skip-links`.

Verify it worked
------------------

Re-run the check and compare the warning count in the
"``N`` links had warnings" summary line before and after your change.
