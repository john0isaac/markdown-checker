How Link Detection Works
===========================

Every check starts from the same extraction step: reading a markdown file
line by line and pulling out link destinations. This page explains what
counts as a checkable link and what's deliberately excluded.

What's matched
-----------------

Only the destination of an inline Markdown link is considered - the part
inside parentheses in ``[text](destination)``, or inside angle brackets in
``[text](<destination>)``. Reference-style links (``[text][ref]`` with a
separate ``[ref]: destination`` definition) are not currently matched.

Code fences are skipped entirely: lines between an opening and matching
closing fence (three or more backtick or tilde characters) are ignored, so
example links inside a code sample are never checked.

How a destination is classified
------------------------------------

Each matched destination falls into one of three buckets:

- **URL**: starts with ``http://`` or ``https://`` (protocol-relative
  ``//host/...`` links are treated as ``https://``). Handled by
  ``check_broken_urls``, ``check_urls_locale``, and ``check_urls_tracking``.
- **Ignored**: starts with another URI scheme (e.g. ``mailto:``, ``tel:``),
  or is a bare same-page anchor (``#section``). These can't be meaningfully
  checked as either a URL or a local file, so no check ever sees them.
- **Path**: anything else - this includes root-relative paths
  (``/docs/usage.md``), explicitly relative paths (``./img.png``,
  ``../docs/usage.md``), and bare relative paths with no prefix
  (``docs/usage.md``). All of these are treated identically and handled by
  ``check_broken_paths`` and ``check_paths_tracking``.

Fragments on paths
----------------------

A path may carry a trailing ``?query`` and/or ``#anchor`` - for example
``docs/usage.md#configuration``. Both checks that operate on paths strip
this fragment before resolving the file, so only the ``docs/usage.md``
part needs to exist on disk; the anchor itself is never validated against
the target file's headings.

Resolving a path to a file
--------------------------------

``check_broken_paths`` tries to resolve a path relative to the markdown
file it was found in first (e.g. ``../img.png`` in ``docs/usage.md``
resolves against ``docs/``), then falls back to resolving it as an
absolute or current-working-directory-relative path. A path is reported as
broken only if neither resolution finds an existing file.
