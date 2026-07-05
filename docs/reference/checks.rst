The Five Checks
================

markdown-checker registers five checks, selected with ``-f``/``--func``.
Each check consumes either the paths or the URLs extracted from a file (see
:doc:`../explanation/link-detection`), never both.

.. contents:: On this page
    :local:

``check_broken_paths``
------------------------

Flags
    Relative or root-relative links whose target file does not exist on
    disk, e.g. ``[guide](./missing.md)`` when ``missing.md`` isn't there.
Ignores
    Web URLs, ``mailto:``-style links, and bare ``#fragment`` links. Query
    strings/anchors on a path (``docs/usage.md#section``) are stripped
    before checking existence.
Options that affect it
    ``SRC``/``--dir``, ``--extensions``, ``--skip-files`` (which files are
    scanned in the first place). Domain/URL skip options do not apply -
    this check never makes network requests.
Sample finding
    .. code-block:: text

        File 'docs/index.md', line 5
        ./missing.md is broken.

``check_broken_urls``
------------------------

Flags
    Web URLs that don't return a ``2xx`` HTTP response after retries.
Ignores
    Hosts in ``--skip-domains`` or the built-in list of hosts known to
    block automated requests; URLs matching ``--skip-urls-containing``.
Options that affect it
    ``--skip-domains``, ``--skip-urls-containing``, ``--timeout``,
    ``--retries``, ``--retry-on-429``, ``--fallback-retry-delay``,
    ``--max-workers``, ``--per-host-delay``.
Severity
    Reports a mix of error-level (``broken``) and warning-level
    (``rate_limited``, ``unverifiable``, ``transient_error``) issues - see
    :doc:`exit-codes` for the full status table.
Sample finding
    .. code-block:: text

        File 'docs/index.md', line 8
        https://example.com/gone is broken.

``check_urls_locale``
------------------------

Flags
    URLs whose path contains a locale segment, e.g. ``/en-us/`` in
    ``https://example.com/en-us/docs``. A "locale segment" is a
    language-country pair matching ``xx-xx`` (case-insensitive).
Ignores
    ``www.nvidia.com`` (built in - its docs always include a locale
    segment), plus any host in ``--skip-domains`` or URL in
    ``--skip-urls-containing``.
Options that affect it
    ``--skip-domains``, ``--skip-urls-containing``.
Sample finding
    .. code-block:: text

        File 'docs/index.md', line 8
        https://example.com/en-us/docs has locale.

``check_urls_tracking``
--------------------------

Flags
    URLs on a configured tracking domain that are missing a ``wt.mc_id``
    query parameter.
Ignores
    URLs on hosts *not* listed in ``--tracking-domains`` (the check does
    nothing for them), plus any host in ``--skip-domains`` or URL in
    ``--skip-urls-containing``.
Default tracking domains
    ``github.com``, ``microsoft.com``, ``visualstudio.com``, ``aka.ms``,
    ``azure.com``.
Options that affect it
    ``--tracking-domains``, ``--skip-domains``, ``--skip-urls-containing``.
Sample finding
    .. code-block:: text

        File 'docs/index.md', line 8
        https://learn.microsoft.com/azure/ is missing tracking id.

``check_paths_tracking``
---------------------------

Flags
    Every relative path link missing a ``wt.mc_id`` query parameter. Unlike
    ``check_urls_tracking``, there is no domain filter - all paths are checked.
Options that affect it
    ``SRC``/``--dir``, ``--extensions``, ``--skip-files`` only.
Sample finding
    .. code-block:: text

        File 'docs/index.md', line 5
        ./usage.md is missing tracking id.
