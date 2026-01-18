"""Tests for activity decorators and utilities."""

import pytest
from datetime import timedelta
from unittest.mock import patch, AsyncMock
import inject

from temporalio import activity, workflow
from temporalio.common import RetryPolicy

from src.worker.lib.decorators import configured_activity
from src.worker.lib.registry import ActivityRegistry


def test_configured_activity_registration(activity_registry):
    """Test that @configured_activity registers with correct metadata."""
    
    @configured_activity(
        name="custom_name",
        task_queue="special_queue",
        start_to_close_timeout=timedelta(seconds=5)
    )
    async def my_activity(x: int) -> int:
        return x + 1

    metadata = activity_registry.get("custom_name")
    assert metadata is not None
    assert metadata.name == "custom_name"
    assert metadata.task_queue == "special_queue"
    assert metadata.start_to_close_timeout == timedelta(seconds=5)
    # Check if Temporal's decorator was applied
    assert hasattr(my_activity, "__temporal_activity_definition")


def test_configured_activity_no_name(activity_registry):
    """Test @configured_activity with default name from function."""
    
    @configured_activity(start_to_close_timeout=timedelta(seconds=10))
    async def unnamed_activity():
        pass

    metadata = activity_registry.get("unnamed_activity")
    assert metadata is not None
    assert metadata.name == "unnamed_activity"


@pytest.mark.asyncio
async def test_activity_execute_magic():
    """Test the .execute() magic method on activities."""
    
    @configured_activity(
        task_queue="magic_queue",
        start_to_close_timeout=timedelta(minutes=5)
    )
    async def magic_activity(val: int) -> int:
        return val * 10

    with patch("temporalio.workflow.execute_activity", new_callable=AsyncMock) as mock_exec:
        # Call the magic .execute method directly on the function
        await magic_activity.execute(42)
        
        mock_exec.assert_called_once()
        args, kwargs = mock_exec.call_args
        # First positional arg is the activity
        assert args[0].__name__ == "magic_activity"
        # Second is the value
        assert args[1] == 42
        assert kwargs["task_queue"] == "magic_queue"
        assert kwargs["start_to_close_timeout"] == timedelta(minutes=5)


@pytest.mark.asyncio
async def test_activity_injection():
    """Test that dependency injection works inside activities."""
    from src.common.dummy_service import DummyService
    
    @configured_activity()
    @inject.params(service=DummyService)
    async def injection_activity(name: str, service: DummyService) -> str:
        return service.get_greeting(name)

    # We test it by calling it directly (since @inject.params supports direct calling if inject is configured)
    result = await injection_activity("Test")
    assert "Hello from DummyService, Test!" in result


def test_activity_default_non_retryable_exceptions(activity_registry):
    """Test that NoRetryException is non-retryable by default."""
    from src.common.exceptions import NoRetryException
    
    @configured_activity()
    async def restricted_activity():
        pass
        
    metadata = activity_registry.get("restricted_activity")
    assert metadata is not None
    assert metadata.retry_policy is not None
    assert "NoRetryException" in metadata.retry_policy.non_retryable_error_types


def test_activity_retry_exclusive_error():
    """Test that specifying both retry_policy and max_retries raises error."""
    with pytest.raises(ValueError, match="Cannot specify both retry_policy and max_retries"):
        @configured_activity(
            retry_policy=RetryPolicy(maximum_attempts=5),
            max_retries=3
        )
        async def invalid_activity():
            pass


def test_activity_max_retries_merging(activity_registry):
    """Test that max_retries merges with default non-retryable errors."""
    @configured_activity(max_retries=7)
    async def retried_activity():
        pass
        
    metadata = activity_registry.get("retried_activity")
    assert metadata is not None
    assert metadata.retry_policy is not None
    assert metadata.retry_policy.maximum_attempts == 7
    assert "NoRetryException" in metadata.retry_policy.non_retryable_error_types


def test_activity_explicit_retry_policy(activity_registry):
    """Test that explicit retry_policy is used."""
    policy = RetryPolicy(maximum_attempts=10, initial_interval=timedelta(seconds=1))
    @configured_activity(retry_policy=policy)
    async def explicit_policy_activity():
        pass
        
    metadata = activity_registry.get("explicit_policy_activity")
    assert metadata is not None
    assert metadata.retry_policy is policy
    assert metadata.retry_policy.maximum_attempts == 10
