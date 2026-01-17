"""Tests for GitHubClient."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest

from src.common.clients.github import GitHubClient
from src.common.models import IssueDetails, IssueReference


@pytest.fixture
def github_client() -> GitHubClient:
    """Create a GitHub client for testing."""
    from src.common.config.github import GitHubSettings

    settings = GitHubSettings(token="test-token")
    return GitHubClient(settings=settings)


@pytest.fixture
def mock_github_issue_response() -> dict:
    """Mock GitHub API issue response."""
    return {
        "number": 123,
        "title": "Test Issue",
        "body": "Test body",
        "state": "open",
        "labels": [{"name": "check-demand"}, {"name": "priority-high"}],
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-02T00:00:00Z",
        "user": {"login": "testuser"},
        "html_url": "https://github.com/owner/repo/issues/123",
    }


@pytest.mark.asyncio
async def test_fetch_issues_by_label(github_client: GitHubClient) -> None:
    """Test fetching issues by label."""
    mock_response_data = [
        {
            "number": 1,
            "title": "Issue 1",
            "html_url": "https://github.com/owner/repo/issues/1",
        },
        {
            "number": 2,
            "title": "Issue 2",
            "html_url": "https://github.com/owner/repo/issues/2",
        },
    ]

    with patch("src.common.clients.github.httpx.AsyncClient") as mock_client_class:
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value=mock_response_data)
        mock_response.raise_for_status = AsyncMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client

        issues = await github_client.fetch_issues_by_label("owner/repo", "check-demand")

        assert len(issues) == 2
        assert all(isinstance(issue, IssueReference) for issue in issues)
        assert issues[0].number == 1
        assert issues[0].title == "Issue 1"
        assert issues[0].platform == "github"
        assert issues[0].repository == "owner/repo"


@pytest.mark.asyncio
async def test_fetch_issue_details(
    github_client: GitHubClient, mock_github_issue_response: dict
) -> None:
    """Test fetching issue details."""
    with patch("src.common.clients.github.httpx.AsyncClient") as mock_client_class:
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value=mock_github_issue_response)
        mock_response.raise_for_status = AsyncMock()

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client

        details = await github_client.fetch_issue_details("owner/repo", 123)

        assert isinstance(details, IssueDetails)
        assert details.number == 123
        assert details.title == "Test Issue"
        assert details.body == "Test body"
        assert details.platform == "github"
        assert details.repository == "owner/repo"
        assert details.labels == ["check-demand", "priority-high"]
        assert details.author == "testuser"
        assert details.state == "open"


def test_github_client_requires_token() -> None:
    """Test that GitHubClient requires a token."""
    from pydantic import ValidationError
    from src.common.config.github import GitHubSettings

    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValidationError):
            # GitHubSettings will raise ValidationError if token is missing
            GitHubSettings()
