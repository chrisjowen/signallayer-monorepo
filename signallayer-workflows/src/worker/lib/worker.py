"""Temporal worker class."""

import asyncio
import signal
from datetime import timedelta
from typing import Any

import inject
import structlog
from temporalio.contrib.openai_agents import ModelActivityParameters, OpenAIAgentsPlugin
from temporalio.worker import Worker

from ..config import WorkerSettings

logger = structlog.get_logger()


class TemporalWorker:
    """A wrapper for the Temporal worker logic."""

    @inject.params(config=WorkerSettings)
    def __init__(
        self,
        workflows: list[type],
        activities: list[Any] | None = None,
        queue: str | None = None,
        config: WorkerSettings | None = None,
    ) -> None:
        """Initialize the Temporal worker.

        Args:
            workflows: List of workflow classes.
            activities: List of activity functions.
            queue: Task queue name. Defaults to config if not provided.
            config: Worker configuration settings (injected).
        """
        self.config = config or WorkerSettings()
        self.queue = queue or self.config.task_queue
        self.activities = activities
        self.workflows = workflows
        self._shutdown_event = asyncio.Event()

    async def run(self) -> None:
        """Connect to Temporal and run the worker."""
        logger.info(
            "starting_worker",
            temporal_url=self.config.temporal_url,
            namespace=self.config.temporal_namespace,
            task_queue=self.queue,
            local=self.config.temporal_local,
        )

        # Connect to Temporal
        try:
            from ...common.temporal_client import connect_temporal

            client = await connect_temporal(self.config)
        except Exception:
            # Error is already logged in connect_temporal
            raise

        logger.info("temporal_client_connected")

        workflows = self.workflows
        if not workflows:
            raise ValueError("No workflows provided to worker")

        activities = self.activities
        if not activities:
            # Note: activities are technically optional for a worker that only runs workflows,
            # but in this project we usually expect them.
            activities = []

        # Configure workflow sandbox to allow httpx (used in activities, not workflows)
        from temporalio.worker.workflow_sandbox import SandboxedWorkflowRunner, SandboxRestrictions

        workflow_runner = SandboxedWorkflowRunner(
            restrictions=SandboxRestrictions.default.with_passthrough_modules(
                "httpx",
                "httpx._client",
                "httpx._models",
                "httpx._auth",
                "urllib3",
                "requests",
                "praw",
                "prawcore",
                "http",
                "http.client",
                "sniffio",
                "sniffio._impl",
                "threading",
                "anyio",
                "anyio._core",
                "anyio._core._eventloop",
                "agents",
                "openai",
                "pydantic",
                "pydantic_core",
                "src.common",
                "src.common.models",
                "src.worker.agents",
                "src.worker.agents.planner",
                "src.worker.agents.researcher",
                "src.worker.agents.reporter",
                "src.worker.agents.orchestrator",
                "src.worker.workflows.activities.research",
                "src.worker.workflows.activities.issues",
                "temporalio.contrib.openai_agents",
                "temporalio.contrib.openai_agents.workflow",
                "temporalio.contrib.openai_agents._invoke_model_activity",
            )
        )

        # Create worker
        worker_kwargs = {
            "client": client,
            "task_queue": self.queue,
            "workflows": workflows,
            "activities": activities,
            "workflow_runner": workflow_runner,
            "max_concurrent_workflow_tasks": self.config.max_concurrent_workflows,
            "max_concurrent_activities": self.config.max_concurrent_activities,
            "plugins": [
                OpenAIAgentsPlugin(
                    model_params=ModelActivityParameters(
                        start_to_close_timeout=timedelta(seconds=30)
                    )
                )
            ],
        }

        worker = Worker(**worker_kwargs)

        # Setup graceful shutdown
        def signal_handler(sig: int, frame: Any) -> None:
            """Handle shutdown signals."""
            logger.info("shutdown_signal_received", signal=sig)
            self._shutdown_event.set()

        # Handle signals if we're in the main thread (otherwise ignore)
        try:
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
        except ValueError:
            # signal only works in main thread
            pass

        logger.info("worker_starting")

        try:
            # Use AsyncExitStack to handle optional plugin context
            # The AsyncExitStack is not strictly necessary here
            # as the Worker itself is an async context manager.
            async with worker:
                logger.info("worker_running")
                await self._shutdown_event.wait()
        except Exception as e:
            logger.error("worker_error", error=str(e))
            raise
        finally:
            logger.info("worker_stopping")
            logger.info("worker_stopped")
