"""Utilities for extracting type hints from workflow methods."""

import inspect
from typing import Any, get_type_hints

from pydantic import BaseModel


def extract_run_method_types(
    workflow_class: type[object],
) -> tuple[type[BaseModel], type[BaseModel]]:
    """Extract input and output Pydantic models from workflow run method.

    Args:
        workflow_class: The workflow class to inspect

    Returns:
        Tuple of (input_model, output_model)

    Raises:
        ValueError: If run method is missing, lacks type hints, or types aren't Pydantic models
    """
    # Check if run method exists
    if not hasattr(workflow_class, "run"):
        raise ValueError(f"Workflow class {workflow_class.__name__} must have a 'run' method")

    run_method = workflow_class.run

    # Get type hints
    try:
        hints = get_type_hints(run_method)
    except Exception as e:
        raise ValueError(
            f"Failed to extract type hints from {workflow_class.__name__}.run: {e}"
        ) from e

    # Extract input type (first parameter after self)
    sig = inspect.signature(run_method)
    params = list(sig.parameters.values())

    if len(params) < 2:  # self + input parameter
        raise ValueError(
            f"Workflow {workflow_class.__name__}.run must have at least one parameter "
            f"(besides 'self') with a type hint"
        )

    input_param = params[1]  # Skip 'self'
    if input_param.name not in hints:
        raise ValueError(
            f"Workflow {workflow_class.__name__}.run parameter '{input_param.name}' "
            f"must have a type hint"
        )

    input_type = hints[input_param.name]

    # Extract return type
    if "return" not in hints:
        raise ValueError(f"Workflow {workflow_class.__name__}.run must have a return type hint")

    output_type = hints["return"]

    # Validate that both are Pydantic models
    if not _is_pydantic_model(input_type):
        raise ValueError(
            f"Workflow {workflow_class.__name__}.run input type must be a Pydantic BaseModel, "
            f"got {input_type}"
        )

    if not _is_pydantic_model(output_type):
        raise ValueError(
            f"Workflow {workflow_class.__name__}.run output type must be a Pydantic BaseModel, "
            f"got {output_type}"
        )

    return input_type, output_type


def _is_pydantic_model(type_hint: Any) -> bool:
    """Check if a type hint is a Pydantic BaseModel.

    Args:
        type_hint: Type to check

    Returns:
        True if type is a Pydantic BaseModel class
    """
    try:
        return inspect.isclass(type_hint) and issubclass(type_hint, BaseModel)
    except TypeError:
        return False
