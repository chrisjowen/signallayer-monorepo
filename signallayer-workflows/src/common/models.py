"""Pydantic models for collaboration platform data."""

from datetime import datetime

from pydantic import BaseModel, Field


class IssueReference(BaseModel):
    """Lightweight reference to an issue from a collaboration platform."""

    platform: str = Field(..., description="Platform name (e.g., 'github', 'linear')")
    number: int = Field(..., description="Issue number")
    repository: str = Field(..., description="Repository or project identifier")
    title: str = Field(..., description="Issue title")
    url: str = Field(..., description="URL to the issue")


class IssueDetails(BaseModel):
    """Complete details of an issue from a collaboration platform."""

    platform: str = Field(..., description="Platform name (e.g., 'github', 'linear')")
    number: int = Field(..., description="Issue number")
    repository: str = Field(..., description="Repository or project identifier")
    title: str = Field(..., description="Issue title")
    body: str = Field(..., description="Issue description/body")
    labels: list[str] = Field(default_factory=list, description="Issue labels")
    state: str = Field(..., description="Issue state (e.g., 'open', 'closed')")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    author: str = Field(..., description="Issue author username")
    url: str = Field(..., description="URL to the issue")
