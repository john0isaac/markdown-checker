from pathlib import Path
from unittest.mock import patch

import pytest

from markdown_checker.checks.broken_urls import _BUILTIN_SKIP_DOMAINS
from markdown_checker.checks.broken_urls import _check_url
from markdown_checker.checks.broken_urls import BrokenURLsCheck
from markdown_checker.models.config import Config
from markdown_checker.models.url import MarkdownURL
from markdown_checker.models.url import URLCheckResult


@pytest.fixture
def check():
    return BrokenURLsCheck()


def test_name():
    """Check name matches registry key."""
    assert BrokenURLsCheck.name == "check_broken_urls"


def test_no_urls_returns_empty(check, make_markdown_links):
    """Returns empty list when there are no URLs to check."""
    links = make_markdown_links()
    result = check.run(links)
    assert result == []


def test_alive_url_not_reported(check, make_markdown_url, make_markdown_links):
    """Alive URLs are not reported."""
    url = make_markdown_url("https://example.com")
    links = make_markdown_links(urls=[url])
    alive_result = URLCheckResult(status="alive", http_status_code=200)
    with patch.object(MarkdownURL, "check", return_value=alive_result):
        result = check.run(links, config=Config(skip_domains=list(_BUILTIN_SKIP_DOMAINS)))
    # example.com not in builtin skip, so it gets checked
    # Since we mock check to return alive, nothing should be returned
    assert result == []


def test_dead_url_reported(check, make_markdown_url, make_markdown_links):
    """Dead URLs are reported with 'is broken' issue."""
    url = make_markdown_url("https://totally-fake-domain-12345.com/page")
    links = make_markdown_links(urls=[url])
    broken_result = URLCheckResult(status="broken", http_status_code=404)
    with patch.object(MarkdownURL, "check", return_value=broken_result):
        result = check.run(links)
    assert len(result) == 1
    assert result[0].issue == "is broken"


def test_custom_skip_domains(check, make_markdown_url, make_markdown_links):
    """Custom skip domains are respected."""
    url = make_markdown_url("https://custom-skip.com/page")
    links = make_markdown_links(urls=[url])
    with patch.object(MarkdownURL, "check") as mock_check:
        result = check.run(links, config=Config(skip_domains=["custom-skip.com"]))
    mock_check.assert_not_called()
    assert result == []


def test_skip_urls_containing(check, make_markdown_url, make_markdown_links):
    """URLs containing skip substrings are not checked."""
    url = make_markdown_url("https://example.com/video-embed.html")
    links = make_markdown_links(urls=[url])
    with patch.object(MarkdownURL, "check") as mock_check:
        check.run(links, config=Config(skip_urls_containing=["https://example.com/video-embed.html"]))
    mock_check.assert_not_called()


# --- Tests for _check_url helper ---


def test_check_url_returns_none_for_skipped_domain():
    """Returns None for URLs on skipped domains."""
    url = MarkdownURL(link="https://github.com/page", line_number=1, file_path=Path("test.md"))
    result = _check_url(
        url,
        skip_domains=["github.com"],
        skip_urls_containing=[],
        timeout=5,
        retries=1,
        retry_on_429=True,
        fallback_retry_delay=60,
    )
    assert result is None


def test_check_url_returns_url_for_broken():
    """Returns the URL with issue set when it is not alive."""
    url = MarkdownURL(link="https://broken.example.com", line_number=1, file_path=Path("test.md"))
    broken_result = URLCheckResult(status="broken", http_status_code=404)
    with patch.object(MarkdownURL, "check", return_value=broken_result):
        result = _check_url(
            url,
            skip_domains=[],
            skip_urls_containing=[],
            timeout=5,
            retries=1,
            retry_on_429=True,
            fallback_retry_delay=60,
        )
    assert result is not None
    assert result.issue == "is broken"
    assert result.issue_level == "error"


def test_check_url_returns_none_for_alive():
    """Returns None for alive URLs."""
    url = MarkdownURL(link="https://alive.example.com", line_number=1, file_path=Path("test.md"))
    alive_result = URLCheckResult(status="alive", http_status_code=200)
    with patch.object(MarkdownURL, "check", return_value=alive_result):
        result = _check_url(
            url,
            skip_domains=[],
            skip_urls_containing=[],
            timeout=5,
            retries=1,
            retry_on_429=True,
            fallback_retry_delay=60,
        )
    assert result is None


# --- Rate-limiting tests ---


def test_check_url_rate_limited_returns_warning_issue():
    """rate_limited status: URL is returned with issue_level='warning' and issue set."""
    url = MarkdownURL(link="https://rate-limited.example.com", line_number=1, file_path=Path("test.md"))
    rate_limited_result = URLCheckResult(status="rate_limited", http_status_code=429, retry_after=30)
    with patch.object(MarkdownURL, "check", return_value=rate_limited_result):
        result = _check_url(
            url,
            skip_domains=[],
            skip_urls_containing=[],
            timeout=5,
            retries=1,
            retry_on_429=True,
            fallback_retry_delay=30,
        )
    assert result is not None
    assert result.issue == "was skipped due to rate limiting"
    assert result.issue_level == "warning"


def test_check_url_transient_error_returns_warning_issue():
    """transient_error status: URL is returned with issue_level='warning' and issue set."""
    url = MarkdownURL(link="https://flaky.example.com", line_number=1, file_path=Path("test.md"))
    transient_result = URLCheckResult(status="transient_error", http_status_code=None)
    with patch.object(MarkdownURL, "check", return_value=transient_result):
        result = _check_url(
            url,
            skip_domains=[],
            skip_urls_containing=[],
            timeout=5,
            retries=1,
            retry_on_429=True,
            fallback_retry_delay=30,
        )
    assert result is not None
    assert result.issue == "could not be reached due to a network error"
    assert result.issue_level == "warning"


def test_rate_limited_urls_reported_as_warnings(check, make_markdown_url, make_markdown_links):
    """URLs that return rate_limited are in the results list with issue_level='warning'."""
    url = make_markdown_url("https://rate-limited.example.com")
    links = make_markdown_links(urls=[url])
    rate_limited_result = URLCheckResult(status="rate_limited", http_status_code=429, retry_after=60)
    with patch.object(MarkdownURL, "check", return_value=rate_limited_result):
        result = check.run(links)
    assert len(result) == 1
    assert result[0].issue_level == "warning"
    assert result[0].issue == "was skipped due to rate limiting"


def test_rate_limited_count_across_urls(check, make_markdown_url, make_markdown_links):
    """All rate-limited URLs are included in the results as warnings."""
    urls = [make_markdown_url(f"https://example.com/{i}") for i in range(3)]
    links = make_markdown_links(urls=urls)
    rate_limited_result = URLCheckResult(status="rate_limited", http_status_code=429)
    with patch.object(MarkdownURL, "check", return_value=rate_limited_result):
        result = check.run(links)
    assert len(result) == 3
    assert all(r.issue_level == "warning" for r in result)


def test_mixed_outcomes_broken_error_rate_limited_warning(check, make_markdown_url, make_markdown_links):
    """Broken URLs have issue_level='error'; rate-limited have 'warning'; alive are excluded."""
    url_broken = make_markdown_url("https://broken.example.com")
    url_rate_limited = make_markdown_url("https://rate-limited.example.com")
    url_alive = make_markdown_url("https://alive.example.com")
    links = make_markdown_links(urls=[url_broken, url_rate_limited, url_alive])

    def fake_check(self, **kwargs):
        if "broken" in self.link:
            return URLCheckResult(status="broken", http_status_code=404)
        if "rate-limited" in self.link:
            return URLCheckResult(status="rate_limited", http_status_code=429)
        return URLCheckResult(status="alive", http_status_code=200)

    with patch.object(MarkdownURL, "check", fake_check):
        result = check.run(links)

    assert len(result) == 2
    broken = next(r for r in result if "broken" in r.link)
    rate_limited = next(r for r in result if "rate-limited" in r.link)
    assert broken.issue_level == "error"
    assert rate_limited.issue_level == "warning"
