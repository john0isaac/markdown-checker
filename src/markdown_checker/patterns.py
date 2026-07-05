"""Central registry of all compiled regular expressions used across the package."""

import re

LINK_PATTERN = re.compile(
    r"\]\(\s*"
    r"(?:<(?P<angle>[^<>\n]*)>|(?P<plain>(?:[^()\s]|\([^()]*\))+))"
    r"(?:\s+[\"'][^\"']*[\"'])?"
    r"\s*\)"
)
"""Matches the ``(...)`` destination of an inline Markdown link.

Plain destinations may contain one level of balanced parentheses (e.g.
Wikipedia URLs), while ``<...>`` destinations may contain spaces. An
optional ``"title"`` or ``'title'`` is matched but not captured.
"""

SCHEME_PATTERN = re.compile(r"\A[A-Za-z][A-Za-z0-9+.-]*:")
"""Matches a URI scheme prefix (e.g. ``mailto:``, ``tel:``, ``ftp:``).

Destinations with a scheme are neither checkable URLs nor local paths.
"""

FENCE_OPEN_PATTERN = re.compile(r"^ {0,3}(`{3,}|~{3,})")
"""Matches an opening or closing code fence (three or more backticks or
tildes), allowing at most 3 spaces of indentation per CommonMark.
"""

LOCALE_PATTERN = re.compile(r"/[a-z]{2}-[a-z]{2}/", re.IGNORECASE)
"""Matches a locale segment in a URL path, e.g. ``/en-us/``."""

TRACKING_PATTERN = re.compile(r"[?&]wt\.mc_id=", re.IGNORECASE)
"""Matches the ``wt.mc_id`` tracking query parameter in a URL."""

TRACKING_QUERY_PATTERN = re.compile(TRACKING_PATTERN.pattern + ".*", TRACKING_PATTERN.flags)
"""Like :data:`TRACKING_PATTERN`, but also consumes the rest of the query string."""
