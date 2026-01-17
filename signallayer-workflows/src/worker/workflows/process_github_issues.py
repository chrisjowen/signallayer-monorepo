"""Workflow for processing GitHub issues."""

from pydantic import BaseModel, Field
from temporalio import workflow

from src.worker.workflows.activities.issues import fetch_issues_by_label
from src.worker.lib.decorators import workflow_api
from src.worker.workflows.research_issue import ResearchIssueInput, ResearchIssueWorkflow


class ProcessGithubIssuesInput(BaseModel):
    """Input for process GitHub issues workflow."""

    repository: str = Field(..., description="Repository to scan (e.g., 'owner/repo')")
    label: str = Field(default="check-demand", description="Label to filter issues by")


class ProcessGithubIssuesOutput(BaseModel):
    """Output from process GitHub issues workflow."""

    signals_found: int = Field(..., description="Number of issues discovered")
    signals_processed: int = Field(..., description="Number of issues successfully processed")


@workflow_api(name="process-github-issues", version="v1")
@workflow.defn
class ProcessGithubIssuesWorkflow:
    """Scheduled workflow that processes GitHub issues from collaboration platforms.

    Queries GitHub issues labeled with 'check-demand' and triggers ResearchIssueWorkflow
    for each discovered signal.
    """

    @workflow.run
    async def run(self, input: ProcessGithubIssuesInput) -> ProcessGithubIssuesOutput:
        """Execute the process GitHub issues workflow.

        Args:
            input: Workflow input with repository and label

        Returns:
            Summary of discovered and processed issues
        """
        workflow.logger.info(
            f"Searching for issues in {input.repository} with label '{input.label}'"
        )

        # Fetch issues with the demand signal label
        issues = await fetch_issues_by_label.execute(input.repository, input.label)

        workflow.logger.info(f"Found {len(issues)} issues")

        if not issues:
            workflow.logger.info("No issues found")
            return ProcessGithubIssuesOutput(signals_found=0, signals_processed=0)

        workflow.logger.info(f"Triggering research for {len(issues)} issues in parallel")

        # Create a list of child workflow tasks
        tasks = []
        for issue_ref in issues:
            # Safely get repository and number for the workflow ID, supporting both dict and object
            repo = getattr(issue_ref, "repository", None) or issue_ref.get("repository")  # type: ignore
            number = getattr(issue_ref, "number", None) or issue_ref.get("number")  # type: ignore

            # Use a dict for the child workflow input to avoid identity issues in sandbox.
            # ResearchIssueInput will validate the dict correctly.
            issue_ref_dict = (
                issue_ref.model_dump() if hasattr(issue_ref, "model_dump") else issue_ref
            )

            task = workflow.execute_child_workflow(
                ResearchIssueWorkflow.run,
                ResearchIssueInput(issue_ref=issue_ref_dict),  # type: ignore
                id=f"research-issue-{repo.replace('/', '-')}-{number}",
            )
            tasks.append(task)

        # Execute all child workflows in parallel and wait for results
        # We use asyncio.gather (supported by Temporal's async environment) to run them concurrently
        import asyncio

        results = await asyncio.gather(*tasks, return_exceptions=True)

        processed_count = 0
        for i, result in enumerate(results):
            issue_ref = issues[i]
            if isinstance(result, Exception):
                workflow.logger.error(f"Failed to process issue #{issue_ref.number}: {str(result)}")
            else:
                processed_count += 1

        workflow.logger.info(f"Completed: {processed_count}/{len(issues)} issues processed")

        return ProcessGithubIssuesOutput(
            signals_found=len(issues), signals_processed=processed_count
        )
