import asyncio

import inject

from ..common.env import setup_environment
from ..common.injection import configure_inject
from .lib.registry import ActivityRegistry, WorkflowRegistry

# Setup environment variables first
setup_environment()

# Configure injection before any other imports that might use it
configure_inject()

from .config import settings
from .lib.worker import TemporalWorker


@inject.params(
    workflow_registry=WorkflowRegistry,
    activity_registry=ActivityRegistry,
)
async def main(
    workflow_registry: WorkflowRegistry,
    activity_registry: ActivityRegistry,
) -> None:
    """Run the Temporal workflow worker."""

    # Import workflows and activities to ensure they are registered
    from . import workflows  # noqa: F401
    from .workflows import activities  # noqa: F401

    # Discover registered components
    queue = settings.task_queue
    workflows_list = [m.workflow_class for m in workflow_registry.get_all(task_queue=queue)]
    activities_list = [m.activity_function for m in activity_registry.get_all(task_queue=queue)]

    # Create and run worker with discovered components
    worker = TemporalWorker(
        workflows=workflows_list,
        activities=activities_list,
        queue=queue,
        config=settings,
    )

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
