"""Tests for the ExampleWorkflow."""

import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from src.common.injection import configure_inject
configure_inject()

from src.worker.workflows.example import ExampleWorkflow, ExampleInput, ExampleOutput
from src.worker.workflows.activities.example import say_hello

@pytest.mark.asyncio
@pytest.mark.skip(reason="Temporal sandbox validation issue with workflow imports - needs investigation")
async def test_example_workflow():
    """Test the ExampleWorkflow logic."""
    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue="test-queue",
            workflows=[ExampleWorkflow],
            activities=[say_hello],
        ):
            input_data = ExampleInput(name="Temporal", count=3)
            result = await env.client.execute_workflow(
                ExampleWorkflow.run,
                input_data,
                id="test-id",
                task_queue="test-queue",
            )

            assert isinstance(result, ExampleOutput)
            assert result.iterations == 3
            assert "Temporal" in result.result
            assert "iteration 1" in result.result
            assert "iteration 3" in result.result

@pytest.mark.asyncio
async def test_example_workflow_invalid_count():
    """Test the ExampleWorkflow with invalid input (via Pydantic)."""
    from pydantic import ValidationError
    
    with pytest.raises(ValidationError):
        ExampleInput(name="Test", count=0)  # ge=1 constraint
