"""Temporal client connection factory."""

from typing import Any, Protocol

import structlog
from temporalio.client import Client

from .pydantic_converter import pydantic_data_converter

logger = structlog.get_logger()


class TemporalSettings(Protocol):
    """Protocol for settings objects containing Temporal connection info."""

    temporal_url: str
    temporal_namespace: str
    temporal_local: bool
    temporal_api_key: str | None


async def connect_temporal(settings: TemporalSettings) -> Client:
    """Create and connect a Temporal client using the provided settings.

    Args:
        settings: An object providing temporal_url, temporal_namespace,
                 temporal_local, and temporal_api_key.

    Returns:
        A connected Temporal client.
    """
    logger.info(
        "connecting_to_temporal",
        url=settings.temporal_url,
        namespace=settings.temporal_namespace,
        local=settings.temporal_local,
    )

    connect_kwargs: dict[str, Any] = {
        "target_host": settings.temporal_url,
        "namespace": settings.temporal_namespace,
    }

    if not settings.temporal_local:
        connect_kwargs["tls"] = True
        if settings.temporal_api_key:
            logger.info("using_api_key_auth")
            connect_kwargs["api_key"] = settings.temporal_api_key
        else:
            logger.warning("no_api_key_provided_for_cloud_connection")

    try:
        client = await Client.connect(
            **connect_kwargs,
            data_converter=pydantic_data_converter,
        )
        logger.info("temporal_client_connected", url=settings.temporal_url)
        return client
    except Exception as e:
        logger.error(
            "temporal_connection_failed",
            url=settings.temporal_url,
            namespace=settings.temporal_namespace,
            error=str(e),
            error_type=type(e).__name__,
        )
        raise
