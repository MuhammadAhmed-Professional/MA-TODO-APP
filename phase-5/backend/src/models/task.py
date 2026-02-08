"""
Task Model (Phase V)

Extended task model for recurring tasks, due dates, and reminders.
Builds upon Phase II model with additional fields.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import field_validator
from sqlmodel import Field, Relationship, SQLModel


class TaskBase(SQLModel):
    """Base task fields shared across schemas"""

    title: str = Field(
        min_length=1,
        max_length=200,
        description="Task title (required)",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Optional task description",
    )

    @field_validator("title", mode="before")
    @classmethod
    def sanitize_title(cls, v: str) -> str:
        """Sanitize title: strip whitespace and prevent XSS."""
        if v is None:
            return v
        sanitized = v.strip()
        if not sanitized:
            raise ValueError("Title cannot be empty or only whitespace")
        sanitized = sanitized.replace("<", "").replace(">", "")
        return sanitized

    @field_validator("description", mode="before")
    @classmethod
    def sanitize_description(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize description: strip whitespace and prevent XSS."""
        if v is None or v == "":
            return None
        sanitized = v.strip()
        if not sanitized:
            return None
        sanitized = sanitized.replace("<", "").replace(">", "")
        return sanitized


class Task(TaskBase, table=True):
    """
    Task database model with advanced features.

    Includes due dates, reminders, recurrence, and categories.
    """

    __tablename__ = "tasks"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique task identifier (UUID v4 as string)",
    )
    is_complete: bool = Field(
        default=False,
        index=True,
        description="Task completion status",
    )
    due_date: Optional[datetime] = Field(
        default=None,
        index=True,
        description="Optional due date for the task (UTC)",
    )
    remind_at: Optional[datetime] = Field(
        default=None,
        index=True,
        description="Optional reminder timestamp (UTC)",
    )
    priority: str = Field(
        default="medium",
        index=True,
        description="Task priority (low, medium, high, urgent)",
    )
    category_id: Optional[str] = Field(
        default=None,
        foreign_key="task_categories.id",
        index=True,
        description="Optional category reference",
    )
    user_id: str = Field(
        foreign_key="user.id",
        index=True,
        description="Owner user ID (Better Auth string ID)",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Task creation timestamp (UTC)",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp (UTC)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "650e8400-e29b-41d4-a716-446655440001",
                "title": "Complete project documentation",
                "description": "Write comprehensive README",
                "is_complete": False,
                "due_date": "2026-02-15T23:59:59Z",
                "remind_at": "2026-02-14T09:00:00Z",
                "priority": "high",
                "category_id": "cat-750e8400-e29b-41d4-a716-446655440002",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "created_at": "2026-01-31T16:00:00Z",
                "updated_at": "2026-01-31T16:00:00Z",
            }
        }


class TaskCreate(TaskBase):
    """Schema for task creation request"""

    due_date: Optional[datetime] = Field(default=None)
    remind_at: Optional[datetime] = Field(default=None)
    priority: str = Field(default="medium", pattern="^(low|medium|high|urgent)$")
    category_id: Optional[str] = Field(default=None)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Complete project documentation",
                "description": "Write comprehensive README",
                "due_date": "2026-02-15T23:59:59Z",
                "remind_at": "2026-02-14T09:00:00Z",
                "priority": "high",
            }
        }


class TaskUpdate(SQLModel):
    """Schema for task update request (all fields optional)"""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    is_complete: Optional[bool] = None
    due_date: Optional[datetime] = None
    remind_at: Optional[datetime] = None
    priority: Optional[str] = Field(None, pattern="^(low|medium|high|urgent)$")
    category_id: Optional[str] = None

    @field_validator("title", mode="before")
    @classmethod
    def sanitize_title(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        sanitized = v.strip()
        if not sanitized:
            raise ValueError("Title cannot be empty")
        return sanitized.replace("<", "").replace(">", "")

    @field_validator("description", mode="before")
    @classmethod
    def sanitize_description(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return None
        sanitized = v.strip()
        if not sanitized:
            return None
        return sanitized.replace("<", "").replace(">", "")


class TaskResponse(TaskBase):
    """Schema for task data in API responses"""

    id: str
    is_complete: bool
    due_date: Optional[datetime]
    remind_at: Optional[datetime]
    priority: str
    category_id: Optional[str]
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "650e8400-e29b-41d4-a716-446655440001",
                "title": "Complete project documentation",
                "description": "Write comprehensive README",
                "is_complete": False,
                "due_date": "2026-02-15T23:59:59Z",
                "remind_at": "2026-02-14T09:00:00Z",
                "priority": "high",
                "category_id": "cat-750e8400-e29b-41d4-a716-446655440002",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "created_at": "2026-01-31T16:00:00Z",
                "updated_at": "2026-01-31T16:00:00Z",
            }
        }


class TaskListResponse(SQLModel):
    """Schema for paginated task list"""

    tasks: List[TaskResponse]
    total: int
    limit: int
    offset: int
