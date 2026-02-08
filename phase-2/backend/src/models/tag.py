"""
Tag Model

Represents user-defined tags/categories for organizing tasks.
"""

import uuid
from typing import List, Optional

from pydantic import field_validator
from sqlmodel import Field, Relationship, SQLModel

from src.models.task_tag import TaskTag


# Predefined color palette for tags
TAG_COLORS = [
    "#ef4444",  # red
    "#f97316",  # orange
    "#f59e0b",  # amber
    "#eab308",  # yellow
    "#84cc16",  # lime
    "#22c55e",  # green
    "#10b981",  # emerald
    "#14b8a6",  # teal
    "#06b6d4",  # cyan
    "#0ea5e9",  # sky
    "#3b82f6",  # blue
    "#6366f1",  # indigo
    "#8b5cf6",  # violet
    "#a855f7",  # purple
    "#d946ef",  # fuchsia
    "#ec4899",  # pink
    "#f43f5e",  # rose
]


class TagBase(SQLModel):
    """Base tag fields shared across schemas"""

    name: str = Field(
        min_length=1,
        max_length=50,
        description="Tag name (unique per user)",
    )
    color: str = Field(
        default="#3b82f6",
        description="Tag color (hex code)",
    )

    @field_validator("name", mode="before")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """Sanitize tag name: strip whitespace and prevent XSS."""
        if v is None:
            return v
        sanitized = v.strip()
        if not sanitized:
            raise ValueError("Tag name cannot be empty or only whitespace")
        # Basic XSS prevention: remove < and > characters
        sanitized = sanitized.replace("<", "").replace(">", "")
        return sanitized

    @field_validator("color", mode="before")
    @classmethod
    def validate_color(cls, v: str) -> str:
        """Validate color is a valid hex code."""
        if v is None:
            return "#3b82f6"  # Default blue

        # Strip whitespace
        color = v.strip()

        # Add # if missing
        if not color.startswith("#"):
            color = f"#{color}"

        # Validate hex format
        if not (len(color) == 7 and color[0] == "#"):
            try:
                # Try to match against predefined colors by name
                color_lower = color.lower().replace("#", "")
                if color_lower in [c.replace("#", "") for c in TAG_COLORS]:
                    return f"#{color_lower}"
            except Exception:
                pass

            raise ValueError(
                f"Invalid color '{v}'. Use hex format (#RRGGBB) or predefined color"
            )

        return color


class Tag(TagBase, table=True):
    """
    Tag database model.

    Stores user-defined tags for categorizing tasks.
    Each user can have multiple tags with unique names.
    """

    __tablename__ = "tags"

    # Better Auth uses string IDs (not UUIDs)
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique tag identifier (UUID v4 as string)",
    )
    # Better Auth uses string IDs (not UUIDs)
    user_id: str = Field(
        foreign_key="user.id",
        index=True,  # Index for fast user tag queries
        description="Owner user ID (foreign key to user table - Better Auth string ID)",
    )

    # Many-to-many relationship with tasks
    tasks: List["Task"] = Relationship(
        back_populates="tags",
        link_model=TaskTag,
    )

    class Config:
        """SQLModel configuration"""

        json_schema_extra = {
            "example": {
                "id": "750e8400-e29b-41d4-a716-446655440002",
                "name": "work",
                "color": "#3b82f6",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            }
        }


class TagCreate(TagBase):
    """Schema for tag creation request"""

    class Config:
        json_schema_extra = {
            "example": {
                "name": "work",
                "color": "#3b82f6",
            }
        }


class TagUpdate(SQLModel):
    """Schema for tag update request (all fields optional)"""

    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="Updated tag name",
    )
    color: Optional[str] = Field(
        None,
        description="Updated tag color (hex code)",
    )

    @field_validator("name", mode="before")
    @classmethod
    def sanitize_name(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize tag name: strip whitespace and prevent XSS."""
        if v is None:
            return v
        sanitized = v.strip()
        if not sanitized:
            raise ValueError("Tag name cannot be empty or only whitespace")
        # Basic XSS prevention
        sanitized = sanitized.replace("<", "").replace(">", "")
        return sanitized

    @field_validator("color", mode="before")
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate color is a valid hex code."""
        if v is None or v == "":
            return None

        # Strip whitespace
        color = v.strip()

        # Add # if missing
        if not color.startswith("#"):
            color = f"#{color}"

        # Validate hex format
        if not (len(color) == 7 and color[0] == "#"):
            raise ValueError(
                f"Invalid color '{v}'. Use hex format (#RRGGBB)"
            )

        return color

    class Config:
        json_schema_extra = {
            "example": {
                "name": "personal",
                "color": "#22c55e",
            }
        }


class TagResponse(TagBase):
    """
    Schema for tag data in API responses.

    Includes all tag fields for client display.
    """

    id: str  # UUID v4 as string (matches Better Auth)
    user_id: str  # UUID v4 as string (matches Better Auth)

    class Config:
        from_attributes = True  # Allow ORM model conversion
        json_schema_extra = {
            "example": {
                "id": "750e8400-e29b-41d4-a716-446655440002",
                "name": "work",
                "color": "#3b82f6",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            }
        }
