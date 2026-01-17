"""Tests for demand signal workflows."""

import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from src.common.models import IssueDetails, IssueReference
from src.worker.workflows.activities.demand_signals import fetch_demand_signals, fetch_issue_details
from src.worker.workflows.check_demand import CheckDemandInput, CheckDemandWorkflow
from src.worker.workflows.find_actions import FindActionsInput, FindActionsWorkflow


@pytest.fixture
def sample_issue_ref() -> IssueReference:
    """Create a sample issue reference."""
    return IssueReference(
        platform="github",
        number=123,
        repository="owner/repo",
        title="Test Demand Signal",
        url="https://github.com/owner/repo/issues/123",
    )


@pytest.fixture
def sample_issue_details(sample_issue_ref: IssueReference) -> IssueDetails:
    """Create sample issue details."""
    from datetime import datetime, timezone

    return IssueDetails(
        platform=sample_issue_ref.platform,
        number=sample_issue_ref.number,
        repository=sample_issue_ref.repository,
        title=sample_issue_ref.title,
        body="This is a test demand signal",
        labels=["check-demand", "priority-high"],
        state="open",
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
        author="testuser",
        url=sample_issue_ref.url,
    )


@pytest.mark.asyncio
async def test_check_demand_workflow(
    sample_issue_ref: IssueReference, sample_issue_details: IssueDetails
) -> None:
    """Test CheckDemandWorkflow execution."""
    async with await WorkflowEnvironment.start_time_skipping() as env:

        async def mock_fetch_issue_details(issue_ref: IssueReference) -> IssueDetails:
            return sample_issue_details

        # Create worker with workflow and mocked activity
        worker = Worker(
            env.client,
            task_queue="test-queue",
            workflows=[CheckDemandWorkflow],
            activities=[mock_fetch_issue_details],
        )

        async with worker:
            result = await env.client.execute_workflow(
                CheckDemandWorkflow.run,
                CheckDemandInput(issue_ref=sample_issue_ref),
                id="test-check-demand",
                task_queue="test-queue",
            )

            assert result.issue.number == sample_issue_ref.number
            assert result.issue.title == sample_issue_ref.title
            assert result.signal_type == "demand"


@pytest.mark.asyncio
async def test_find_actions_workflow_with_issues(
    sample_issue_ref: IssueReference, sample_issue_details: IssueDetails
) -> None:
    """Test FindActionsWorkflow when issues are found."""
    async with await WorkflowEnvironment.start_time_skipping() as env:

        async def mock_fetch_demand_signals(
            repository: str, label: str
        ) -> list[IssueReference]:
            return [sample_issue_ref]

        async def mock_fetch_issue_details(issue_ref: IssueReference) -> IssueDetails:
            return sample_issue_details

        # Create worker with workflows and mocked activities
        worker = Worker(
            env.client,
            task_queue="test-queue",
            workflows=[FindActionsWorkflow, CheckDemandWorkflow],
            activities=[mock_fetch_demand_signals, mock_fetch_issue_details],
        )

        async with worker:
            result = await env.client.execute_workflow(
                FindActionsWorkflow.run,
                FindActionsInput(repository="owner/repo", label="check-demand"),
                id="test-find-actions",
                task_queue="test-queue",
            )

            assert result.signals_found == 1
            assert result.signals_processed == 1


@pytest.mark.asyncio
async def test_find_actions_workflow_no_issues() -> None:
    """Test FindActionsWorkflow when no issues are found."""
    async with await WorkflowEnvironment.start_time_skipping() as env:

        async def mock_fetch_demand_signals(
            repository: str, label: str
        ) -> list[IssueReference]:
            return []

        # Create worker with workflow and mocked activity
        worker = Worker(
            env.client,
            task_queue="test-queue",
            workflows=[FindActionsWorkflow],
            activities=[mock_fetch_demand_signals],
        )

        async with worker:
            result = await env.client.execute_workflow(
                FindActionsWorkflow.run,
                FindActionsInput(repository="owner/repo", label="check-demand"),
                id="test-find-actions-empty",
                task_queue="test-queue",
            )

            assert result.signals_found == 0
            assert result.signals_processed == 0
