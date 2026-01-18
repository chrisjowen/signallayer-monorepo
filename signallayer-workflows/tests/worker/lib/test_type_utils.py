"""Tests for type hint extraction utilities."""

import pytest
from pydantic import BaseModel
from temporalio import workflow

from src.worker.lib.type_utils import extract_run_method_types


class ValidInput(BaseModel):
    name: str


class ValidOutput(BaseModel):
    result: str


@workflow.defn
class ValidWorkflow:
    @workflow.run
    async def run(self, input: ValidInput) -> ValidOutput:
        return ValidOutput(result=f"Hello {input.name}")


class NoRunMethodWorkflow:
    """Workflow without @workflow.defn or run method for testing."""

    pass


@workflow.defn
class NoTypeHintsWorkflow:
    @workflow.run
    async def run(self, input):  # type: ignore
        return {"result": "test"}


@workflow.defn
class NoReturnTypeWorkflow:
    @workflow.run
    async def run(self, input: ValidInput):  # type: ignore
        return ValidOutput(result="test")


@workflow.defn
class NonPydanticInputWorkflow:
    @workflow.run
    async def run(self, input: dict) -> ValidOutput:  # type: ignore
        return ValidOutput(result="test")


@workflow.defn
class NonPydanticOutputWorkflow:
    @workflow.run
    async def run(self, input: ValidInput) -> str:  # type: ignore
        return "test"


def test_extract_valid_types():
    """Test extracting types from valid workflow."""
    input_type, output_type = extract_run_method_types(ValidWorkflow)

    assert input_type == ValidInput
    assert output_type == ValidOutput


def test_extract_no_run_method_raises():
    """Test that workflow without run method raises error."""
    with pytest.raises(ValueError, match="must have a 'run' method"):
        extract_run_method_types(NoRunMethodWorkflow)


def test_extract_no_type_hints_raises():
    """Test that workflow without type hints raises error."""
    with pytest.raises(ValueError, match="must have a type hint"):
        extract_run_method_types(NoTypeHintsWorkflow)


def test_extract_no_return_type_raises():
    """Test that workflow without return type raises error."""
    with pytest.raises(ValueError, match="must have a return type hint"):
        extract_run_method_types(NoReturnTypeWorkflow)


def test_extract_non_pydantic_input_raises():
    """Test that non-Pydantic input type raises error."""
    with pytest.raises(ValueError, match="input type must be a Pydantic BaseModel"):
        extract_run_method_types(NonPydanticInputWorkflow)


def test_extract_non_pydantic_output_raises():
    """Test that non-Pydantic output type raises error."""
    with pytest.raises(ValueError, match="output type must be a Pydantic BaseModel"):
        extract_run_method_types(NonPydanticOutputWorkflow)
