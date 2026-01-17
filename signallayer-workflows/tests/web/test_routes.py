"""Tests for dynamic route generation."""

from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel
from temporalio import workflow
import inject

from src.web.routes import generate_workflow_routes
from src.worker.lib.decorators import workflow_api
from src.worker.lib.registry import WorkflowRegistry


# Test models
class TestWorkflowInput(BaseModel):
    """Test input model."""

    name: str
    value: int


class TestWorkflowOutput(BaseModel):
    """Test output model."""

    result: str


# Module-level workflows (Temporal requirement)
@workflow.defn
class TestWorkflow:
    """Test workflow for route testing."""

    @workflow.run
    async def run(self, input_data: TestWorkflowInput) -> TestWorkflowOutput:
        """Run the workflow."""
        return TestWorkflowOutput(result=f"Processed {input_data.name}")


@workflow.defn
class AnotherWorkflow:
    """Another test workflow."""

    @workflow.run
    async def run(self, input_data: TestWorkflowInput) -> TestWorkflowOutput:
        """Run the workflow."""
        return TestWorkflowOutput(result="Another")


@pytest.fixture
def workflow_registry():
    """Workflow registry fixture."""
    # Ensure injection is configured for these tests
    from src.common.injection import configure_inject
    configure_inject()
    return inject.instance(WorkflowRegistry)


@pytest.fixture(autouse=True)
def clear_registry(workflow_registry):
    """Clear registry before each test."""
    workflow_registry.clear()
    yield
    workflow_registry.clear()


@pytest.fixture
def mock_temporal_client():
    """Create a mock Temporal client."""
    client = AsyncMock()
    client.execute_workflow = AsyncMock()
    client.start_workflow = AsyncMock()
    client.close = AsyncMock()
    return client


@pytest.fixture
def app_with_routes(mock_temporal_client, workflow_registry):
    """Create FastAPI app with workflow routes."""
    # Register test workflow
    workflow_api(name="test-workflow", version="v2")(TestWorkflow)

    # Create app with routes
    app = FastAPI()

    # Mock the get_temporal_client dependency
    async def override_get_temporal_client():
        return mock_temporal_client

    from src.web.dependencies import get_temporal_client

    app.dependency_overrides[get_temporal_client] = override_get_temporal_client

    # Generate and include routes
    router = generate_workflow_routes(workflow_registry)
    app.include_router(router, prefix="/api/v1")

    return app


def test_generate_workflow_routes_creates_router(workflow_registry):
    """Test that generate_workflow_routes creates an APIRouter."""
    workflow_api(name="example", version="v2")(TestWorkflow)

    router = generate_workflow_routes(workflow_registry)

    assert router is not None
    assert len(router.routes) > 0


def test_route_path_includes_workflow_name_and_version(workflow_registry):
    """Test that generated route path includes workflow name and version."""
    workflow_api(name="test-workflow", version="v2")(TestWorkflow)

    router = generate_workflow_routes(workflow_registry)

    # Find the route
    route_paths = [route.path for route in router.routes]
    assert "/workflow/test-workflow-v2" in route_paths


def test_sync_workflow_execution(app_with_routes, mock_temporal_client):
    """Test synchronous workflow execution."""
    client = TestClient(app_with_routes)

    # Mock successful execution
    mock_temporal_client.execute_workflow.return_value = TestWorkflowOutput(
        result="Processed test"
    )

    response = client.post(
        "/api/v1/workflow/test-workflow-v2", json={"name": "test", "value": 42}
    )

    assert response.status_code == 200
    assert response.json() == {"result": "Processed test"}
    mock_temporal_client.execute_workflow.assert_called_once()


def test_async_workflow_execution(app_with_routes, mock_temporal_client):
    """Test asynchronous workflow execution."""
    client = TestClient(app_with_routes)

    # Mock workflow handle
    mock_handle = Mock()
    mock_handle.id = "test-workflow-20250110-abc123"
    mock_handle.result_run_id = "run-xyz789"
    mock_temporal_client.start_workflow.return_value = mock_handle

    response = client.post(
        "/api/v1/workflow/test-workflow-v2?async=true",
        json={"name": "test", "value": 42},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["workflow_id"] == "test-workflow-20250110-abc123"
    assert data["run_id"] == "run-xyz789"
    assert "status_url" in data
    mock_temporal_client.start_workflow.assert_called_once()


def test_invalid_input_returns_422(app_with_routes):
    """Test that invalid input returns 422 validation error."""
    client = TestClient(app_with_routes)

    response = client.post(
        "/api/v1/workflow/test-workflow-v2",
        json={"name": "test"},  # Missing 'value' field
    )

    assert response.status_code == 422


def test_multiple_workflows_generate_multiple_routes(workflow_registry):
    """Test that multiple workflows create multiple routes."""
    workflow_api(name="workflow-one", version="v2")(TestWorkflow)
    workflow_api(name="workflow-two", version="v2")(AnotherWorkflow)

    router = generate_workflow_routes(workflow_registry)

    route_paths = [route.path for route in router.routes]
    assert "/workflow/workflow-one-v2" in route_paths
    assert "/workflow/workflow-two-v2" in route_paths


def test_route_accepts_post_method_only(app_with_routes):
    """Test that routes only accept POST method."""
    client = TestClient(app_with_routes)

    get_response = client.get("/api/v1/workflow/test-workflow-v2")
    assert get_response.status_code == 405  # Method Not Allowed

    put_response = client.put(
        "/api/v1/workflow/test-workflow-v2", json={"name": "test", "value": 42}
    )
    assert put_response.status_code == 405


def test_openapi_schema_includes_workflow_endpoint(app_with_routes):
    """Test that OpenAPI schema includes the generated endpoint."""
    client = TestClient(app_with_routes)

    response = client.get("/openapi.json")
    assert response.status_code == 200

    schema = response.json()
    assert "/api/v1/workflow/test-workflow-v2" in schema["paths"]

    endpoint = schema["paths"]["/api/v1/workflow/test-workflow-v2"]
    assert "post" in endpoint
    # router.add_api_route parameters are handled by FastAPI and might not be explicitly in endpoint[post] if they are from query or body
    # but let's check for the async query parameter in parameters list
    params = endpoint["post"].get("parameters", [])
    async_param = next((p for p in params if p["name"] == "async"), None)
    assert async_param is not None
    assert async_param["in"] == "query"
