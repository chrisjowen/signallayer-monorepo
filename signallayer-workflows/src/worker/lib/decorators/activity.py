from collections.abc import Awaitable, Callable
from datetime import timedelta
from typing import (
    Any,
    Generic,
    ParamSpec,
    Protocol,
    TypeVar,
    cast,
    runtime_checkable,
)

from temporalio import activity, workflow
from temporalio.common import RetryPolicy

from ..models import ActivityMetadata

P = ParamSpec("P")
T = TypeVar("T")

# Default retry behavior: don't retry NoRetryException
DEFAULT_RETRY_POLICY = RetryPolicy(
    non_retryable_error_types=["NoRetryException"]
)

@runtime_checkable
class ExecutableActivity(Protocol, Generic[P, T]):
    """Protocol for activities with the .execute magic method."""
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Awaitable[T]: ...
    async def execute(self, *args: P.args, **kwargs: P.kwargs) -> T: ...


def configured_activity(
    name: str | None = None,
    task_queue: str | None = None,
    schedule_to_close_timeout: timedelta | None = None,
    start_to_close_timeout: timedelta | None = None,
    retry_policy: RetryPolicy | None = None,
    max_retries: int | None = None,
) -> Callable[[Callable[P, Awaitable[T]]], ExecutableActivity[P, T]]:
    """Decorator to register a Temporal activity with default options.
    
    Automatically applies @activity.defn and attaches a .execute() helper.
    """

    if retry_policy is not None and max_retries is not None:
        raise ValueError("Cannot specify both retry_policy and max_retries")

    # Use default retry policy or create one from max_retries
    if retry_policy:
        final_retry_policy = retry_policy
    elif max_retries is not None:
        final_retry_policy = RetryPolicy(
            maximum_attempts=max_retries,
            non_retryable_error_types=DEFAULT_RETRY_POLICY.non_retryable_error_types
        )
    else:
        final_retry_policy = DEFAULT_RETRY_POLICY

    def decorator(func: Callable[P, Awaitable[T]]) -> ExecutableActivity[P, T]:
        # Apply Temporal's activity decorator
        if name:
            temporal_decorated = activity.defn(name=name)(func)
        else:
            temporal_decorated = activity.defn(func)

        # Determine activity name for our registry
        activity_name = name or func.__name__

        # Create metadata
        metadata = ActivityMetadata(
            activity_function=temporal_decorated,
            name=activity_name,
            task_queue=task_queue,
            schedule_to_close_timeout=schedule_to_close_timeout,
            start_to_close_timeout=start_to_close_timeout,
            retry_policy=final_retry_policy,
        )

        # Register in global registry if injection is configured
        import inject
        if inject.is_configured():
            from ..registry import ActivityRegistry
            try:
                act_registry = inject.instance(ActivityRegistry)
                act_registry.register_activity(metadata)
            except inject.InjectorException:
                # Injection configured but registry not bound (unlikely)
                pass

        # Attach the .execute magic method
        async def execute(*args: P.args, **exec_kwargs: Any) -> T:
            """Execute this activity with Temporal defaults."""
            # Use defaults from metadata
            opts = {
                "task_queue": exec_kwargs.pop("task_queue", metadata.task_queue),
                "schedule_to_close_timeout": exec_kwargs.pop(
                    "schedule_to_close_timeout", metadata.schedule_to_close_timeout
                ),
                "start_to_close_timeout": exec_kwargs.pop(
                    "start_to_close_timeout", metadata.start_to_close_timeout
                ),
                "retry_policy": exec_kwargs.pop("retry_policy", metadata.retry_policy),
            }

            # Prepare arguments for execute_activity
            # We use 'args' keyword argument which handles multiple arguments correctly
            return await cast(
                T,
                workflow.execute_activity(
                    temporal_decorated, args=args, **opts, **exec_kwargs
                ),
            )

        # Attach the method
        temporal_decorated.execute = execute

        # Explicitly cast for IDE support
        return cast(ExecutableActivity[P, T], temporal_decorated)

    return decorator
