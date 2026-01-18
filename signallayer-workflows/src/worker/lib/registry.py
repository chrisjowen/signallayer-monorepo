"""Registry for storing and retrieving workflow and activity metadata."""

from threading import Lock
from typing import Generic, TypeVar

from .models import ActivityMetadata, WorkflowMetadata

T = TypeVar("T", WorkflowMetadata, ActivityMetadata)

class GenericRegistry(Generic[T]):
    """Generic thread-safe registry."""

    def __init__(self) -> None:
        self._items: dict[str, T] = {}
        self._lock: Lock = Lock()

    def register(self, key: str, metadata: T) -> None:
        """Register an item with its metadata."""
        with self._lock:
            if key in self._items:
                existing = self._items[key]
                # Allow re-registration if it's the same class/function name (likely sandbox reload)
                if self._get_item_name(existing) == self._get_item_name(metadata):
                    return
                raise ValueError(f"Item '{key}' is already registered")
            self._items[key] = metadata

    def get(self, key: str) -> T | None:
        """Get metadata by key."""
        return self._items.get(key)

    def get_all(self, task_queue: str | None = None) -> list[T]:
        """Get all registered items, optionally filtered by task queue."""
        items = list(self._items.values())
        if task_queue:
            # Include items that match the queue OR have no queue specified (default)
            return [i for i in items if i.task_queue == task_queue or i.task_queue is None]
        return items

    def clear(self) -> None:
        """Clear all registered items."""
        with self._lock:
            self._items.clear()

    def _get_item_name(self, item: T) -> str:
        if isinstance(item, WorkflowMetadata):
            return item.workflow_class.__name__
        elif isinstance(item, ActivityMetadata):
            return item.activity_function.__name__
        return ""


class WorkflowRegistry(GenericRegistry[WorkflowMetadata]):
    """Registry for workflows."""

    def register_workflow(self, metadata: WorkflowMetadata) -> None:
        full_name = f"{metadata.name}-{metadata.version}"
        self.register(full_name, metadata)


class ActivityRegistry(GenericRegistry[ActivityMetadata]):
    """Registry for activities."""

    def register_activity(self, metadata: ActivityMetadata) -> None:
        self.register(metadata.name, metadata)
