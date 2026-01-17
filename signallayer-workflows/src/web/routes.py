"""Dynamic route generation for workflow endpoints."""

import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, Query
from temporalio.client import Client

if TYPE_CHECKING:
    from ..worker.lib.registry import WorkflowMetadata, WorkflowRegistry

from .config import settings
from .dependencies import get_temporal_client
from .models import ErrorResponse, WorkflowHandleResponse


def generate_workflow_routes(workflow_registry: "WorkflowRegistry") -> APIRouter:
    """Generate FastAPI routes for all registered workflows."""
    router = APIRouter(prefix="/workflow", tags=["workflows"])

    # Get all registered workflows
    workflows = workflow_registry.get_all()

    for metadata in workflows:
        # Create route for this workflow
        _add_workflow_route(router, metadata)

    return router


def _add_workflow_route(router: APIRouter, metadata: "WorkflowMetadata") -> None:
    """Add a single workflow route to the router.

    Args:
        router: FastAPI router to add the route to
        metadata: Workflow metadata containing models and configuration
    """
    # Extract models for type hints
    input_model = metadata.input_model
    output_model = metadata.output_model
    workflow_name = f"{metadata.name}-{metadata.version}"
    workflow_class = metadata.workflow_class

    async def execute_workflow_endpoint(
        input_data: input_model,  # type: ignore[valid-type]
        async_execution: bool = Query(
            False,
            alias="async",
            description="Execute workflow asynchronously and return handle",
        ),
        client: Client = Depends(get_temporal_client),
    ) -> output_model | WorkflowHandleResponse:  # type: ignore[valid-type]
        """Execute workflow with the provided input.

        Args:
            input_data: Validated input data matching workflow input model
            async_execution: Whether to execute asynchronously
            client: Temporal client for workflow execution

        Returns:
            Workflow result (sync mode) or workflow handle (async mode)
        """
        # Generate unique workflow ID
        timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        workflow_id = f"{metadata.name}-{timestamp}-{uuid.uuid4().hex[:8]}"

        if async_execution:
            # Start workflow asynchronously
            handle = await client.start_workflow(
                workflow_class.run,  # type: ignore[attr-defined]
                input_data,
                id=workflow_id,
                task_queue=settings.task_queue,
            )

            # Return handle information
            status_url = (
                f"{settings.api_prefix}/workflow/{workflow_name}/status/{workflow_id}"
            )
            return WorkflowHandleResponse(
                workflow_id=handle.id,
                run_id=handle.result_run_id or "",
                status_url=status_url,
            )
        else:
            # Execute workflow synchronously and wait for result
            # Use task queue from settings or metadata
            task_queue = metadata.task_queue or settings.task_queue

            result = await client.execute_workflow(
                workflow_class.run,  # type: ignore[attr-defined]
                input_data,
                id=workflow_id,
                task_queue=task_queue,
            )
            return result  # type: ignore[no-any-return]

    # Set endpoint metadata
    execute_workflow_endpoint.__name__ = f"execute_{metadata.name.replace('-', '_')}"
    execute_workflow_endpoint.__doc__ = (
        f"Execute {metadata.name} workflow.\n\n"
        f"Supports both synchronous and asynchronous execution modes."
    )

    # Add route to router
    router.add_api_route(
        f"/{workflow_name}",
        execute_workflow_endpoint,
        methods=["POST"],
        response_model=output_model | WorkflowHandleResponse,
        status_code=200,
        responses={
            200: {
                "description": "Workflow executed successfully (sync mode)",
                "model": output_model,
            },
            202: {
                "description": "Workflow started successfully (async mode)",
                "model": WorkflowHandleResponse,
            },
            422: {"description": "Invalid input data", "model": ErrorResponse},
        },
        summary=f"Execute {workflow_name} workflow",
        description=(
            f"Execute the {workflow_name} workflow with the provided input data.\n\n"
            f"**Sync Mode (default):** Returns workflow result directly.\n"
            f"**Async Mode (async=true):** Starts workflow and returns handle for tracking."
        ),
    )
