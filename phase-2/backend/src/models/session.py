"""
Better Auth Session Model

Maps to the `session` table created by Better Auth in the shared database.
Used for validating user sessions without calling the auth server.
"""

from datetime import datetime
from sqlmodel import SQLModel, Field


class BetterAuthSession(SQLModel, table=True):
    """
    Better Auth session table schema.

    This table is created and managed by the Better Auth server.
    The backend queries it directly for session validation instead of
    making HTTP calls to the auth server.

    Table name: session (Better Auth default)
    """
    __tablename__ = "session"

    # Session ID (primary key - internal identifier)
    id: str = Field(primary_key=True, description="Internal session ID")

    # Session token (matches `token` from login response JSON)
    token: str = Field(index=True, description="Public session token from login response")

    # User ID (foreign key to user table)
    userId: str = Field(index=True, description="Better Auth user ID (not UUID)")

    # Session expiration timestamp
    expiresAt: datetime = Field(description="Session expiration time (UTC)")

    # Optional session metadata
    ipAddress: str | None = Field(default=None, description="Client IP address")
    userAgent: str | None = Field(default=None, description="Client user agent")

    # Timestamps (Better Auth auto-manages these)
    createdAt: datetime | None = Field(default=None, description="Session creation time")
    updatedAt: datetime | None = Field(default=None, description="Last session update time")
