"""Workflow for batch processing condo email extraction."""

import asyncio
from typing import Optional

from pydantic import BaseModel, Field
from temporalio import workflow

from src.worker.lib.decorators import workflow_api
from src.worker.workflows.activities.condo_emails import list_condo_names
from src.worker.workflows.find_condo_emails import (
    FindCondoEmailsInput,
    FindCondoEmailsWorkflow,
)


class BatchProcessCondosInput(BaseModel):
    """Input for batch process condos workflow."""

    data_dir: str = Field(
        default="data/condos", description="Directory containing condo JSON files"
    )
    location: str = Field(default="Singapore", description="Location to use for all condos")
    batch_size: int = Field(default=5, description="Number of concurrent child workflows")
    limit: Optional[int] = Field(
        default=None, description="Max number of condos to process (for testing)"
    )


class BatchProcessCondosOutput(BaseModel):
    """Output for batch process condos workflow."""

    total_processed: int
    condos_found: int


@workflow_api(name="batch-process-condos", version="v1")
@workflow.defn
class BatchProcessCondosWorkflow:
    """Workflow that lists condos and triggers FindCondoEmailsWorkflow for each."""

    @workflow.run
    async def run(self, input: BatchProcessCondosInput) -> BatchProcessCondosOutput:
        """Execute the batch process condos workflow."""
        workflow.logger.info("Starting batch condo processing...")

        # Step 1: List all condo names and addresses
        condos = await list_condo_names.execute(input.data_dir)

        if input.limit:
            condos = condos[: input.limit]

        workflow.logger.info(f"Found {len(condos)} condos to process")

        # Step 2: Process in batches
        total_processed = 0
        batch_size = input.batch_size

        for i in range(0, len(condos), batch_size):
            batch = condos[i : i + batch_size]
            workflow.logger.info(f"Processing batch {i // batch_size + 1} ({len(batch)} condos)")

            tasks = []
            for condo in batch:
                name = condo["name"]
                address = condo["address"]
                # Use a safe ID for the child workflow
                safe_name = name.lower().replace(" ", "-").replace("/", "-")
                child_id = f"find-emails-{safe_name}"

                task = workflow.execute_child_workflow(
                    FindCondoEmailsWorkflow.run,
                    FindCondoEmailsInput(condo_name=name, address=address, location=input.location),
                    id=child_id,
                )
                tasks.append(task)

            # Wait for the batch to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for res in results:
                if isinstance(res, Exception):
                    workflow.logger.error(f"Child workflow failed: {res}")
                else:
                    total_processed += 1

        return BatchProcessCondosOutput(total_processed=total_processed, condos_found=len(condos))
