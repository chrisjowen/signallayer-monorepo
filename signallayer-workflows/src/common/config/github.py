"""GitHub client configuration settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class GitHubSettings(BaseSettings):
    """Settings for GitHub API client.

    Configuration is loaded from environment variables with GITHUB_ prefix.
    """

    model_config = SettingsConfigDict(
        env_prefix="GITHUB_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    token: str
    """GitHub personal access token for API authentication."""

    base_url: str = "https://api.github.com"
    """GitHub API base URL. Defaults to public GitHub API."""

    timeout_seconds: int = 30
    """HTTP request timeout in seconds."""

    max_retries: int = 3
    """Maximum number of retries for failed requests."""
