from pathlib import Path

import pytest

from markdown_checker.models.path import MarkdownPath
from markdown_checker.models.url import MarkdownURL
from markdown_checker.utils.extract_links import MarkdownLinks

RESOURCES_DIR = Path(__file__).parent / "resources"


@pytest.fixture
def resources_dir() -> Path:
    return RESOURCES_DIR


@pytest.fixture
def sample1_path(resources_dir: Path) -> Path:
    return resources_dir / "sample1.md"


@pytest.fixture
def sample2_path(resources_dir: Path) -> Path:
    return resources_dir / "sample2.md"


@pytest.fixture
def sample3_path(resources_dir: Path) -> Path:
    return resources_dir / "sample3.md"


@pytest.fixture
def sample4_path(resources_dir: Path) -> Path:
    return resources_dir / "sample4.md"


@pytest.fixture
def dummy_file_path(tmp_path: Path) -> Path:
    return tmp_path / "dummy.md"


@pytest.fixture
def make_markdown_url():
    def _factory(link: str, line_number: int = 1, file_path: Path = Path("test.md"), issue: str = "") -> MarkdownURL:
        return MarkdownURL(link=link, line_number=line_number, file_path=file_path, issue=issue)

    return _factory


@pytest.fixture
def make_markdown_path():
    def _factory(link: str, line_number: int = 1, file_path: Path = Path("test.md"), issue: str = "") -> MarkdownPath:
        return MarkdownPath(link=link, line_number=line_number, file_path=file_path, issue=issue)

    return _factory


@pytest.fixture
def make_markdown_links():
    def _factory(
        urls: list[MarkdownURL] | None = None,
        paths: list[MarkdownPath] | None = None,
    ) -> MarkdownLinks:
        return MarkdownLinks(urls=urls or [], paths=paths or [])

    return _factory


@pytest.fixture
def url_with_tracking(make_markdown_url):
    return make_markdown_url("https://learn.microsoft.com/en-us/azure?WT.mc_id=test123")


@pytest.fixture
def url_without_tracking(make_markdown_url):
    return make_markdown_url("https://learn.microsoft.com/en-us/azure")


@pytest.fixture
def url_with_locale(make_markdown_url):
    return make_markdown_url("https://learn.microsoft.com/en-us/azure")


@pytest.fixture
def url_without_locale(make_markdown_url):
    return make_markdown_url("https://learn.microsoft.com/azure")


@pytest.fixture
def path_with_tracking(make_markdown_path):
    return make_markdown_path("./docs/guide.md?WT.mc_id=test123")


@pytest.fixture
def path_without_tracking(make_markdown_path):
    return make_markdown_path("./docs/guide.md")


@pytest.fixture
def path_with_locale(make_markdown_path):
    return make_markdown_path("./en-us/docs/guide.md")


@pytest.fixture
def path_without_locale(make_markdown_path):
    return make_markdown_path("./docs/guide.md")
