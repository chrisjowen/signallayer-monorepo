"""Response models for workflow API."""

from pydantic import BaseModel, Field


class WorkflowHandleResponse(BaseModel):
    """Response model for asynchronous workflow execution.

    Returned when a workflow is started in async mode (async=true query parameter).
    Contains identifiers to track and query the workflow status.
    """

    workflow_id: str = Field(..., description="Unique identifier for the workflow instance")
    run_id: str = Field(..., description="Temporal run ID for this workflow execution")
    status_url: str = Field(
        ...,
        description="URL to check workflow status",
        examples=["/api/v1/workflow/example-workflow-v2/status/workflow-123"],
    )


class ErrorResponse(BaseModel):
    """Standard error response model.

    Used for all error responses from the API.
    """

    error: str = Field(..., description="Error type or code")
    message: str = Field(..., description="Human-readable error message")
    details: dict[str, object] | None = Field(
        None, description="Additional error details"
    )
