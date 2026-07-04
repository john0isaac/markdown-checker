"""
Module to determine the GitHub repository blob URL when running inside GitHub Actions.
"""

import json
import os
from pathlib import Path


def get_github_repo_blob_url() -> str | None:
    """
    Build the ``<server>/<owner>/<repo>/blob/<sha>`` URL for the commit currently being checked,
    inferring the correct source repository from the GitHub Actions event context.

    For ``pull_request``/``pull_request_target`` events, the source (head) repository and commit
    are used so links point at the contributor's fork/branch rather than the base repo's merge
    commit. For all other events (e.g. ``push``), the repository and commit that triggered the
    workflow are used.

    Returns:
        The blob base URL, or ``None`` if not running in GitHub Actions or the required
        information could not be determined.
    """
    if os.environ.get("GITHUB_ACTIONS") != "true":
        return None

    server_url = os.environ.get("GITHUB_SERVER_URL")
    if not server_url:
        return None

    if os.environ.get("GITHUB_EVENT_NAME") in ("pull_request", "pull_request_target"):
        return _pull_request_blob_url(server_url)

    repo_full_name = os.environ.get("GITHUB_REPOSITORY")
    sha = os.environ.get("GITHUB_SHA")
    if not repo_full_name or not sha:
        return None
    return f"{server_url}/{repo_full_name}/blob/{sha}"


def _pull_request_blob_url(server_url: str) -> str | None:
    """Build the blob URL for a pull_request event, using the head (source) repo and commit."""
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        return None

    try:
        payload = json.loads(Path(event_path).read_text(encoding="utf-8"))
        head = payload["pull_request"]["head"]
        repo_full_name = head["repo"]["full_name"]
        sha = head["sha"]
    except (OSError, ValueError, KeyError, TypeError):
        return None

    if not repo_full_name or not sha:
        return None
    return f"{server_url}/{repo_full_name}/blob/{sha}"
