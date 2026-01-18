import re
from collections.abc import Callable
from typing import TypeVar

from ..models import WorkflowMetadata
from ..type_utils import extract_run_method_types

T = TypeVar("T")


def workflow_api(
    name: str | None = None,
    version: str = "v2",
    task_queue: str | None = None
) -> Callable[[type[T]], type[T]]:
    """Decorator to register a Temporal workflow for API exposure.

    Args:
        name: API endpoint name (defaults to kebab-case class name)
        version: API version (default: "v2")
        task_queue: Default task queue for this workflow
    """

    def decorator(workflow_class: type[T]) -> type[T]:
        # Validate that this is a Temporal workflow
        if not hasattr(workflow_class, "__temporal_workflow_definition"):
            raise ValueError(
                f"Class {workflow_class.__name__} must be decorated with @workflow.defn "
                f"before @workflow_api"
            )

        # Determine workflow name
        workflow_name = name or _class_name_to_kebab(workflow_class.__name__)

        # Extract input/output types from run method
        try:
            input_model, output_model = extract_run_method_types(workflow_class)
        except ValueError as e:
            raise ValueError(f"Failed to register workflow {workflow_class.__name__}: {e}") from e

        # Create metadata
        metadata = WorkflowMetadata(
            workflow_class=workflow_class,
            name=workflow_name,
            input_model=input_model,
            output_model=output_model,
            version=version,
            task_queue=task_queue,
        )

        # Register in global registry if injection is configured
        import inject
        if inject.is_configured():
            from ..registry import WorkflowRegistry
            try:
                workflow_registry = inject.instance(WorkflowRegistry)
                workflow_registry.register_workflow(metadata)
            except inject.InjectorException:
                pass

        # Return original class unchanged
        return workflow_class

    return decorator


def _class_name_to_kebab(class_name: str) -> str:
    """Convert PascalCase class name to kebab-case."""
    # Insert hyphens before uppercase letters (except at start)
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1-\2", class_name)
    # Insert hyphens before uppercase letters preceded by lowercase
    s2 = re.sub("([a-z0-9])([A-Z])", r"\1-\2", s1)
    # Convert to lowercase
    return s2.lower()
