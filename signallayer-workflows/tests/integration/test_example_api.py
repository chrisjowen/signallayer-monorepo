"""Integration tests for the generated workflow API."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
import inject

from src.web.main import app
from src.web.dependencies import get_temporal_client
from src.worker.workflows.example import ExampleWorkflow, ExampleOutput
from src.worker.lib.registry import WorkflowMetadata, WorkflowRegistry
from src.common.injection import configure_inject

# Ensure inject is configured for tests
configure_inject()

@pytest.fixture
def workflow_registry():
    """Workflow registry fixture."""
    return inject.instance(WorkflowRegistry)

@pytest.fixture(autouse=True)
def setup_registry(workflow_registry):
    """Ensure ExampleWorkflow is registered."""
    from src.worker.lib.type_utils import extract_run_method_types
    input_model, output_model = extract_run_method_types(ExampleWorkflow)
    metadata = WorkflowMetadata(
        workflow_class=ExampleWorkflow,
        name="example-workflow",
        input_model=input_model,
        output_model=output_model,
        version="v2",
    )
    # Clear and re-register to be safe across tests
    workflow_registry.clear()
    workflow_registry.register_workflow(metadata)
    yield
    workflow_registry.clear()

@pytest.fixture
def mock_temporal_client():
    """Create a mock Temporal client."""
    client = AsyncMock()
    return client

@pytest.fixture
def client_with_mocked_temporal(mock_temporal_client):
    """FastAPI client with mocked Temporal dependency."""
    app.dependency_overrides[get_temporal_client] = lambda: mock_temporal_client
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

def test_execute_example_workflow_api(client_with_mocked_temporal, mock_temporal_client):
    """Test that the ExampleWorkflow endpoint exists and works."""
    # Setup mock return
    mock_temporal_client.execute_workflow.return_value = ExampleOutput(
        result="Hello Test (iteration 1)",
        iterations=1
    )

    # Post to the generated endpoint
    response = client_with_mocked_temporal.post(
        "/api/v1/workflow/example-workflow-v2",
        json={"name": "Test", "count": 1}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["iterations"] == 1
    assert "Hello Test" in data["result"]
    
    # Verify the correct workflow was called
    mock_temporal_client.execute_workflow.assert_called_once()
    args, kwargs = mock_temporal_client.execute_workflow.call_args
    assert kwargs["id"].startswith("example-workflow")

def test_execute_example_workflow_async_api(client_with_mocked_temporal, mock_temporal_client):
    """Test the asynchronous execution mode of the ExampleWorkflow endpoint."""
    # Setup mock handle
    mock_handle = AsyncMock()
    mock_handle.id = "example-workflow-id"
    mock_handle.result_run_id = "run-id"
    mock_temporal_client.start_workflow.return_value = mock_handle

    # Post with async=true
    response = client_with_mocked_temporal.post(
        "/api/v1/workflow/example-workflow-v2?async=true",
        json={"name": "Test", "count": 1}
    )

    assert response.status_code == 200
    data = response.json()
    assert "workflow_id" in data
    assert "status_url" in data
    
    # Verify the workflow was started with the correct ID prefix
    mock_temporal_client.start_workflow.assert_called_once()
    _, kwargs = mock_temporal_client.start_workflow.call_args
    assert kwargs["id"].startswith("example-workflow")
    assert kwargs["id"] in data["status_url"]
