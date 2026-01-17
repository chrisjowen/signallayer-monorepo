"""Web application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict

class WebSettings(BaseSettings):
    """Configuration settings for the web application.

    All settings are prefixed with WEB_ in environment variables.
    """

    model_config = SettingsConfigDict(
        env_prefix="WEB_",
        case_sensitive=False,
        extra="ignore",
    )

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000

    # Temporal connection settings
    temporal_url: str = "localhost:7233"
    temporal_namespace: str = "default"
    temporal_local: bool = True
    temporal_api_key: str | None = None
    temporal_timeout: int = 30
    task_queue: str = "default"

    # API settings
    api_prefix: str = "/api/v1"


# Global settings instance
settings = WebSettings()
