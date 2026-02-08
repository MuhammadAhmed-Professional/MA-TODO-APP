"""
Advanced Task Models

Extended task models for Phase V advanced features:
- RecurringTask: Task recurrence patterns
- TaskReminder: Scheduled reminders for tasks
- TaskPriority: Priority levels (enum)
- TaskCategory: User-defined task categories
- Extended Task model with priority, due_date, category
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import field_validator
from sqlmodel import Field, SQLModel


class TaskPriority(str, Enum):
    """Task priority levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class FrequencyType(str, Enum):
    """Recurring task frequency types"""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class NotificationType(str, Enum):
    """Notification delivery methods"""

    EMAIL = "email"
    PUSH = "push"
    IN_APP = "in_app"


class TaskCategory(SQLModel, table=True):
    """
    User-defined task category for organization.

    Categories allow users to organize tasks by projects, contexts, or themes.
    Each category has a color for visual distinction in the UI.
    """

    __tablename__ = "task_categories"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique category identifier (UUID v4 as string)",
    )
    user_id: str = Field(
        foreign_key="user.id",
        index=True,
        description="Owner user ID (Better Auth string ID)",
    )
    name: str = Field(
        min_length=1,
        max_length=50,
        description="Category name (e.g., 'Work', 'Personal', 'Shopping')",
    )
    color: str = Field(
        max_length=7,
        default="#3b82f6",  # Tailwind blue-500
        description="Hex color code for category badge (e.g., #3b82f6)",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Category creation timestamp (UTC)",
    )

    @field_validator("name", mode="before")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """Sanitize category name: strip whitespace and prevent XSS."""
        if v is None:
            return v
        sanitized = v.strip()
        if not sanitized:
            raise ValueError("Category name cannot be empty or only whitespace")
        # Basic XSS prevention
        sanitized = sanitized.replace("<", "").replace(">", "")
        return sanitized

    @field_validator("color", mode="before")
    @classmethod
    def validate_color(cls, v: str) -> str:
        """Validate hex color format."""
        if v is None:
            return "#3b82f6"  # Default blue
        # Remove whitespace
        v = v.strip()
        # Validate hex color format (#RRGGBB)
        if not v.startswith("#") or len(v) != 7:
            raise ValueError("Color must be in hex format (#RRGGBB)")
        return v.lower()

    class Config:
        json_schema_extra = {
            "example": {
                "id": "cat-650e8400-e29b-41d4-a716-446655440001",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Work",
                "color": "#ef4444",  # Tailwind red-500
                "created_at": "2025-12-07T16:00:00Z",
            }
        }


class RecurringTask(SQLModel, table=True):
    """
    Recurring task configuration.

    Stores recurrence patterns for tasks that repeat on a schedule.
    When a recurring task is marked complete, a new instance is automatically
    spawned based on the recurrence rules.
    """

    __tablename__ = "recurring_tasks"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique recurring task identifier",
    )
    task_id: str = Field(
        foreign_key="tasks.id",
        unique=True,
        index=True,
        description="Associated task ID (one-to-one relationship)",
    )
    frequency: FrequencyType = Field(
        description="Recurrence frequency (daily/weekly/monthly/custom)",
    )
    interval: int = Field(
        default=1,
        ge=1,
        description="Interval multiplier (e.g., every 2 weeks = weekly + interval=2)",
    )
    next_due_at: Optional[datetime] = Field(
        default=None,
        description="Next occurrence timestamp (UTC)",
    )
    cron_expression: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Cron expression for custom frequency (e.g., '0 9 * * 1' = Mondays at 9am)",
    )
    is_active: bool = Field(
        default=True,
        index=True,
        description="Whether recurrence is active (can be paused by user)",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Recurrence creation timestamp (UTC)",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp (UTC)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "rec-750e8400-e29b-41d4-a716-446655440002",
                "task_id": "650e8400-e29b-41d4-a716-446655440001",
                "frequency": "weekly",
                "interval": 1,
                "next_due_at": "2026-02-07T09:00:00Z",
                "cron_expression": None,
                "is_active": True,
                "created_at": "2025-12-07T16:00:00Z",
                "updated_at": "2025-12-07T16:00:00Z",
            }
        }


class TaskReminder(SQLModel, table=True):
    """
    Scheduled reminder for a task.

    Reminders trigger notifications at a specific time to alert users
    about upcoming or overdue tasks. Notifications are processed by the
    notification microservice.
    """

    __tablename__ = "task_reminders"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique reminder identifier",
    )
    task_id: str = Field(
        foreign_key="tasks.id",
        index=True,
        description="Associated task ID",
    )
    remind_at: datetime = Field(
        description="Reminder trigger timestamp (UTC)",
    )
    is_sent: bool = Field(
        default=False,
        index=True,
        description="Whether reminder notification has been sent",
    )
    notification_type: NotificationType = Field(
        default=NotificationType.IN_APP,
        description="Notification delivery method (email/push/in_app)",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Reminder creation timestamp (UTC)",
    )
    sent_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when reminder was sent (UTC)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "rem-850e8400-e29b-41d4-a716-446655440003",
                "task_id": "650e8400-e29b-41d4-a716-446655440001",
                "remind_at": "2026-02-01T09:00:00Z",
                "is_sent": False,
                "notification_type": "in_app",
                "created_at": "2025-12-07T16:00:00Z",
                "sent_at": None,
            }
        }


# Request/Response Schemas for API


class TaskCategoryCreate(SQLModel):
    """Schema for creating a task category"""

    name: str = Field(min_length=1, max_length=50)
    color: str = Field(max_length=7, default="#3b82f6")

    @field_validator("name", mode="before")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        if v is None:
            return v
        sanitized = v.strip()
        if not sanitized:
            raise ValueError("Category name cannot be empty")
        return sanitized.replace("<", "").replace(">", "")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Work",
                "color": "#ef4444",
            }
        }


class TaskCategoryResponse(SQLModel):
    """Schema for task category in API responses"""

    id: str
    user_id: str
    name: str
    color: str
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "cat-650e8400-e29b-41d4-a716-446655440001",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Work",
                "color": "#ef4444",
                "created_at": "2025-12-07T16:00:00Z",
            }
        }


class RecurringTaskCreate(SQLModel):
    """Schema for setting up recurring task"""

    frequency: FrequencyType
    interval: int = Field(default=1, ge=1)
    cron_expression: Optional[str] = Field(None, max_length=100)

    class Config:
        json_schema_extra = {
            "example": {
                "frequency": "weekly",
                "interval": 1,
                "cron_expression": None,
            }
        }


class RecurringTaskResponse(SQLModel):
    """Schema for recurring task in API responses"""

    id: str
    task_id: str
    frequency: FrequencyType
    interval: int
    next_due_at: Optional[datetime]
    cron_expression: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskReminderCreate(SQLModel):
    """Schema for creating a task reminder"""

    remind_at: datetime
    notification_type: NotificationType = NotificationType.IN_APP

    class Config:
        json_schema_extra = {
            "example": {
                "remind_at": "2026-02-01T09:00:00Z",
                "notification_type": "in_app",
            }
        }


class TaskReminderResponse(SQLModel):
    """Schema for task reminder in API responses"""

    id: str
    task_id: str
    remind_at: datetime
    is_sent: bool
    notification_type: NotificationType
    created_at: datetime
    sent_at: Optional[datetime]

    class Config:
        from_attributes = True
