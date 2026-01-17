"""FastAPI web application for workflow execution."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import inject
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from temporalio.client import Client

from ..common.env import setup_environment
from ..common.injection import configure_inject
from ..worker.lib.registry import WorkflowRegistry

# Setup environment variables first
setup_environment()

# Configure injection before any other imports that might use it
configure_inject()

from .config import settings
from .dependencies import set_client_getter
from .routes import generate_workflow_routes

logger = structlog.get_logger()

# Global client instance
_temporal_client: Client | None = None


async def _get_temporal_client() -> Client:
    """Get or create Temporal client instance.

    Returns:
        Connected Temporal client

    Raises:
        RuntimeError: If client is not initialized
    """
    global _temporal_client
    if _temporal_client is None:
        raise RuntimeError("Temporal client not initialized")
    return _temporal_client


@inject.params(workflow_registry=WorkflowRegistry)
@asynccontextmanager
async def lifespan(app: FastAPI, workflow_registry: WorkflowRegistry) -> AsyncIterator[None]:
    """Manage application lifecycle events.

    Args:
        app: FastAPI application instance
        workflow_registry: Injected workflow registry
    """
    global _temporal_client

    # Startup
    logger.info(
        "starting_web_application",
        temporal_url=settings.temporal_url,
        namespace=settings.temporal_namespace,
    )

    try:
        from ..common.temporal_client import connect_temporal
        _temporal_client = await connect_temporal(settings)

        # Set the client getter for dependencies
        set_client_getter(_get_temporal_client)

        # Import workflows to ensure they are registered in the WorkflowRegistry
        from ..worker import workflows  # noqa: F401

        # Generate and mount workflow routes
        workflow_router = generate_workflow_routes(workflow_registry)
        app.include_router(workflow_router, prefix=settings.api_prefix)

        workflow_count = len(workflow_registry.get_all())
        logger.info(
            "workflow_routes_mounted",
            workflow_count=workflow_count,
            prefix=settings.api_prefix,
        )

    except Exception as e:
        logger.error("startup_failed", error=str(e))
        raise

    yield

    # Shutdown
    logger.info("shutting_down_web_application")
    # Temporal client connections are closed automatically


def create_app() -> FastAPI:
    """Create and configure FastAPI application.

    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="Temporal Workflow API",
        description="Dynamic REST API for Temporal workflows",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check endpoint
    from fastapi import Depends

    from .dependencies import get_workflow_registry

    @app.get("/health")
    async def health_check(
        workflow_registry: WorkflowRegistry = Depends(get_workflow_registry)
    ) -> dict[str, str | int]:
        """Health check endpoint.

        Returns:
            Health status and workflow count
        """
        workflow_count = len(workflow_registry.get_all())
        return {
            "status": "healthy",
            "workflow_count": workflow_count,
        }

    return app


app = create_app()
