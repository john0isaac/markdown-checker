import pytest

from markdown_checker.checks.locale import _BUILTIN_SKIP_DOMAINS, PathsLocaleCheck, URLsLocaleCheck

# --- URLsLocaleCheck ---


@pytest.fixture
def urls_check():
    return URLsLocaleCheck()


def test_urls_locale_check_name():
    """Check name matches registry key."""
    assert URLsLocaleCheck.name == "check_urls_locale"


def test_urls_with_locale_reported(urls_check, make_markdown_url, make_markdown_links):
    """URLs with locale segments are reported."""
    url = make_markdown_url("https://learn.microsoft.com/en-us/azure")
    links = make_markdown_links(urls=[url])
    result = urls_check.run(links)
    assert len(result) == 1
    assert result[0].issue == "has locale"


def test_urls_without_locale_not_reported(urls_check, make_markdown_url, make_markdown_links):
    """URLs without locale segments are not reported."""
    url = make_markdown_url("https://learn.microsoft.com/azure")
    links = make_markdown_links(urls=[url])
    result = urls_check.run(links)
    assert result == []


def test_urls_locale_skip_domains(urls_check, make_markdown_url, make_markdown_links):
    """URLs on skip domains are not checked for locale."""
    url = make_markdown_url("https://www.nvidia.com/en-us/page")
    links = make_markdown_links(urls=[url])
    result = urls_check.run(links)
    assert result == []


def test_urls_locale_custom_skip_domains(urls_check, make_markdown_url, make_markdown_links):
    """Custom skip domains are respected."""
    url = make_markdown_url("https://custom.com/en-us/page")
    links = make_markdown_links(urls=[url])
    result = urls_check.run(links, skip_domains=["custom.com"])
    assert result == []


def test_urls_locale_skip_urls_containing(urls_check, make_markdown_url, make_markdown_links):
    """URLs matching skip_urls_containing are not checked."""
    url = make_markdown_url("https://example.com/en-us/video-embed.html")
    links = make_markdown_links(urls=[url])
    result = urls_check.run(links, skip_urls_containing=["https://example.com/en-us/video-embed.html"])
    assert result == []


def test_urls_locale_no_urls(urls_check, make_markdown_links):
    """Returns empty list when there are no URLs."""
    links = make_markdown_links()
    result = urls_check.run(links)
    assert result == []


@pytest.mark.parametrize(
    "link, expected_count",
    [
        ("https://example.com/fr-fr/docs", 1),
        ("https://example.com/pt-br/docs", 1),
        ("https://example.com/docs", 0),
    ],
)
def test_urls_locale_various_locales(urls_check, make_markdown_url, make_markdown_links, link, expected_count):
    """Detects various locale patterns in URLs."""
    url = make_markdown_url(link)
    links = make_markdown_links(urls=[url])
    result = urls_check.run(links)
    assert len(result) == expected_count


# --- PathsLocaleCheck ---


@pytest.fixture
def paths_check():
    return PathsLocaleCheck()


def test_paths_locale_check_name():
    """Check name matches registry key."""
    assert PathsLocaleCheck.name == "check_paths_locale"


def test_paths_with_locale_reported(paths_check, make_markdown_path, make_markdown_links):
    """Paths with locale segments are reported."""
    path = make_markdown_path("./en-us/docs/guide.md")
    links = make_markdown_links(paths=[path])
    result = paths_check.run(links)
    assert len(result) == 1
    assert result[0].issue == "has locale"


def test_paths_without_locale_not_reported(paths_check, make_markdown_path, make_markdown_links):
    """Paths without locale segments are not reported."""
    path = make_markdown_path("./docs/guide.md")
    links = make_markdown_links(paths=[path])
    result = paths_check.run(links)
    assert result == []


def test_paths_locale_no_paths(paths_check, make_markdown_links):
    """Returns empty list when there are no paths."""
    links = make_markdown_links()
    result = paths_check.run(links)
    assert result == []


def test_builtin_skip_domains_contains_nvidia():
    """Builtin skip domains includes nvidia."""
    assert "www.nvidia.com" in _BUILTIN_SKIP_DOMAINS
