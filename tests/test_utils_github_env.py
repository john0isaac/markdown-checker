import json
from pathlib import Path

from markdown_checker.utils.github_env import get_github_repo_blob_url


def test_returns_none_outside_github_actions(monkeypatch):
    """Returns None when not running inside GitHub Actions."""
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    assert get_github_repo_blob_url() is None


def test_returns_none_without_server_url(monkeypatch):
    """Returns None when GITHUB_SERVER_URL is missing."""
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.delenv("GITHUB_SERVER_URL", raising=False)
    assert get_github_repo_blob_url() is None


def test_push_event_uses_repository_and_sha(monkeypatch):
    """For push events, builds the URL from GITHUB_REPOSITORY and GITHUB_SHA."""
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")
    monkeypatch.setenv("GITHUB_EVENT_NAME", "push")
    monkeypatch.setenv("GITHUB_REPOSITORY", "john0isaac/markdown-checker")
    monkeypatch.setenv("GITHUB_SHA", "abc123")
    assert get_github_repo_blob_url() == "https://github.com/john0isaac/markdown-checker/blob/abc123"


def test_push_event_returns_none_without_repository_or_sha(monkeypatch):
    """For push events, returns None when GITHUB_REPOSITORY or GITHUB_SHA is missing."""
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")
    monkeypatch.setenv("GITHUB_EVENT_NAME", "push")
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    monkeypatch.delenv("GITHUB_SHA", raising=False)
    assert get_github_repo_blob_url() is None


def test_pull_request_event_uses_head_repo_and_sha(monkeypatch, tmp_path: Path):
    """For pull_request events, builds the URL from the head (source) repo and commit."""
    event_path = tmp_path / "event.json"
    event_path.write_text(
        json.dumps(
            {
                "pull_request": {
                    "head": {
                        "sha": "def456",
                        "repo": {"full_name": "forker/markdown-checker"},
                    }
                }
            }
        )
    )
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")
    monkeypatch.setenv("GITHUB_EVENT_NAME", "pull_request")
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(event_path))
    monkeypatch.setenv("GITHUB_REPOSITORY", "john0isaac/markdown-checker")
    monkeypatch.setenv("GITHUB_SHA", "mergecommitsha")
    assert get_github_repo_blob_url() == "https://github.com/forker/markdown-checker/blob/def456"


def test_pull_request_target_event_uses_head_repo_and_sha(monkeypatch, tmp_path: Path):
    """The pull_request_target event is treated the same as pull_request."""
    event_path = tmp_path / "event.json"
    event_path.write_text(
        json.dumps({"pull_request": {"head": {"sha": "def456", "repo": {"full_name": "forker/markdown-checker"}}}})
    )
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")
    monkeypatch.setenv("GITHUB_EVENT_NAME", "pull_request_target")
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(event_path))
    assert get_github_repo_blob_url() == "https://github.com/forker/markdown-checker/blob/def456"


def test_pull_request_event_returns_none_without_event_path(monkeypatch):
    """Returns None when GITHUB_EVENT_PATH is missing for a pull_request event."""
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")
    monkeypatch.setenv("GITHUB_EVENT_NAME", "pull_request")
    monkeypatch.delenv("GITHUB_EVENT_PATH", raising=False)
    assert get_github_repo_blob_url() is None


def test_pull_request_event_returns_none_on_malformed_payload(monkeypatch, tmp_path: Path):
    """Returns None when the event payload is missing expected fields."""
    event_path = tmp_path / "event.json"
    event_path.write_text(json.dumps({"pull_request": {}}))
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")
    monkeypatch.setenv("GITHUB_EVENT_NAME", "pull_request")
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(event_path))
    assert get_github_repo_blob_url() is None


def test_pull_request_event_returns_none_on_invalid_json(monkeypatch, tmp_path: Path):
    """Returns None when the event payload file is not valid JSON."""
    event_path = tmp_path / "event.json"
    event_path.write_text("not json")
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_SERVER_URL", "https://github.com")
    monkeypatch.setenv("GITHUB_EVENT_NAME", "pull_request")
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(event_path))
    assert get_github_repo_blob_url() is None
