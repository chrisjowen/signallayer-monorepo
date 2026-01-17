"""Collaboration context using Strategy Pattern for platform delegation."""

import inject

from src.common.clients.github import GitHubClient
from src.common.models import IssueDetails, IssueReference


class CollaborationContext:
    """Context for collaboration platform operations using Strategy Pattern.

    Delegates to platform-specific clients (GitHubClient, LinearClient, etc.)
    to maintain clean domain boundaries and follow SRP.
    """

    @inject.autoparams()
    def __init__(self, github_client: GitHubClient):
        """Initialize collaboration context with platform clients.

        Args:
            github_client: GitHub API client
        """
        self.github_client = github_client

    async def fetch_issues_by_label(
        self, platform: str, repository: str, label: str, state: str = "open"
    ) -> list[IssueReference]:
        """Fetch issues from a collaboration platform filtered by label.

        Args:
            platform: Platform name ('github', 'linear', etc.)
            repository: Repository or project identifier
            label: Label to filter by
            state: Issue state filter

        Returns:
            List of issue references

        Raises:
            ValueError: If platform is not supported
        """
        if platform == "github":
            return await self.github_client.fetch_issues_by_label(repository, label, state)
        else:
            raise ValueError(f"Unsupported platform: {platform}")

    async def fetch_issue_details(
        self, platform: str, repository: str, issue_number: int
    ) -> IssueDetails:
        """Fetch complete details for a specific issue.

        Args:
            platform: Platform name ('github', 'linear', etc.)
            repository: Repository or project identifier
            issue_number: Issue number

        Returns:
            Complete issue details

        Raises:
            ValueError: If platform is not supported
        """
        if platform == "github":
            return await self.github_client.fetch_issue_details(repository, issue_number)
        else:
            raise ValueError(f"Unsupported platform: {platform}")

    async def post_comment(
        self, platform: str, repository: str, issue_number: int, body: str
    ) -> int:
        """Post a comment on an issue.

        Args:
            platform: Platform name
            repository: Repository identifier
            issue_number: Issue number
            body: Comment body

        Returns:
            Comment ID

        Raises:
            ValueError: If platform is not supported
        """
        if platform == "github":
            return await self.github_client.post_comment(repository, issue_number, body)
        else:
            raise ValueError(f"Unsupported platform: {platform}")

    async def update_comment(
        self, platform: str, repository: str, comment_id: int, body: str
    ) -> None:
        """Update a comment on an issue.

        Args:
            platform: Platform name
            repository: Repository identifier
            comment_id: Comment ID
            body: New comment body

        Raises:
            ValueError: If platform is not supported
        """
        if platform == "github":
            await self.github_client.update_comment(repository, comment_id, body)
        else:
            raise ValueError(f"Unsupported platform: {platform}")

    async def get_comment(
        self, platform: str, repository: str, comment_id: int
    ) -> str:
        """Get a comment body.

        Args:
            platform: Platform name
            repository: Repository identifier
            comment_id: Comment ID

        Returns:
            Comment body

        Raises:
            ValueError: If platform is not supported
        """
        if platform == "github":
            return await self.github_client.get_comment(repository, comment_id)
        else:
            raise ValueError(f"Unsupported platform: {platform}")

    async def list_comments(
        self, platform: str, repository: str, issue_number: int
    ) -> list[dict]:
        """List comments on an issue.

        Args:
            platform: Platform name
            repository: Repository identifier
            issue_number: Issue number

        Returns:
            List of comment dictionaries

        Raises:
            ValueError: If platform is not supported
        """
        if platform == "github":
            return await self.github_client.list_comments(repository, issue_number)
        else:
            raise ValueError(f"Unsupported platform: {platform}")

    async def add_labels(
        self, platform: str, repository: str, issue_number: int, labels: list[str]
    ) -> None:
        """Add labels to an issue.

        Args:
            platform: Platform name
            repository: Repository identifier
            issue_number: Issue number
            labels: List of labels to add

        Raises:
            ValueError: If platform is not supported
        """
        if platform == "github":
            await self.github_client.add_labels(repository, issue_number, labels)
        else:
            raise ValueError(f"Unsupported platform: {platform}")

    async def remove_label(
        self, platform: str, repository: str, issue_number: int, label: str
    ) -> None:
        """Remove a label from an issue.

        Args:
            platform: Platform name
            repository: Repository identifier
            issue_number: Issue number
            label: Label to remove

        Raises:
            ValueError: If platform is not supported
        """
        if platform == "github":
            await self.github_client.remove_label(repository, issue_number, label)
        else:
            raise ValueError(f"Unsupported platform: {platform}")
