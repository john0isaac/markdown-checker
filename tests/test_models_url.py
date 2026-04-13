from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest

from markdown_checker.models.url import MarkdownURL


@pytest.mark.parametrize(
    "link, expected_host",
    [
        ("https://learn.microsoft.com/azure", "learn.microsoft.com"),
        ("https://github.com/user/repo", "github.com"),
        ("http://localhost:8000/path", "localhost:8000"),
        ("https://www.example.com/page?q=1", "www.example.com"),
    ],
)
def test_host_name(link: str, expected_host: str):
    """Extracts the hostname from the URL."""
    url = MarkdownURL(link=link, line_number=1, file_path=Path("test.md"))
    assert url.host_name() == expected_host


def test_parsed_url_returns_parse_result():
    """Returns a ParseResult from urlparse."""
    url = MarkdownURL(link="https://example.com/path?q=1#frag", line_number=1, file_path=Path("test.md"))
    parsed = url.parsed_url
    assert parsed.scheme == "https"
    assert parsed.netloc == "example.com"
    assert parsed.path == "/path"
    assert parsed.query == "q=1"
    assert parsed.fragment == "frag"


def test_is_alive_success():
    """Returns True when HEAD request succeeds."""
    url = MarkdownURL(link="https://example.com", line_number=1, file_path=Path("test.md"))
    mock_response = MagicMock()
    mock_response.is_success = True
    mock_client = MagicMock(spec=httpx.Client)
    mock_client.head.return_value = mock_response
    assert url.is_alive(timeout=5, retries=1, client=mock_client) is True


def test_is_alive_head_fails_get_succeeds():
    """Falls back to GET when HEAD fails."""
    url = MarkdownURL(link="https://example.com", line_number=1, file_path=Path("test.md"))
    head_response = MagicMock()
    head_response.is_success = False
    get_response = MagicMock()
    get_response.is_success = True
    mock_client = MagicMock(spec=httpx.Client)
    mock_client.head.return_value = head_response
    mock_client.get.return_value = get_response
    assert url.is_alive(timeout=5, retries=1, client=mock_client) is True


def test_is_alive_all_fail():
    """Returns False when both HEAD and GET fail for all retries."""
    url = MarkdownURL(link="https://example.com", line_number=1, file_path=Path("test.md"))
    head_response = MagicMock()
    head_response.is_success = False
    get_response = MagicMock()
    get_response.is_success = False
    mock_client = MagicMock(spec=httpx.Client)
    mock_client.head.return_value = head_response
    mock_client.get.return_value = get_response
    assert url.is_alive(timeout=5, retries=1, client=mock_client) is False


def test_is_alive_http_error_retries():
    """Retries on httpx.HTTPError and returns False after exhausting retries."""
    url = MarkdownURL(link="https://example.com", line_number=1, file_path=Path("test.md"))
    mock_client = MagicMock(spec=httpx.Client)
    mock_client.head.side_effect = httpx.HTTPError("timeout")
    with patch("markdown_checker.models.url.time.sleep"):
        assert url.is_alive(timeout=5, retries=2, client=mock_client) is False
    assert mock_client.head.call_count == 2


def test_is_alive_unsupported_protocol_redirect():
    """Returns True when redirect leads to a non-HTTP scheme (e.g. vscode://)."""
    url = MarkdownURL(
        link="https://vscode.dev/redirect?url=vscode://something", line_number=1, file_path=Path("test.md")
    )
    mock_client = MagicMock(spec=httpx.Client)
    mock_client.head.side_effect = httpx.UnsupportedProtocol("Request URL has an unsupported protocol 'vscode://'.")
    assert url.is_alive(timeout=5, retries=1, client=mock_client) is True


def test_is_alive_runtime_error_returns_false():
    """Returns False when client raises RuntimeError (e.g. client closed)."""
    url = MarkdownURL(link="https://example.com", line_number=1, file_path=Path("test.md"))
    mock_client = MagicMock(spec=httpx.Client)
    mock_client.head.side_effect = RuntimeError("Cannot send a request, as the client has been closed.")
    with patch("markdown_checker.models.url.time.sleep"):
        assert url.is_alive(timeout=5, retries=2, client=mock_client) is False
    assert mock_client.head.call_count == 2


def test_is_alive_creates_client_when_none():
    """Creates and closes its own httpx.Client when none is provided."""
    url = MarkdownURL(link="https://example.com", line_number=1, file_path=Path("test.md"))
    mock_response = MagicMock()
    mock_response.is_success = True
    with patch("markdown_checker.models.url.httpx.Client") as MockClient:
        mock_client_instance = MagicMock()
        mock_client_instance.head.return_value = mock_response
        MockClient.return_value = mock_client_instance
        result = url.is_alive(timeout=5, retries=1)
        assert result is True
        mock_client_instance.close.assert_called_once()


def test_is_alive_does_not_close_provided_client():
    """Does not close the client when one is provided externally."""
    url = MarkdownURL(link="https://example.com", line_number=1, file_path=Path("test.md"))
    mock_response = MagicMock()
    mock_response.is_success = True
    mock_client = MagicMock(spec=httpx.Client)
    mock_client.head.return_value = mock_response
    url.is_alive(timeout=5, retries=1, client=mock_client)
    mock_client.close.assert_not_called()
