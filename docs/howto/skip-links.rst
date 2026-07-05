How to Skip Domains and URLs
==============================

Goal: exclude specific domains or URL patterns from a check without
removing the link from your markdown.

This applies to ``check_broken_urls`` and ``check_urls_locale``, which both
support ``--skip-domains`` and ``--skip-urls-containing``.

Skip a domain entirely
-------------------------

Use ``-sd``/``--skip-domains`` when a domain is known to be unreliable to
check automatically (e.g. it blocks bots) but you still want to keep the link:

.. code-block:: bash

    markdown-checker . -f check_broken_urls --skip-domains=example.com,test.com

Matching is a substring match against the URL's hostname, so
``--skip-domains=example.com`` also matches ``www.example.com``.

Skip URLs containing a substring
------------------------------------

Use ``-suc``/``--skip-urls-containing`` to skip based on the full URL
instead of just the hostname - useful for excluding specific paths on a
domain you otherwise want checked:

.. code-block:: bash

    markdown-checker . -f check_broken_urls --skip-urls-containing=/embed/,/preview/

List syntax
-----------

Every list option (``--skip-domains``, ``--skip-urls-containing``,
``--extensions``, ``--skip-files``, ``--tracking-domains``) takes a single
comma-separated value:

- Correct: ``--skip-domains=example.com,test.com``
- Correct (quoting is optional): ``--skip-domains="example.com,test.com"``
- Wrong: ``--skip-domains=[example.com,test.com]`` (no square brackets)
- Wrong: ``--skip-domains=example.com, test.com`` (no spaces after commas)
- Wrong: ``--skip-domains example.com test.com`` (use ``=`` and commas, not
  repeated flags)

Verify it worked
------------------

Re-run the check and confirm the skipped domain/URL no longer appears in
the output or in ``comment.md``. If it's still reported, double check for
stray spaces or brackets in the value.
