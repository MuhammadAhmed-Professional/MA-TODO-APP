"""
User Model (Phase V)

Simple user model for authentication and ownership.
Uses Better Auth string IDs.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """
    User database model.

    Stores user account information for authentication and task ownership.
    Uses string IDs to match Better Auth.
    """

    __tablename__ = "user"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
        description="Unique user identifier (UUID v4 as string)",
    )
    email: str = Field(
        unique=True,
        index=True,
        max_length=255,
        description="User email address (unique)",
    )
    name: str = Field(
        max_length=100,
        description="User display name",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Account creation timestamp (UTC)",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp (UTC)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "name": "John Doe",
                "created_at": "2026-01-31T16:00:00Z",
                "updated_at": "2026-01-31T16:00:00Z",
            }
        }


class UserResponse(SQLModel):
    """Schema for user data in API responses"""

    id: str
    email: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True
