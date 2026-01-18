"""Tests for workflow registry."""

import pytest
from pydantic import BaseModel
from temporalio import workflow

from src.worker.lib.models import WorkflowMetadata
from src.worker.lib.registry import WorkflowRegistry


class TestInput(BaseModel):
    value: str


class TestOutput(BaseModel):
    result: str


@workflow.defn
class TestWorkflow:
    @workflow.run
    async def run(self, input: TestInput) -> TestOutput:
        return TestOutput(result=f"processed: {input.value}")


@workflow.defn
class AnotherTestWorkflow:
    @workflow.run
    async def run(self, input: TestInput) -> TestOutput:
        return TestOutput(result="different")


def test_registry_injection(workflow_registry):
    """Test that registry can be injected."""
    assert isinstance(workflow_registry, WorkflowRegistry)


def test_register_workflow(workflow_registry):
    """Test registering a workflow in the registry."""
    metadata = WorkflowMetadata(
        workflow_class=TestWorkflow,
        name="test-workflow",
        input_model=TestInput,
        output_model=TestOutput,
        version="v2",
    )

    workflow_registry.register_workflow(metadata)

    retrieved = workflow_registry.get("test-workflow-v2")
    assert retrieved is not None
    assert retrieved.name == "test-workflow"
    assert retrieved.workflow_class == TestWorkflow


def test_register_duplicate_raises_error(workflow_registry):
    """Test that registering duplicate workflow name raises error."""
    metadata = WorkflowMetadata(
        workflow_class=TestWorkflow,
        name="test-workflow",
        input_model=TestInput,
        output_model=TestOutput,
        version="v2",
    )

    workflow_registry.register_workflow(metadata)

    metadata_conflict = WorkflowMetadata(
        workflow_class=AnotherTestWorkflow,
        name="test-workflow",
        input_model=TestInput,
        output_model=TestOutput,
        version="v2",
    )

    with pytest.raises(ValueError, match="already registered"):
        workflow_registry.register_workflow(metadata_conflict)


def test_get_nonexistent_returns_none(workflow_registry):
    """Test that getting non-existent workflow returns None."""
    result = workflow_registry.get("nonexistent-workflow-v2")
    assert result is None


def test_get_all_workflows(workflow_registry):
    """Test getting all registered workflows."""
    metadata1 = WorkflowMetadata(
        workflow_class=TestWorkflow,
        name="workflow-one",
        input_model=TestInput,
        output_model=TestOutput,
        version="v2",
    )
    metadata2 = WorkflowMetadata(
        workflow_class=TestWorkflow,
        name="workflow-two",
        input_model=TestInput,
        output_model=TestOutput,
        version="v2",
    )

    workflow_registry.register_workflow(metadata1)
    workflow_registry.register_workflow(metadata2)

    all_workflows = workflow_registry.get_all()
    assert len(all_workflows) == 2
    assert metadata1 in all_workflows
    assert metadata2 in all_workflows


def test_clear_registry(workflow_registry):
    """Test clearing the registry."""
    metadata = WorkflowMetadata(
        workflow_class=TestWorkflow,
        name="test-workflow",
        input_model=TestInput,
        output_model=TestOutput,
        version="v2",
    )

    workflow_registry.register_workflow(metadata)
    assert len(workflow_registry.get_all()) == 1

    workflow_registry.clear()
    assert len(workflow_registry.get_all()) == 0
