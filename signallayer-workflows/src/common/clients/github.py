"""GitHub API client for collaboration platform integration."""

from datetime import datetime
from typing import Any

import inject
import httpx
from pydantic import BaseModel

from ..config.github import GitHubSettings
from ..models import IssueDetails, IssueReference


class GitHubIssue(BaseModel):
    """GitHub API issue response model."""

    number: int
    title: str
    body: str | None = None
    state: str
    labels: list[dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    user: dict[str, Any]
    html_url: str


class GitHubClient:
    """Client for interacting with GitHub API.

    Handles authentication, rate limiting, and API interactions.
    Returns platform-agnostic models for use by CollaborationContext.
    """

    @inject.params(settings=GitHubSettings)
    def __init__(self, settings: GitHubSettings):
        """Initialize GitHub client.

        Args:
            settings: GitHub settings (injected via DI)
        """
        self.settings = settings
        self.base_url = self.settings.base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {self.settings.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def fetch_issues_by_label(
        self, repository: str, label: str, state: str = "open"
    ) -> list[IssueReference]:
        """Fetch issues from a GitHub repository filtered by label.

        Args:
            repository: Repository in format "owner/repo"
            label: Label to filter by
            state: Issue state filter (open, closed, all)

        Returns:
            List of issue references
        """
        url = f"{self.base_url}/repos/{repository}/issues"
        params = {"labels": label, "state": state, "per_page": 100}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            issues_data = response.json()

        return [
            IssueReference(
                platform="github",
                number=issue["number"],
                repository=repository,
                title=issue["title"],
                url=issue["html_url"],
            )
            for issue in issues_data
        ]

    async def fetch_issue_details(self, repository: str, issue_number: int) -> IssueDetails:
        """Fetch complete details for a specific GitHub issue.

        Args:
            repository: Repository in format "owner/repo"
            issue_number: Issue number

        Returns:
            Complete issue details
        """
        url = f"{self.base_url}/repos/{repository}/issues/{issue_number}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            issue_data = response.json()

        # Parse into GitHub model first for validation
        github_issue = GitHubIssue(**issue_data)

        # Convert to platform-agnostic model
        return IssueDetails(
            platform="github",
            number=github_issue.number,
            repository=repository,
            title=github_issue.title,
            body=github_issue.body or "",
            labels=[label["name"] for label in github_issue.labels],
            state=github_issue.state,
            created_at=github_issue.created_at,
            updated_at=github_issue.updated_at,
            author=github_issue.user["login"],
            url=github_issue.html_url,
        )

    async def post_comment(self, repository: str, issue_number: int, body: str) -> int:
        """Post a comment on a GitHub issue.

        Args:
            repository: Repository in format "owner/repo"
            issue_number: Issue number
            body: Comment body

        Returns:
            Comment ID
        """
        url = f"{self.base_url}/repos/{repository}/issues/{issue_number}/comments"
        payload = {"body": body}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json().get("id")

    async def get_comment(self, repository: str, comment_id: int) -> str:
        """Get the body of a GitHub issue comment.
        
        Args:
            repository: Repository in format "owner/repo"
            comment_id: Comment ID
            
        Returns:
            Comment body
        """
        url = f"{self.base_url}/repos/{repository}/issues/comments/{comment_id}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json().get("body", "")

    async def list_comments(self, repository: str, issue_number: int) -> list[dict]:
        """List comments on a GitHub issue.

        Args:
            repository: Repository in format "owner/repo"
            issue_number: Issue number

        Returns:
            List of comment dictionaries
        """
        url = f"{self.base_url}/repos/{repository}/issues/{issue_number}/comments"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            comments_data = response.json()

        return [
            {
                "id": comment["id"],
                "body": comment["body"],
                "author": comment["user"]["login"],
                "created_at": comment["created_at"],
            }
            for comment in comments_data
        ]

    async def update_comment(self, repository: str, comment_id: int, body: str) -> None:
        """Update a comment on a GitHub issue.

        Args:
            repository: Repository in format "owner/repo"
            comment_id: Comment ID
            body: Comment body
        """
        url = f"{self.base_url}/repos/{repository}/issues/comments/{comment_id}"
        payload = {"body": body}

        async with httpx.AsyncClient() as client:
            response = await client.patch(url, headers=self.headers, json=payload)
            response.raise_for_status()

    async def add_labels(self, repository: str, issue_number: int, labels: list[str]) -> None:
        """Add labels to an issue.

        Args:
            repository: Repository in format "owner/repo"
            issue_number: Issue number
            labels: List of labels to add
        """
        url = f"{self.base_url}/repos/{repository}/issues/{issue_number}/labels"
        payload = {"labels": labels}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()

    async def remove_label(self, repository: str, issue_number: int, label: str) -> None:
        """Remove a label from an issue.

        Args:
            repository: Repository in format "owner/repo"
            issue_number: Issue number
            label: Label name to remove
        """
        url = f"{self.base_url}/repos/{repository}/issues/{issue_number}/labels/{label}"

        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=self.headers)
            # Ignore 404 (label already removed)
            if response.status_code != 404:
                response.raise_for_status()
