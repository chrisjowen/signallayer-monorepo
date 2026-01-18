from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from pydantic import BaseModel
from temporalio.common import RetryPolicy


@dataclass(frozen=True)
class WorkflowMetadata:
    """Metadata for a registered workflow."""

    workflow_class: type[object]
    name: str
    input_model: type[BaseModel]
    output_model: type[BaseModel]
    version: str
    task_queue: str | None = None


@dataclass(frozen=True)
class ActivityMetadata:
    """Metadata for a registered activity."""

    activity_function: Callable[..., Any]
    name: str
    task_queue: str | None = None
    schedule_to_close_timeout: timedelta | None = None
    start_to_close_timeout: timedelta | None = None
    retry_policy: RetryPolicy | None = None
