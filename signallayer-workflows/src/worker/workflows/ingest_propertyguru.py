"""Workflow for ingesting PropertyGuru autocomplete data for Singapore streets."""

import asyncio

from pydantic import BaseModel, Field
from temporalio import workflow

from src.worker.lib.decorators import workflow_api
from src.worker.workflows.activities.propertyguru import (
    fetch_propertyguru_autocomplete,
    load_streets_list,
    save_propertyguru_data,
)


class IngestPropertyGuruInput(BaseModel):
    """Input for PropertyGuru ingestion workflow."""

    streets_file: str = Field(
        default="data/singapore.streets.json",
        description="Path to the JSON file containing street names",
    )
    output_dir: str = Field(default="data", description="Directory to save the output files")
    max_concurrent: int = Field(default=10, description="Maximum number of concurrent API requests")


class IngestPropertyGuruOutput(BaseModel):
    """Output from PropertyGuru ingestion workflow."""

    total_streets: int = Field(..., description="Total number of streets processed")
    successful: int = Field(..., description="Number of successful fetches")
    failed: int = Field(..., description="Number of failed fetches")
    failed_streets: list[str] = Field(
        default_factory=list, description="List of streets that failed"
    )


@workflow_api(name="ingest-propertyguru", version="v1")
@workflow.defn
class IngestPropertyGuruWorkflow:
    """Workflow that ingests PropertyGuru autocomplete data.

    Processes all Singapore streets in parallel.
    """

    @workflow.run
    async def run(self, input: IngestPropertyGuruInput) -> IngestPropertyGuruOutput:
        """Execute the PropertyGuru ingestion workflow.

        Args:
            input: Workflow input with configuration

        Returns:
            Ingestion results with success/failure counts
        """
        workflow.logger.info(f"Starting PropertyGuru ingestion from {input.streets_file}")

        # Load the list of streets
        streets = await load_streets_list.execute(input.streets_file)
        total_streets = len(streets)

        workflow.logger.info(f"Loaded {total_streets} streets to process")

        # Process streets in parallel with concurrency control
        successful = 0
        failed = 0
        failed_streets = []

        # Create a semaphore to limit concurrency
        semaphore = asyncio.Semaphore(input.max_concurrent)

        async def process_street(street_name: str) -> tuple[str, bool]:
            """Process a single street with semaphore control."""
            async with semaphore:
                try:
                    workflow.logger.info(f"Fetching data for: {street_name}")

                    # Fetch the data
                    data = await fetch_propertyguru_autocomplete.execute(street_name)

                    # Save the data
                    output_path = await save_propertyguru_data.execute(
                        street_name, data, input.output_dir
                    )

                    workflow.logger.info(f"✓ Saved {street_name} to {output_path}")
                    return street_name, True

                except Exception as e:
                    workflow.logger.error(f"✗ Failed to process {street_name}: {e}")
                    return street_name, False

        # Process all streets in parallel
        tasks = [process_street(street) for street in streets]
        results = await asyncio.gather(*tasks, return_exceptions=False)

        # Count successes and failures
        for street_name, success in results:
            if success:
                successful += 1
            else:
                failed += 1
                failed_streets.append(street_name)

        workflow.logger.info(
            f"Ingestion complete: {successful} successful, "
            f"{failed} failed out of {total_streets} total"
        )

        return IngestPropertyGuruOutput(
            total_streets=total_streets,
            successful=successful,
            failed=failed,
            failed_streets=failed_streets,
        )
