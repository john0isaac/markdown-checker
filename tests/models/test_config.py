import httpx2

from markdown_checker.models.config import Config
from markdown_checker.models.config import create_http_client
from markdown_checker.models.config import DEFAULT_HEADERS


def test_config_defaults():
    """Config exposes the documented default values."""
    config = Config()
    assert config.skip_domains == []
    assert config.skip_urls_containing == []
    assert config.tracking_domains == []
    assert config.timeout == 20
    assert config.retries == 3
    assert config.retry_on_429 is True
    assert config.fallback_retry_delay == 30
    assert config.max_workers == 10
    assert config.per_host_delay == 0.5
    assert config.max_pending == 200
    assert config.output_mode == "local"


def test_config_is_frozen():
    """Config instances are immutable."""
    config = Config()
    try:
        config.timeout = 5  # type: ignore[misc]
    except Exception as exc:
        assert type(exc).__name__ == "FrozenInstanceError"
    else:
        raise AssertionError("Config should be frozen")


def test_config_field_defaults_are_independent_lists():
    """Mutating one Config instance's list fields doesn't affect another's."""
    a = Config()
    b = Config()
    a.skip_domains.append("example.com")
    assert b.skip_domains == []


def test_create_http_client_uses_default_headers():
    """create_http_client() builds a client with the default headers when none are given."""
    client = create_http_client()
    try:
        assert isinstance(client, httpx2.Client)
        for key, value in DEFAULT_HEADERS.items():
            assert client.headers.get(key) == value
    finally:
        client.close()


def test_create_http_client_uses_custom_headers():
    """create_http_client() honors custom headers when provided."""
    client = create_http_client(headers={"X-Custom": "value"})
    try:
        assert client.headers.get("X-Custom") == "value"
    finally:
        client.close()


def test_create_http_client_follows_redirects():
    """create_http_client() is configured to follow redirects up to 10 hops."""
    client = create_http_client()
    try:
        assert client.follow_redirects is True
        assert client.max_redirects == 10
    finally:
        client.close()
