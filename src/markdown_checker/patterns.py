"""Central registry of all compiled regular expressions used across the package."""

import functools
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

LOCALE_PATTERN = re.compile(r"/(?P<language>[a-z]{2})-(?P<region>[a-z]{2})(?=/|$)", re.IGNORECASE)
"""Matches a candidate locale segment in a URL path, e.g. ``/en-us/`` or a
trailing ``/en-us``. Candidates are validated against known locales by
:meth:`~markdown_checker.models.base.MarkdownLinkBase.has_locale`, so
look-alikes such as ``/ci-cd/`` aren't reported.
"""

DEFAULT_TRACKING_PARAMS: tuple[str, ...] = ("wt.mc_id",)
"""Tracking query parameters required by default (see ``--tracking-param``)."""


@functools.lru_cache
def tracking_pattern(params: tuple[str, ...]) -> re.Pattern[str]:
    """Build a case-insensitive pattern matching any of ``params`` as a query
    parameter, e.g. ``?wt.mc_id=`` or ``&utm_source=``.
    """
    names = "|".join(re.escape(param) for param in params)
    return re.compile(rf"[?&](?:{names})=", re.IGNORECASE)


TRACKING_PATTERN = tracking_pattern(DEFAULT_TRACKING_PARAMS)
"""Matches the default ``wt.mc_id`` tracking query parameter in a URL."""

TRACKING_QUERY_PATTERN = re.compile(TRACKING_PATTERN.pattern + ".*", TRACKING_PATTERN.flags)
"""Like :data:`TRACKING_PATTERN`, but also consumes the rest of the query string."""

QUERY_OR_ANCHOR_PATTERN = re.compile(r"[?#].*", re.DOTALL)
"""Matches a link's ``?query`` and/or ``#anchor``, from the first ``?`` or ``#`` to the end."""
