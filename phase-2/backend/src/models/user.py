"""
User Model

Represents a registered application user with authentication credentials.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import EmailStr, field_validator
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    """Base user fields shared across schemas"""

    email: EmailStr = Field(
        unique=True,
        index=True,
        max_length=255,
        description="Unique email address for authentication",
    )
    name: str = Field(
        min_length=1,
        max_length=100,
        description="User's display name",
    )

    @field_validator("name", mode="before")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """Sanitize name: strip whitespace and prevent XSS."""
        if v is None:
            return v
        # Strip leading/trailing whitespace
        sanitized = v.strip()
        if not sanitized:
            raise ValueError("Name cannot be empty or only whitespace")
        # Basic XSS prevention: remove < and > characters
        sanitized = sanitized.replace("<", "").replace(">", "")
        return sanitized


class User(UserBase, table=True):
    """
    User database model - Compatible with Better Auth schema.

    Stores user account information including authentication credentials.
    Passwords are hashed with bcrypt and never stored in plaintext.

    NOTE: This model is compatible with Better Auth's 'user' table schema.
    Better Auth manages authentication; FastAPI uses this for task ownership.
    """

    __tablename__ = "user"  # Better Auth uses singular 'user'

    # Better Auth uses string IDs (not UUIDs)
    id: str = Field(
        primary_key=True,
        description="Unique user identifier (Better Auth managed)",
    )

    # Better Auth fields (camelCase to match Better Auth schema)
    emailVerified: bool = Field(
        default=False,
        sa_column_kwargs={"name": "emailVerified"},  # Preserve camelCase in DB
        description="Email verification status (managed by Better Auth)",
    )
    image: Optional[str] = Field(
        default=None,
        description="User avatar URL (optional)",
    )
    createdAt: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"name": "createdAt"},  # Preserve camelCase in DB
        description="Account creation timestamp (UTC)",
    )
    updatedAt: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"name": "updatedAt"},  # Preserve camelCase in DB
        description="Last update timestamp (UTC)",
    )

    # NOTE: Better Auth manages passwords separately - no hashed_password column in user table

    class Config:
        """SQLModel configuration"""

        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "alice@example.com",
                "name": "Alice Smith",
                "created_at": "2025-12-06T12:00:00Z",
                "updated_at": "2025-12-06T12:00:00Z",
            }
        }


class UserCreate(UserBase):
    """Schema for user signup request"""

    password: str = Field(
        min_length=8,
        max_length=100,
        description="User password (min 8 characters)",
    )

    @field_validator("password", mode="before")
    @classmethod
    def sanitize_password(cls, v: str) -> str:
        """Sanitize password: strip whitespace only."""
        if v is None:
            return v
        # Strip leading/trailing whitespace only
        # DO NOT strip internal whitespace (passwords may contain spaces)
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "email": "alice@example.com",
                "name": "Alice Smith",
                "password": "SecurePass123!",
            }
        }


class UserLogin(SQLModel):
    """Schema for user login request"""

    email: EmailStr = Field(description="User email address")
    password: str = Field(description="User password")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "alice@example.com",
                "password": "SecurePass123!",
            }
        }


class UserResponse(UserBase):
    """
    Schema for user data in API responses.

    Excludes sensitive fields like hashed_password.
    Compatible with Better Auth response format.
    """

    id: str  # UUID v4 as string (matches Better Auth)
    emailVerified: bool
    createdAt: datetime
    updatedAt: datetime
    image: Optional[str] = None

    class Config:
        from_attributes = True  # Allow ORM model conversion
        populate_by_name = True  # Allow both camelCase and snake_case field names
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "alice@example.com",
                "name": "Alice Smith",
                "emailVerified": False,
                "createdAt": "2025-12-06T12:00:00Z",
                "updatedAt": "2025-12-06T12:00:00Z",
                "image": None,
            }
        }
