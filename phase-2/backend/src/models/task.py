"""
Task Model

Represents a todo task owned by a user.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import field_validator
from sqlmodel import Field, Relationship, SQLModel

from src.models.priority import Priority
from src.models.task_tag import TaskTag


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
        # Strip leading/trailing whitespace
        sanitized = v.strip()
        if not sanitized:
            raise ValueError("Title cannot be empty or only whitespace")
        # Basic XSS prevention: remove < and > characters
        sanitized = sanitized.replace("<", "").replace(">", "")
        return sanitized

    @field_validator("description", mode="before")
    @classmethod
    def sanitize_description(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize description: strip whitespace and prevent XSS."""
        if v is None or v == "":
            return None
        # Strip leading/trailing whitespace
        sanitized = v.strip()
        if not sanitized:
            return None
        # Basic XSS prevention: remove < and > characters
        sanitized = sanitized.replace("<", "").replace(">", "")
        return sanitized


class Task(TaskBase, table=True):
    """
    Task database model.

    Stores user's todo tasks with ownership and completion tracking.
    """

    __tablename__ = "tasks"

    # Better Auth uses string IDs (not UUIDs)
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique task identifier (UUID v4 as string)",
    )
    is_complete: bool = Field(
        default=False,
        index=True,  # Index for filtering by completion status
        description="Task completion status",
    )
    priority: int = Field(
        default=Priority.MEDIUM,
        index=True,  # Index for filtering/sorting by priority
        description="Task priority (1=low, 2=medium, 3=high)",
    )
    due_date: Optional[datetime] = Field(
        default=None,
        index=True,  # Index for filtering by due date
        description="Optional due date for the task",
    )
    # Better Auth uses string IDs (not UUIDs)
    user_id: str = Field(
        foreign_key="user.id",
        index=True,  # Index for fast user task queries
        description="Owner user ID (foreign key to user table - Better Auth string ID)",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Task creation timestamp (UTC)",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp (UTC)",
    )

    # Many-to-many relationship with tags
    tags: List["Tag"] = Relationship(
        back_populates="tasks",
        link_model=TaskTag,
    )

    class Config:
        """SQLModel configuration"""

        json_schema_extra = {
            "example": {
                "id": "650e8400-e29b-41d4-a716-446655440001",
                "title": "Complete project documentation",
                "description": "Write comprehensive README and API docs",
                "is_complete": False,
                "priority": 2,
                "due_date": "2025-12-31T23:59:59Z",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "created_at": "2025-12-07T16:00:00Z",
                "updated_at": "2025-12-07T16:00:00Z",
            }
        }


class TaskCreate(TaskBase):
    """Schema for task creation request"""

    priority: int = Field(
        default=Priority.MEDIUM,
        ge=Priority.LOW,
        le=Priority.HIGH,
        description="Task priority (default: medium)",
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="Optional due date for the task",
    )
    tag_ids: Optional[List[str]] = Field(
        default=[],
        description="Optional list of tag IDs to associate with the task",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Complete project documentation",
                "description": "Write comprehensive README and API docs",
                "priority": 2,
                "due_date": "2025-12-31T23:59:59Z",
                "tag_ids": ["750e8400-e29b-41d4-a716-446655440002"],
            }
        }


class TaskUpdate(SQLModel):
    """Schema for task update request (all fields optional)"""

    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Updated task title",
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Updated task description",
    )
    is_complete: Optional[bool] = Field(
        None,
        description="Updated completion status",
    )
    priority: Optional[int] = Field(
        None,
        ge=Priority.LOW,
        le=Priority.HIGH,
        description="Updated task priority",
    )
    due_date: Optional[datetime] = Field(
        None,
        description="Updated due date (set to null to clear)",
    )

    @field_validator("title", mode="before")
    @classmethod
    def sanitize_title(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize title: strip whitespace and prevent XSS."""
        if v is None:
            return v
        # Strip leading/trailing whitespace
        sanitized = v.strip()
        if not sanitized:
            raise ValueError("Title cannot be empty or only whitespace")
        # Basic XSS prevention: remove < and > characters
        sanitized = sanitized.replace("<", "").replace(">", "")
        return sanitized

    @field_validator("description", mode="before")
    @classmethod
    def sanitize_description(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize description: strip whitespace and prevent XSS."""
        if v is None or v == "":
            return None
        # Strip leading/trailing whitespace
        sanitized = v.strip()
        if not sanitized:
            return None
        # Basic XSS prevention: remove < and > characters
        sanitized = sanitized.replace("<", "").replace(">", "")
        return sanitized

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Complete project documentation (updated)",
                "description": "Write README, API docs, and deployment guide",
                "is_complete": True,
                "priority": 3,
                "due_date": "2025-12-31T23:59:59Z",
            }
        }


class TaskToggleComplete(SQLModel):
    """Schema for toggling task completion status"""

    is_complete: bool = Field(description="New completion status")

    class Config:
        json_schema_extra = {
            "example": {
                "is_complete": True,
            }
        }


class TaskResponse(TaskBase):
    """
    Schema for task data in API responses.

    Includes all task fields for client display.
    """

    id: str  # UUID v4 as string (matches Better Auth)
    is_complete: bool
    priority: int
    due_date: Optional[datetime]
    user_id: str  # UUID v4 as string (matches Better Auth)
    created_at: datetime
    updated_at: datetime
    tags: List["TagResponse"] = []  # Associated tags

    class Config:
        from_attributes = True  # Allow ORM model conversion
        json_schema_extra = {
            "example": {
                "id": "650e8400-e29b-41d4-a716-446655440001",
                "title": "Complete project documentation",
                "description": "Write comprehensive README and API docs",
                "is_complete": False,
                "priority": 2,
                "due_date": "2025-12-31T23:59:59Z",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "created_at": "2025-12-07T16:00:00Z",
                "updated_at": "2025-12-07T16:00:00Z",
                "tags": [
                    {
                        "id": "750e8400-e29b-41d4-a716-446655440002",
                        "name": "work",
                        "color": "#3b82f6",
                    }
                ],
            }
        }


# Forward reference for Tag model (circular import)
from src.models.tag import Tag, TagResponse  # noqa: E402

Task.model_rebuild()
