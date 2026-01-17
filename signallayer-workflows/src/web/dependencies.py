"""Temporal client dependency for FastAPI."""

from collections.abc import Awaitable, Callable

import inject
from temporalio.client import Client

from ..worker.lib.registry import ActivityRegistry, WorkflowRegistry
from .config import WebSettings
from .config import settings as default_settings

# Import the global client getter from main
# This will be set during application startup
_client_getter: Callable[[], Awaitable[Client]] | None = None


def get_workflow_registry() -> WorkflowRegistry:
    """FastAPI dependency that provides the WorkflowRegistry."""
    return inject.instance(WorkflowRegistry)


def get_activity_registry() -> ActivityRegistry:
    """FastAPI dependency that provides the ActivityRegistry."""
    return inject.instance(ActivityRegistry)


def set_client_getter(getter: Callable[[], Awaitable[Client]]) -> None:
    """Set the global client getter function.

    Args:
        getter: Function that returns the Temporal client
    """
    global _client_getter
    _client_getter = getter


def _get_settings() -> WebSettings:
    """Get settings instance."""
    return default_settings


async def get_temporal_client() -> Client:
    """FastAPI dependency that provides a Temporal client.

    Returns the global Temporal client instance that was created during
    application startup.

    Returns:
        Connected Temporal client instance

    Raises:
        RuntimeError: If client getter is not configured

    Example:
        ```python
        @app.post("/workflow/example")
        async def execute_workflow(
            input_data: ExampleInput,
            client: Client = Depends(get_temporal_client)
        ):
            result = await client.execute_workflow(...)
            return result
        ```
    """
    if _client_getter is None:
        raise RuntimeError("Temporal client getter not configured")
    return await _client_getter()
