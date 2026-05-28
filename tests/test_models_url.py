from pathlib import Path
from unittest.mock import MagicMock
from unittest.mock import patch

import httpx2
import pytest

from markdown_checker.models.url import MarkdownURL
from markdown_checker.models.url import URLCheckResult


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


def test_check_success():
    """Returns alive when HEAD request succeeds."""
    url = MarkdownURL(link="https://example.com", line_number=1, file_path=Path("test.md"))
    mock_client = MagicMock(spec=httpx2.Client)
    mock_client.head.return_value = _make_response(200)
    result = url.check(timeout=5, retries=1, client=mock_client)
    assert result.status == "alive"


def test_check_head_fails_get_succeeds():
    """Falls back to GET when HEAD fails."""
    url = MarkdownURL(link="https://example.com", line_number=1, file_path=Path("test.md"))
    mock_client = MagicMock(spec=httpx2.Client)
    mock_client.head.return_value = _make_response(404)
    mock_client.get.return_value = _make_response(200)
    result = url.check(timeout=5, retries=1, client=mock_client)
    assert result.status == "alive"


def test_check_all_fail():
    """Returns broken when both HEAD and GET fail for all retries."""
    url = MarkdownURL(link="https://example.com", line_number=1, file_path=Path("test.md"))
    mock_client = MagicMock(spec=httpx2.Client)
    mock_client.head.return_value = _make_response(404)
    mock_client.get.return_value = _make_response(404)
    result = url.check(timeout=5, retries=1, client=mock_client)
    assert result.status == "broken"


def test_check_http_error_retries():
    """Retries on httpx2.HTTPError and returns transient_error after exhausting retries."""
    url = MarkdownURL(link="https://example.com", line_number=1, file_path=Path("test.md"))
    mock_client = MagicMock(spec=httpx2.Client)
    mock_client.head.side_effect = httpx2.HTTPError("timeout")
    with patch("markdown_checker.models.url.time.sleep"):
        result = url.check(timeout=5, retries=2, client=mock_client)
    assert result.status == "transient_error"
    assert mock_client.head.call_count == 2


def test_check_unsupported_protocol_redirect():
    """Returns alive when redirect leads to a non-HTTP scheme (e.g. vscode://)."""
    url = MarkdownURL(
        link="https://vscode.dev/redirect?url=vscode://something", line_number=1, file_path=Path("test.md")
    )
    mock_client = MagicMock(spec=httpx2.Client)
    mock_client.head.side_effect = httpx2.UnsupportedProtocol("Request URL has an unsupported protocol 'vscode://'.")
    result = url.check(timeout=5, retries=1, client=mock_client)
    assert result.status == "alive"


def test_check_runtime_error_returns_transient_error():
    """Returns transient_error when client raises RuntimeError (e.g. client closed)."""
    url = MarkdownURL(link="https://example.com", line_number=1, file_path=Path("test.md"))
    mock_client = MagicMock(spec=httpx2.Client)
    mock_client.head.side_effect = RuntimeError("Cannot send a request, as the client has been closed.")
    with patch("markdown_checker.models.url.time.sleep"):
        result = url.check(timeout=5, retries=2, client=mock_client)
    assert result.status == "transient_error"
    assert mock_client.head.call_count == 2


def _make_response(status_code: int, headers: dict | None = None) -> MagicMock:
    """Build a mock httpx2.Response with the given status code and headers."""
    resp = MagicMock(spec=httpx2.Response)
    resp.status_code = status_code
    resp.is_success = 200 <= status_code < 300
    resp.is_redirect = 300 <= status_code < 400
    resp.headers = headers or {}
    return resp


def test_check_429_with_retry_after_integer_sleeps_and_retries():
    """429 + Retry-After: 2 → sleep(2) called, request retried, returns alive on success."""
    url = MarkdownURL(link="https://example.com", line_number=1, file_path=Path("test.md"))
    mock_client = MagicMock(spec=httpx2.Client)
    rate_limited = _make_response(429, {"retry-after": "2"})
    success = _make_response(200)
    mock_client.head.side_effect = [rate_limited, success]

    with patch("markdown_checker.models.url.time.sleep") as mock_sleep:
        result = url.check(timeout=5, retries=2, client=mock_client, retry_on_429=True, fallback_retry_delay=60)

    assert result.status == "alive"
    mock_sleep.assert_called_once_with(2.0)
    assert mock_client.head.call_count == 2


def test_check_429_without_retry_after_uses_fallback():
    """429 with no Retry-After header → sleep(fallback_retry_delay) called."""
    url = MarkdownURL(link="https://example.com", line_number=1, file_path=Path("test.md"))
    mock_client = MagicMock(spec=httpx2.Client)
    rate_limited = _make_response(429, {})
    success = _make_response(200)
    mock_client.head.side_effect = [rate_limited, success]

    with patch("markdown_checker.models.url.time.sleep") as mock_sleep:
        result = url.check(timeout=5, retries=2, client=mock_client, retry_on_429=True, fallback_retry_delay=30)

    assert result.status == "alive"
    mock_sleep.assert_called_once_with(30.0)


def test_check_429_retry_succeeds():
    """After a 429, a successful retry means check returns alive."""
    url = MarkdownURL(link="https://example.com", line_number=1, file_path=Path("test.md"))
    mock_client = MagicMock(spec=httpx2.Client)
    rate_limited = _make_response(429, {"retry-after": "1"})
    success = _make_response(200)
    mock_client.head.side_effect = [rate_limited, success]

    with patch("markdown_checker.models.url.time.sleep"):
        result = url.check(timeout=5, retries=2, client=mock_client, retry_on_429=True, fallback_retry_delay=60)

    assert result.status == "alive"


def test_is_alive_retry_on_429_disabled_uses_exponential_backoff():
    """When retry_on_429=False, a 429 response uses normal exponential backoff."""
    url = MarkdownURL(link="https://example.com", line_number=1, file_path=Path("test.md"))
    mock_client = MagicMock(spec=httpx2.Client)
    rate_limited = _make_response(429, {"retry-after": "999"})
    rate_limited_get = _make_response(429, {"retry-after": "999"})
    success = _make_response(200)
    mock_client.head.side_effect = [rate_limited, success]
    mock_client.get.return_value = rate_limited_get

    with patch("markdown_checker.models.url.time.sleep") as mock_sleep:
        url.check(timeout=5, retries=2, client=mock_client, retry_on_429=False, fallback_retry_delay=60)

    # Should use exponential backoff (0.5 * 2^0 = 0.5), NOT the Retry-After value.
    mock_sleep.assert_called_once_with(0.5)


def test_check_non_success_with_retry_after_header_uses_delay():
    """Any non-success, non-redirect response with Retry-After is respected."""
    url = MarkdownURL(link="https://example.com", line_number=1, file_path=Path("test.md"))
    mock_client = MagicMock(spec=httpx2.Client)
    # 503 with Retry-After: 5 should also trigger the delay.
    throttled = _make_response(503, {"retry-after": "5"})
    success = _make_response(200)
    mock_client.head.side_effect = [throttled, success]

    with patch("markdown_checker.models.url.time.sleep") as mock_sleep:
        result = url.check(timeout=5, retries=2, client=mock_client, retry_on_429=True, fallback_retry_delay=60)

    assert result.status == "alive"
    mock_sleep.assert_called_once_with(5.0)


def test_check_creates_client_when_none():
    """Creates and closes its own httpx2.Client when none is provided."""
    url = MarkdownURL(link="https://example.com", line_number=1, file_path=Path("test.md"))
    with patch("markdown_checker.models.url.httpx2.Client") as MockClient:
        mock_client_instance = MagicMock()
        mock_client_instance.head.return_value = _make_response(200)
        MockClient.return_value = mock_client_instance
        result = url.check(timeout=5, retries=1)
        assert result.status == "alive"
        mock_client_instance.close.assert_called_once()


def test_check_does_not_close_provided_client():
    """Does not close the client when one is provided externally."""
    url = MarkdownURL(link="https://example.com", line_number=1, file_path=Path("test.md"))
    mock_client = MagicMock(spec=httpx2.Client)
    mock_client.head.return_value = _make_response(200)
    url.check(timeout=5, retries=1, client=mock_client)
    mock_client.close.assert_not_called()


# ---------------------------------------------------------------------------
# URLCheckResult dataclass
# ---------------------------------------------------------------------------


def test_url_check_result_fields():
    """URLCheckResult stores all three fields."""
    r = URLCheckResult(status="alive", http_status_code=200, retry_after=None)
    assert r.status == "alive"
    assert r.http_status_code == 200
    assert r.retry_after is None


def test_url_check_result_defaults():
    """http_status_code and retry_after default to None."""
    r = URLCheckResult(status="broken")
    assert r.http_status_code is None
    assert r.retry_after is None


# ---------------------------------------------------------------------------
# check() method — four outcome values
# ---------------------------------------------------------------------------


def test_check_returns_alive_on_2xx():
    """check() returns status='alive' when HEAD responds with 2xx."""
    url = MarkdownURL(link="https://example.com", line_number=1, file_path=Path("test.md"))
    mock_client = MagicMock(spec=httpx2.Client)
    success = _make_response(200)
    mock_client.head.return_value = success
    result = url.check(timeout=5, retries=1, client=mock_client)
    assert result.status == "alive"
    assert result.http_status_code == 200


def test_check_returns_broken_on_persistent_404():
    """check() returns status='broken' when HEAD and GET both return 404."""
    url = MarkdownURL(link="https://example.com", line_number=1, file_path=Path("test.md"))
    mock_client = MagicMock(spec=httpx2.Client)
    not_found = _make_response(404)
    mock_client.head.return_value = not_found
    mock_client.get.return_value = not_found
    result = url.check(timeout=5, retries=1, client=mock_client)
    assert result.status == "broken"
    assert result.http_status_code == 404


def test_check_returns_rate_limited_when_429_exhausts_retries():
    """check() returns status='rate_limited' when 429 persists across all retries."""
    url = MarkdownURL(link="https://example.com", line_number=1, file_path=Path("test.md"))
    mock_client = MagicMock(spec=httpx2.Client)
    rate_limited = _make_response(429, {"retry-after": "5"})
    mock_client.head.return_value = rate_limited
    with patch("markdown_checker.models.url.time.sleep"):
        result = url.check(timeout=5, retries=2, client=mock_client, retry_on_429=True, fallback_retry_delay=30)
    assert result.status == "rate_limited"
    assert result.http_status_code == 429
    assert result.retry_after == 5


def test_check_returns_broken_when_429_is_followed_by_404():
    """A later hard HTTP failure should classify the URL as broken, not rate-limited."""
    url = MarkdownURL(link="https://example.com", line_number=1, file_path=Path("test.md"))
    mock_client = MagicMock(spec=httpx2.Client)
    rate_limited = _make_response(429, {"retry-after": "5"})
    not_found = _make_response(404)
    mock_client.head.side_effect = [rate_limited, not_found]
    mock_client.get.return_value = not_found
    with patch("markdown_checker.models.url.time.sleep"):
        result = url.check(timeout=5, retries=2, client=mock_client, retry_on_429=True, fallback_retry_delay=30)
    assert result.status == "broken"
    assert result.http_status_code == 404


def test_check_returns_broken_when_network_error_is_followed_by_404():
    """A later hard HTTP failure should classify the URL as broken, not transient_error."""
    url = MarkdownURL(link="https://example.com", line_number=1, file_path=Path("test.md"))
    mock_client = MagicMock(spec=httpx2.Client)
    not_found = _make_response(404)
    mock_client.head.side_effect = [httpx2.HTTPError("timeout"), not_found]
    mock_client.get.return_value = not_found
    with patch("markdown_checker.models.url.time.sleep"):
        result = url.check(timeout=5, retries=2, client=mock_client)
    assert result.status == "broken"
    assert result.http_status_code == 404


def test_check_prefers_rate_limited_when_retries_mix_429_and_network_errors():
    """Mixed 429 and network failures without a hard HTTP failure classify as rate_limited."""
    url = MarkdownURL(link="https://example.com", line_number=1, file_path=Path("test.md"))
    mock_client = MagicMock(spec=httpx2.Client)
    rate_limited = _make_response(429, {"retry-after": "5"})
    mock_client.head.side_effect = [rate_limited, httpx2.HTTPError("timeout")]
    with patch("markdown_checker.models.url.time.sleep"):
        result = url.check(timeout=5, retries=2, client=mock_client, retry_on_429=True, fallback_retry_delay=30)
    assert result.status == "rate_limited"
    assert result.http_status_code == 429
    assert result.retry_after == 5


def test_check_returns_transient_error_on_network_failure():
    """check() returns status='transient_error' when only HTTPErrors are raised."""
    url = MarkdownURL(link="https://example.com", line_number=1, file_path=Path("test.md"))
    mock_client = MagicMock(spec=httpx2.Client)
    mock_client.head.side_effect = httpx2.HTTPError("connection refused")
    with patch("markdown_checker.models.url.time.sleep"):
        result = url.check(timeout=5, retries=2, client=mock_client)
    assert result.status == "transient_error"
    assert result.http_status_code is None


def test_check_returns_unverifiable_when_head_and_get_both_return_403():
    """check() returns status='unverifiable' when both HEAD and GET return 403."""
    url = MarkdownURL(link="https://example.com", line_number=1, file_path=Path("test.md"))
    mock_client = MagicMock(spec=httpx2.Client)
    mock_client.head.return_value = _make_response(403)
    mock_client.get.return_value = _make_response(403)
    result = url.check(timeout=5, retries=1, client=mock_client)
    assert result.status == "unverifiable"
    assert result.http_status_code == 403


def test_check_returns_unverifiable_when_head_and_get_both_return_401():
    """check() returns status='unverifiable' when both HEAD and GET return 401."""
    url = MarkdownURL(link="https://example.com", line_number=1, file_path=Path("test.md"))
    mock_client = MagicMock(spec=httpx2.Client)
    mock_client.head.return_value = _make_response(401)
    mock_client.get.return_value = _make_response(401)
    result = url.check(timeout=5, retries=1, client=mock_client)
    assert result.status == "unverifiable"
    assert result.http_status_code == 401


def test_check_returns_alive_when_head_returns_403_but_get_succeeds():
    """check() falls back to GET and returns alive when HEAD is 403 but GET succeeds."""
    url = MarkdownURL(link="https://example.com", line_number=1, file_path=Path("test.md"))
    mock_client = MagicMock(spec=httpx2.Client)
    mock_client.head.return_value = _make_response(403)
    mock_client.get.return_value = _make_response(200)
    result = url.check(timeout=5, retries=1, client=mock_client)
    assert result.status == "alive"
    assert result.http_status_code == 200


def test_check_returns_broken_when_head_returns_403_but_get_returns_404():
    """check() returns broken when HEAD is 403 but GET reveals the resource is gone (404)."""
    url = MarkdownURL(link="https://example.com", line_number=1, file_path=Path("test.md"))
    mock_client = MagicMock(spec=httpx2.Client)
    mock_client.head.return_value = _make_response(403)
    mock_client.get.return_value = _make_response(404)
    result = url.check(timeout=5, retries=1, client=mock_client)
    assert result.status == "broken"
    assert result.http_status_code == 404
