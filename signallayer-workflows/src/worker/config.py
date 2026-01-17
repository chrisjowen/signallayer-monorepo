"""Worker configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict

class WorkerSettings(BaseSettings):
    """Configuration settings for the Temporal worker."""

    model_config = SettingsConfigDict(
        env_prefix="WORKER_",
        case_sensitive=False,
        extra="ignore",
    )

    # These will automatically match WORKER_TEMPORAL_URL, etc.
    temporal_url: str = "localhost:7233"
    temporal_namespace: str = "default"
    temporal_local: bool = True
    temporal_api_key: str | None = None

    task_queue: str = "default"

    # Worker concurrency settings
    max_concurrent_workflows: int = 100
    max_concurrent_activities: int = 100


# Global settings instance
settings = WorkerSettings()
