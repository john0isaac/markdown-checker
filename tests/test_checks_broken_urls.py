from pathlib import Path
from unittest.mock import patch

import pytest

from markdown_checker.checks.broken_urls import _BUILTIN_SKIP_DOMAINS, BrokenURLsCheck, _check_url
from markdown_checker.models.config import Config
from markdown_checker.models.url import MarkdownURL


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
    with patch.object(MarkdownURL, "is_alive", return_value=True):
        result = check.run(links, config=Config(skip_domains=list(_BUILTIN_SKIP_DOMAINS)))
    # example.com not in builtin skip, so it gets checked
    # Since we mock is_alive to True, nothing should be returned
    assert result == []


def test_dead_url_reported(check, make_markdown_url, make_markdown_links):
    """Dead URLs are reported with 'is broken' issue."""
    url = make_markdown_url("https://totally-fake-domain-12345.com/page")
    links = make_markdown_links(urls=[url])
    with patch.object(MarkdownURL, "is_alive", return_value=False):
        result = check.run(links)
    assert len(result) == 1
    assert result[0].issue == "is broken"


def test_builtin_skip_domains_skipped(check, make_markdown_url, make_markdown_links):
    """URLs from builtin skip domains are not checked."""
    url = make_markdown_url("https://openai.com/pricing")
    links = make_markdown_links(urls=[url])
    with patch.object(MarkdownURL, "is_alive") as mock_alive:
        result = check.run(links)
    mock_alive.assert_not_called()
    assert result == []


def test_custom_skip_domains(check, make_markdown_url, make_markdown_links):
    """Custom skip domains are respected."""
    url = make_markdown_url("https://custom-skip.com/page")
    links = make_markdown_links(urls=[url])
    with patch.object(MarkdownURL, "is_alive") as mock_alive:
        result = check.run(links, config=Config(skip_domains=["custom-skip.com"]))
    mock_alive.assert_not_called()
    assert result == []


def test_skip_urls_containing(check, make_markdown_url, make_markdown_links):
    """URLs containing skip substrings are not checked."""
    url = make_markdown_url("https://example.com/video-embed.html")
    links = make_markdown_links(urls=[url])
    with patch.object(MarkdownURL, "is_alive") as mock_alive:
        check.run(links, config=Config(skip_urls_containing=["https://example.com/video-embed.html"]))
    mock_alive.assert_not_called()


# --- Tests for _check_url helper ---


def test_check_url_returns_none_for_skipped_domain():
    """Returns None for URLs on skipped domains."""
    url = MarkdownURL(link="https://github.com/page", line_number=1, file_path=Path("test.md"))
    result = _check_url(url, skip_domains=["github.com"], skip_urls_containing=[], timeout=5, retries=1)
    assert result is None


def test_check_url_returns_url_for_broken():
    """Returns the URL with issue set when it is not alive."""
    url = MarkdownURL(link="https://broken.example.com", line_number=1, file_path=Path("test.md"))
    with patch.object(MarkdownURL, "is_alive", return_value=False):
        result = _check_url(url, skip_domains=[], skip_urls_containing=[], timeout=5, retries=1)
    assert result is not None
    assert result.issue == "is broken"


def test_check_url_returns_none_for_alive():
    """Returns None for alive URLs."""
    url = MarkdownURL(link="https://alive.example.com", line_number=1, file_path=Path("test.md"))
    with patch.object(MarkdownURL, "is_alive", return_value=True):
        result = _check_url(url, skip_domains=[], skip_urls_containing=[], timeout=5, retries=1)
    assert result is None


def test_builtin_skip_domains_list():
    """Builtin skip domains list contains known bot-blocking domains."""
    assert isinstance(_BUILTIN_SKIP_DOMAINS, list)
    assert len(_BUILTIN_SKIP_DOMAINS) > 0
    assert "openai.com" in _BUILTIN_SKIP_DOMAINS
