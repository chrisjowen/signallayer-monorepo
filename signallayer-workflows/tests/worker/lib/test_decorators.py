"""Tests for workflow_api decorator."""

import pytest
from pydantic import BaseModel
from temporalio import workflow

from src.worker.lib.decorators import _class_name_to_kebab, workflow_api


class DecoratorTestInput(BaseModel):
    value: int


class DecoratorTestOutput(BaseModel):
    result: int


@workflow.defn
class ExampleWorkflow:
    @workflow.run
    async def run(self, input: DecoratorTestInput) -> DecoratorTestOutput:
        return DecoratorTestOutput(result=input.value * 2)


@workflow.defn
class AnotherWorkflow:
    @workflow.run
    async def run(self, input: DecoratorTestInput) -> DecoratorTestOutput:
        return DecoratorTestOutput(result=input.value)


@workflow.defn
class VersionedWorkflow:
    @workflow.run
    async def run(self, input: DecoratorTestInput) -> DecoratorTestOutput:
        return DecoratorTestOutput(result=input.value)


def test_class_name_to_kebab():
    """Test converting class names to kebab-case."""
    assert _class_name_to_kebab("ExampleWorkflow") == "example-workflow"
    assert _class_name_to_kebab("MyAPIWorkflow") == "my-api-workflow"
    assert _class_name_to_kebab("SimpleClass") == "simple-class"
    assert _class_name_to_kebab("HTTPSConnection") == "https-connection"


def test_decorator_with_defaults(workflow_registry):
    """Test decorator with default settings."""
    # Apply decorator manually in test since registry is cleared
    decorated = workflow_api()(ExampleWorkflow)

    metadata = workflow_registry.get("example-workflow-v2")
    assert metadata is not None
    assert metadata.name == "example-workflow"
    assert metadata.version == "v2"
    assert metadata.input_model == DecoratorTestInput
    assert metadata.output_model == DecoratorTestOutput
    assert decorated is ExampleWorkflow


def test_decorator_with_custom_name(workflow_registry):
    """Test decorator with custom name."""
    workflow_api(name="custom-name")(AnotherWorkflow)

    metadata = workflow_registry.get("custom-name-v2")
    assert metadata is not None
    assert metadata.name == "custom-name"


def test_decorator_with_custom_version(workflow_registry):
    """Test decorator with custom version."""
    workflow_api(version="v3")(VersionedWorkflow)

    metadata = workflow_registry.get("versioned-workflow-v3")
    assert metadata is not None
    assert metadata.version == "v3"


def test_decorator_without_workflow_defn_raises():
    """Test that decorator without @workflow.defn raises error."""
    with pytest.raises(ValueError, match="must be decorated with @workflow.defn"):

        @workflow_api()
        class NotAWorkflow:
            pass


def test_decorator_returns_original_class():
    """Test that decorator returns the original class unchanged."""
    decorated = workflow_api()(ExampleWorkflow)

    # Should return the same class
    assert decorated is ExampleWorkflow
    assert hasattr(decorated, "run")
    assert hasattr(decorated, "__temporal_workflow_definition")
