from markdown_checker.patterns import FENCE_OPEN_PATTERN
from markdown_checker.patterns import LINK_PATTERN
from markdown_checker.patterns import LOCALE_PATTERN
from markdown_checker.patterns import SCHEME_PATTERN
from markdown_checker.patterns import TRACKING_PATTERN
from markdown_checker.patterns import TRACKING_QUERY_PATTERN


def test_link_pattern_matches_plain_destination():
    """LINK_PATTERN captures a plain markdown link destination."""
    match = LINK_PATTERN.search("[text](https://example.com/page)")
    assert match is not None
    assert match.group("plain") == "https://example.com/page"


def test_link_pattern_matches_angle_destination():
    """LINK_PATTERN captures an <...> destination, allowing spaces."""
    match = LINK_PATTERN.search("[text](<./path with spaces.md>)")
    assert match is not None
    assert match.group("angle") == "./path with spaces.md"


def test_link_pattern_ignores_title():
    """LINK_PATTERN captures the destination without a trailing title."""
    match = LINK_PATTERN.search('[text](https://example.com "A title")')
    assert match is not None
    assert match.group("plain") == "https://example.com"


def test_link_pattern_allows_one_level_of_balanced_parens():
    """LINK_PATTERN allows a single level of balanced parentheses in the destination."""
    match = LINK_PATTERN.search("[text](https://en.wikipedia.org/wiki/Example_(disambiguation))")
    assert match is not None
    assert match.group("plain") == "https://en.wikipedia.org/wiki/Example_(disambiguation)"


def test_scheme_pattern_matches_known_schemes():
    """SCHEME_PATTERN matches destinations with a URI scheme."""
    assert SCHEME_PATTERN.match("mailto:test@example.com")
    assert SCHEME_PATTERN.match("tel:+1234567890")
    assert SCHEME_PATTERN.match("ftp://example.com")


def test_scheme_pattern_does_not_match_relative_paths():
    """SCHEME_PATTERN does not match plain relative paths or http(s) URLs' host part."""
    assert SCHEME_PATTERN.match("./docs/guide.md") is None
    assert SCHEME_PATTERN.match("../guide.md") is None


def test_fence_open_pattern_matches_backtick_and_tilde_fences():
    """FENCE_OPEN_PATTERN matches opening code fences with up to 3 spaces of indentation."""
    assert FENCE_OPEN_PATTERN.match("```python")
    assert FENCE_OPEN_PATTERN.match("~~~")
    assert FENCE_OPEN_PATTERN.match("   ```")


def test_fence_open_pattern_rejects_over_indented_fence():
    """FENCE_OPEN_PATTERN does not match fences indented by more than 3 spaces."""
    assert FENCE_OPEN_PATTERN.match("    ```") is None


def test_locale_pattern_matches_locale_segment():
    """LOCALE_PATTERN matches locale path segments case-insensitively."""
    assert LOCALE_PATTERN.search("/en-us/docs")
    assert LOCALE_PATTERN.search("/EN-US/docs")


def test_locale_pattern_no_match_without_locale():
    """LOCALE_PATTERN does not match paths without a locale segment."""
    assert LOCALE_PATTERN.search("/docs/guide") is None


def test_tracking_pattern_matches_wt_mc_id():
    """TRACKING_PATTERN matches wt.mc_id query parameters case-insensitively."""
    assert TRACKING_PATTERN.search("?WT.mc_id=abc123")
    assert TRACKING_PATTERN.search("&wt.mc_id=abc123")


def test_tracking_pattern_no_match_without_tracking_param():
    """TRACKING_PATTERN does not match URLs without a tracking query param."""
    assert TRACKING_PATTERN.search("?ref=other") is None


def test_tracking_query_pattern_consumes_rest_of_query_string():
    """TRACKING_QUERY_PATTERN matches the tracking param and everything after it."""
    match = TRACKING_QUERY_PATTERN.search("https://example.com/page?WT.mc_id=abc&other=1")
    assert match is not None
    assert match.group(0) == "?WT.mc_id=abc&other=1"
