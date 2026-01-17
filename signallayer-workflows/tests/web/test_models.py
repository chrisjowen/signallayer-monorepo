"""Tests for web response models."""

from src.web.models import ErrorResponse, WorkflowHandleResponse


def test_workflow_handle_response_creation():
    """Test creating WorkflowHandleResponse."""
    response = WorkflowHandleResponse(
        workflow_id="test-workflow-123",
        run_id="run-456",
        status_url="/api/v1/workflow/test-v2/status/test-workflow-123",
    )

    assert response.workflow_id == "test-workflow-123"
    assert response.run_id == "run-456"
    assert response.status_url == "/api/v1/workflow/test-v2/status/test-workflow-123"


def test_workflow_handle_response_model_dump():
    """Test serializing WorkflowHandleResponse to dict."""
    response = WorkflowHandleResponse(
        workflow_id="test-123",
        run_id="run-456",
        status_url="/status/test-123",
    )

    data = response.model_dump()
    assert data == {
        "workflow_id": "test-123",
        "run_id": "run-456",
        "status_url": "/status/test-123",
    }


def test_error_response_creation():
    """Test creating ErrorResponse."""
    response = ErrorResponse(
        error="ValidationError", message="Input data is invalid", details={"field": "name"}
    )

    assert response.error == "ValidationError"
    assert response.message == "Input data is invalid"
    assert response.details == {"field": "name"}


def test_error_response_without_details():
    """Test creating ErrorResponse without details."""
    response = ErrorResponse(error="NotFound", message="Workflow not found")

    assert response.error == "NotFound"
    assert response.message == "Workflow not found"
    assert response.details is None


def test_error_response_model_dump():
    """Test serializing ErrorResponse to dict."""
    response = ErrorResponse(
        error="InternalError",
        message="Something went wrong",
        details={"trace_id": "abc123"},
    )

    data = response.model_dump()
    assert data == {
        "error": "InternalError",
        "message": "Something went wrong",
        "details": {"trace_id": "abc123"},
    }
