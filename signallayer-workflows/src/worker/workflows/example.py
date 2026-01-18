"""Example workflows demonstrating the workflow API."""

from pydantic import BaseModel, Field
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from ..lib.decorators import workflow_api
    from .activities.example import say_hello


class ExampleInput(BaseModel):
    """Input model for example workflow."""

    name: str = Field(..., description="Name to process")
    count: int = Field(default=1, ge=1, le=100, description="Number of iterations")


class ExampleOutput(BaseModel):
    """Output model for example workflow."""

    result: str = Field(..., description="Processed result")
    iterations: int = Field(..., description="Number of iterations performed")


@workflow_api(name="example-workflow", version="v2")
@workflow.defn
class ExampleWorkflow:
    """Example workflow that demonstrates basic functionality."""

    @workflow.run
    async def run(self, input: ExampleInput) -> ExampleOutput:
        """Execute the example workflow.

        Args:
            input: Workflow input data

        Returns:
            Workflow execution result
        """
        # Simulate some processing
        results = []
        for i in range(input.count):
            # Use the .execute() magic provided by @configured_activity
            message = await say_hello.execute(input.name)
            results.append(f"{message} (iteration {i + 1})")
            # Small sleep to simulate work
            await workflow.sleep(0.1)

        return ExampleOutput(
            result=", ".join(results),
            iterations=input.count,
        )
