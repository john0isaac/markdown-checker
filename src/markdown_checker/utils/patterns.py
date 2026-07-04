"""Central registry of all compiled regular expressions used across the package."""

import re

# --- extract_links.py -------------------------------------------------------

# Matches the (...) destination of an inline markdown link. Plain destinations
# may contain one level of balanced parentheses (e.g. wikipedia URLs); <...>
# destinations may contain spaces; an optional "title" or 'title' is consumed
# but not captured.
LINK_PATTERN = re.compile(
    r"\]\(\s*"
    r"(?:<(?P<angle>[^<>\n]*)>|(?P<plain>(?:[^()\s]|\([^()]*\))+))"
    r"(?:\s+[\"'][^\"']*[\"'])?"
    r"\s*\)"
)
# Destinations with a URI scheme (mailto:, tel:, ftp:, ...) are neither
# checkable URLs nor local paths.
SCHEME_PATTERN = re.compile(r"\A[A-Za-z][A-Za-z0-9+.-]*:")
# Opening/closing code fence: at most 3 spaces of indentation per CommonMark.
FENCE_OPEN_PATTERN = re.compile(r"^ {0,3}(`{3,}|~{3,})")

# --- models/base.py ----------------------------------------------------------

LOCALE_PATTERN = re.compile(r"/[a-z]{2}-[a-z]{2}/", re.IGNORECASE)
TRACKING_PATTERN = re.compile(r"[?&]wt\.mc_id=", re.IGNORECASE)

# --- models/path.py ------------------------------------------------------------

# Same as TRACKING_PATTERN but also consumes the rest of the query string.
TRACKING_QUERY_PATTERN = re.compile(TRACKING_PATTERN.pattern + ".*", TRACKING_PATTERN.flags)
