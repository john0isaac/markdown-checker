import pytest

from markdown_checker.checks.tracking import PathsTrackingCheck, URLsTrackingCheck
from markdown_checker.models.config import Config

# --- URLsTrackingCheck ---


@pytest.fixture
def urls_check():
    return URLsTrackingCheck()


def test_urls_tracking_check_name():
    """Check name matches registry key."""
    assert URLsTrackingCheck.name == "check_urls_tracking"


def test_url_on_tracking_domain_without_id_reported(urls_check, make_markdown_url, make_markdown_links):
    """URLs on tracking domains without tracking ID are reported."""
    url = make_markdown_url("https://learn.microsoft.com/azure")
    links = make_markdown_links(urls=[url])
    result = urls_check.run(links, config=Config(tracking_domains=["learn.microsoft.com"]))
    assert len(result) == 1
    assert result[0].issue == "is missing tracking id"


def test_url_on_tracking_domain_with_id_not_reported(urls_check, make_markdown_url, make_markdown_links):
    """URLs on tracking domains with tracking ID are not reported."""
    url = make_markdown_url("https://learn.microsoft.com/azure?WT.mc_id=test")
    links = make_markdown_links(urls=[url])
    result = urls_check.run(links, config=Config(tracking_domains=["learn.microsoft.com"]))
    assert result == []


def test_url_not_on_tracking_domain_not_reported(urls_check, make_markdown_url, make_markdown_links):
    """URLs not on tracking domains are not reported."""
    url = make_markdown_url("https://example.com/page")
    links = make_markdown_links(urls=[url])
    result = urls_check.run(links, config=Config(tracking_domains=["learn.microsoft.com"]))
    assert result == []


def test_urls_tracking_skip_domains(urls_check, make_markdown_url, make_markdown_links):
    """URLs on skip domains are not checked for tracking."""
    url = make_markdown_url("https://learn.microsoft.com/azure")
    links = make_markdown_links(urls=[url])
    result = urls_check.run(
        links, config=Config(skip_domains=["learn.microsoft.com"], tracking_domains=["learn.microsoft.com"])
    )
    assert result == []


def test_urls_tracking_skip_urls_containing(urls_check, make_markdown_url, make_markdown_links):
    """URLs matching skip_urls_containing are not checked."""
    url = make_markdown_url("https://learn.microsoft.com/azure")
    links = make_markdown_links(urls=[url])
    result = urls_check.run(
        links,
        config=Config(
            skip_urls_containing=["https://learn.microsoft.com/azure"],
            tracking_domains=["microsoft.com"],
        ),
    )
    assert result == []


def test_urls_tracking_no_urls(urls_check, make_markdown_links):
    """Returns empty list when there are no URLs."""
    links = make_markdown_links()
    result = urls_check.run(links, config=Config(tracking_domains=["microsoft.com"]))
    assert result == []


def test_urls_tracking_no_tracking_domains(urls_check, make_markdown_url, make_markdown_links):
    """No issues when tracking_domains is empty."""
    url = make_markdown_url("https://learn.microsoft.com/azure")
    links = make_markdown_links(urls=[url])
    result = urls_check.run(links, config=Config(tracking_domains=[]))
    assert result == []


@pytest.mark.parametrize(
    "link, has_tracking",
    [
        ("https://learn.microsoft.com/azure?WT.mc_id=abc", True),
        ("https://learn.microsoft.com/azure?wt.mc_id=abc", True),
        ("https://learn.microsoft.com/azure&WT.mc_id=abc", True),
        ("https://learn.microsoft.com/azure", False),
    ],
)
def test_urls_tracking_id_detection(urls_check, make_markdown_url, make_markdown_links, link, has_tracking):
    """Detects both WT.mc_id and wt.mc_id tracking patterns."""
    url = make_markdown_url(link)
    links = make_markdown_links(urls=[url])
    result = urls_check.run(links, config=Config(tracking_domains=["learn.microsoft.com"]))
    assert (len(result) == 0) == has_tracking


# --- PathsTrackingCheck ---


@pytest.fixture
def paths_check():
    return PathsTrackingCheck()


def test_paths_tracking_check_name():
    """Check name matches registry key."""
    assert PathsTrackingCheck.name == "check_paths_tracking"


def test_path_without_tracking_reported(paths_check, make_markdown_path, make_markdown_links):
    """Paths without tracking ID are reported."""
    path = make_markdown_path("./docs/guide.md")
    links = make_markdown_links(paths=[path])
    result = paths_check.run(links)
    assert len(result) == 1
    assert result[0].issue == "is missing tracking id"


def test_path_with_tracking_not_reported(paths_check, make_markdown_path, make_markdown_links):
    """Paths with tracking ID are not reported."""
    path = make_markdown_path("./docs/guide.md?WT.mc_id=test")
    links = make_markdown_links(paths=[path])
    result = paths_check.run(links)
    assert result == []


def test_paths_tracking_no_paths(paths_check, make_markdown_links):
    """Returns empty list when there are no paths."""
    links = make_markdown_links()
    result = paths_check.run(links)
    assert result == []


def test_paths_tracking_multiple(paths_check, make_markdown_path, make_markdown_links):
    """Reports all paths missing tracking."""
    paths = [
        make_markdown_path("./a.md"),
        make_markdown_path("./b.md?WT.mc_id=ok"),
        make_markdown_path("./c.md"),
    ]
    links = make_markdown_links(paths=paths)
    result = paths_check.run(links)
    assert len(result) == 2
