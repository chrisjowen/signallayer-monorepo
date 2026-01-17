"""Pytest fixtures for worker tests."""

import pytest
import inject
from src.worker.lib.registry import WorkflowRegistry
from src.common.injection import configure_inject

# Ensure inject is configured for all tests
configure_inject()

@pytest.fixture
def workflow_registry() -> WorkflowRegistry:
    """Fixture to get WorkflowRegistry."""
    from src.worker.lib.registry import WorkflowRegistry
    return inject.instance(WorkflowRegistry)

@pytest.fixture
def activity_registry():
    """Fixture to get ActivityRegistry."""
    from src.worker.lib.registry import ActivityRegistry
    return inject.instance(ActivityRegistry)

@pytest.fixture(autouse=True)
def clear_registries(workflow_registry, activity_registry):
    """Clear registries before each test."""
    workflow_registry.clear()
    activity_registry.clear()
    yield
    workflow_registry.clear()
    activity_registry.clear()
