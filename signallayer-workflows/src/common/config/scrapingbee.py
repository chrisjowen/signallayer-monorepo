"""ScrapingBee client configuration settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ScrapingBeeSettings(BaseSettings):
    """Settings for ScrapingBee API client.

    Configuration is loaded from environment variables.
    """

    model_config = SettingsConfigDict(
        env_prefix="SCRAPING_BEE_",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_key: str = "DUMMY_API_KEY"
    """ScrapingBee API key."""

    timeout: int = 60
    """ScrapingBee timeout in seconds."""
