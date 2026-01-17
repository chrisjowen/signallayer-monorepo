"""Workflow for researching a specific issue."""

from agents import Runner
from pydantic import BaseModel, Field
from temporalio import workflow

from src.common.models import IssueReference
from src.worker.agents import planner, reporter, researcher
from src.worker.lib.decorators import workflow_api
from src.worker.workflows.activities.issues import (
    add_issue_labels,
    fetch_issue_details,
    post_github_comment,
    remove_issue_label,
)


class ResearchIssueInput(BaseModel):
    """Input for research issue workflow."""

    issue_ref: IssueReference = Field(..., description="Reference to the issue to research")


class ResearchIssueOutput(BaseModel):
    """Output from research issue workflow."""

    title: str = Field(..., description="Issue title")
    status: str = Field(..., description="Research status")
    findings: str = Field(..., description="Research findings markdown")


@workflow_api(name="research-issue", version="v1")
@workflow.defn
class ResearchIssueWorkflow:
    """Workflow that researches a specific issue to determine its validity and context."""

    @workflow.run
    async def run(self, input: ResearchIssueInput) -> ResearchIssueOutput:
        """Execute the research issue workflow.

        Args:
            input: Workflow input with issue reference

        Returns:
            Research result
        """
        repository = input.issue_ref.repository
        issue_number = input.issue_ref.number

        workflow.logger.info(f"Researching issue #{issue_number} in {repository}")

        try:
            # Phase 0: Initialization & Context Setup
            comment_id, raw_details = await self._initialize_phase(repository, issue_number)
            issue_context = self._build_issue_context(
                repository, issue_number, comment_id, raw_details
            )

            # Phase 1: Planning
            plan_text = await self._run_planning_phase(issue_context, comment_id)

            # Phase 2: Research Execution
            findings_text = await self._run_research_phase(issue_context, plan_text)

            # Phase 3: Reporting & Verdict
            final_output = await self._run_reporting_phase(issue_context, findings_text)

            # Finalization
            await self._mark_as_done(repository, issue_number)

            return ResearchIssueOutput(
                title=raw_details["title"],
                status="researched",
                findings=final_output,
            )

        except Exception as e:
            await self._handle_failure(repository, issue_number, e)
            raise e

    async def _initialize_phase(self, repository: str, issue_number: int) -> tuple[int, dict]:
        """Sets up the initial state and fetches issue details."""
        comment_id = await self._initialize_state(repository, issue_number)
        raw_details = await fetch_issue_details.execute(repository, issue_number)
        return comment_id, raw_details

    def _build_issue_context(
        self, repository: str, issue_number: int, comment_id: int, details: dict
    ) -> str:
        """Constructs the base context string for all agents."""
        return (
            f"Issue Title: {details['title']}\n"
            f"Issue Number: #{issue_number}\n"
            f"Repository: {repository}\n"
            f"Body: {details['body']}\n"
            f"Status Comment ID: {comment_id}\n"
        )

    async def _run_planning_phase(self, issue_context: str, comment_id: int) -> str:
        """Runs the Planner 📋 agent to create a research plan."""
        workflow.logger.info("Starting Planning Phase (Planner 📋)...")
        planner_context = (
            f"{issue_context}\n"
            f"Your task: Create a research plan and update the status comment (ID: {comment_id})."
        )
        result = await Runner.run(planner, planner_context)
        return result.final_output

    async def _run_research_phase(self, issue_context: str, plan_text: str) -> str:
        """Runs the Researcher 🕵️ agent to execute the research plan."""
        workflow.logger.info("Starting Research Execution Phase (Researcher 🕵️)...")
        research_context = (
            f"{issue_context}\n"
            f"Plan:\n{plan_text}\n\n"
            "Your task: Execute each item in the plan. Mark them as complete in the GitHub comment as you go."
        )
        result = await Runner.run(researcher, research_context, max_turns=150)
        return result.final_output

    async def _run_reporting_phase(self, issue_context: str, findings_text: str) -> str:
        """Runs the Reporter 🧠 agent to synthesize findings and report."""
        workflow.logger.info("Starting Reporting Phase (Reporter 🧠)...")
        reporter_context = (
            f"{issue_context}\n"
            f"Research Findings:\n{findings_text}\n\n"
            "Your task: Synthesize the findings and post a final verdict comment."
        )
        result = await Runner.run(reporter, reporter_context)
        return result.final_output

    async def _initialize_state(self, repository: str, issue_number: int) -> int:
        """Sets issue to in-progress, removes old label, adds new one, and posts WIP comment."""
        await remove_issue_label.execute(repository, issue_number, "research")
        await add_issue_labels.execute(repository, issue_number, ["research:inprogress"])

        wip_body = (
            "## 🚧 Research Started\n\n"
            "**Planner 📋** is creating a specialized research plan. Execution by **Researcher 🕵️** will follow shortly.\n\n"
            "**Status**: Initializing..."
        )
        comment_result = await post_github_comment.execute(repository, issue_number, wip_body)
        return comment_result.get("comment_id")

    async def _mark_as_done(self, repository: str, issue_number: int) -> None:
        """Replaces in-progress label with done label."""
        await remove_issue_label.execute(repository, issue_number, "research:inprogress")
        await add_issue_labels.execute(repository, issue_number, ["research:done"])

    async def _handle_failure(self, repository: str, issue_number: int, error: Exception) -> None:
        """Handles failure cleanup: reverts labels and posts error comment."""
        workflow.logger.error(f"Research workflow failed: {error}")
        try:
            await remove_issue_label.execute(repository, issue_number, "research:inprogress")
            await add_issue_labels.execute(repository, issue_number, ["research"])

            await post_github_comment.execute(
                repository, issue_number, f"❌ **Research Workflow Failed**\n\nError: {str(error)}"
            )
        except Exception as cleanup_error:
            workflow.logger.error(f"Failed to cleanup after error: {cleanup_error}")
