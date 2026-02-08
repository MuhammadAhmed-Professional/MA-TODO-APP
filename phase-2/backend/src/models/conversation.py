"""
Conversation and Message Models for AI Chatbot

Represents chat conversations and individual messages for Phase III AI-powered todo assistant.
"""

import uuid
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import JSON, Column, Index
from sqlmodel import Field, Relationship, SQLModel


class Conversation(SQLModel, table=True):
    """
    Represents a chat conversation session between user and AI assistant.

    Stores conversation metadata and groups related messages together.
    Supports conversation history and context management.
    """

    __tablename__ = "conversations"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique conversation identifier (UUID v4)",
    )
    user_id: str = Field(
        foreign_key="user.id",
        index=True,
        description="Owner user ID (Better Auth string ID, foreign key to user table)",
    )
    title: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Optional conversation title (auto-generated from first message)",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Conversation creation timestamp (UTC)",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp (UTC)",
    )

    # Relationships
    messages: list["Message"] = Relationship(
        back_populates="conversation",
        cascade_delete=True,
    )

    __table_args__ = (
        # Composite index for efficient user conversation queries
        # Used in: SELECT * FROM conversations WHERE user_id = ? ORDER BY created_at DESC
        Index("ix_conversations_user_id_created_at", "user_id", "created_at"),
    )

    class Config:
        """SQLModel configuration"""

        json_schema_extra = {
            "example": {
                "id": "750e8400-e29b-41d4-a716-446655440001",
                "user_id": "p2776Z8HHiUv8GxFHnuso20ALer4HHWy",
                "title": "Planning my week tasks",
                "created_at": "2025-12-13T18:00:00Z",
                "updated_at": "2025-12-13T18:00:00Z",
            }
        }


class Message(SQLModel, table=True):
    """
    Represents a single message in a conversation.

    Stores both user input and AI assistant responses, including tool invocations
    and results for full conversation history and context.
    """

    __tablename__ = "messages"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique message identifier (UUID v4)",
    )
    conversation_id: uuid.UUID = Field(
        foreign_key="conversations.id",
        index=True,
        description="Parent conversation ID (foreign key)",
    )
    user_id: str = Field(
        foreign_key="user.id",
        index=True,
        description="User ID for audit trail (Better Auth string ID, foreign key)",
    )
    role: str = Field(
        description="Message origin: 'user' or 'assistant'",
    )
    content: str = Field(
        description="Text content of the message",
    )
    tool_calls: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON),
        description="JSON structure of tool invocations (if any)",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Message creation timestamp (UTC)",
    )

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")

    __table_args__ = (
        # Composite index for efficient message retrieval by conversation
        # Used in: SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC
        Index("ix_messages_conversation_id_created_at", "conversation_id", "created_at"),
        # Index for user audit queries
        Index("ix_messages_user_id_created_at", "user_id", "created_at"),
    )

    class Config:
        """SQLModel configuration"""

        json_schema_extra = {
            "example": {
                "id": "850e8400-e29b-41d4-a716-446655440002",
                "conversation_id": "750e8400-e29b-41d4-a716-446655440001",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "role": "user",
                "content": "Add a task to buy groceries tomorrow",
                "tool_calls": None,
                "created_at": "2025-12-13T18:01:00Z",
            }
        }


class ConversationCreate(SQLModel):
    """Schema for conversation creation request"""

    title: Optional[str] = Field(
        None,
        max_length=255,
        description="Optional conversation title",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Weekend planning",
            }
        }


class MessageCreate(SQLModel):
    """Schema for message creation request"""

    content: str = Field(
        min_length=1,
        description="Message text content",
    )
    conversation_id: Optional[UUID] = Field(
        default=None,
        description="Optional conversation ID to continue existing conversation",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "content": "Show me all my pending tasks",
                "conversation_id": None,
            }
        }


class ConversationResponse(SQLModel):
    """
    Schema for conversation data in API responses.

    Includes metadata and optionally the last N messages.
    """

    id: uuid.UUID
    user_id: str
    title: Optional[str]
    message_count: int = Field(description="Total number of messages in conversation")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "750e8400-e29b-41d4-a716-446655440001",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Planning my week tasks",
                "message_count": 12,
                "created_at": "2025-12-13T18:00:00Z",
                "updated_at": "2025-12-13T18:15:00Z",
            }
        }


class MessageResponse(SQLModel):
    """
    Schema for message data in API responses.

    Includes full message content and tool invocation history.
    """

    id: uuid.UUID
    conversation_id: uuid.UUID
    user_id: str
    role: str
    content: str
    tool_calls: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "850e8400-e29b-41d4-a716-446655440002",
                "conversation_id": "750e8400-e29b-41d4-a716-446655440001",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "role": "assistant",
                "content": "I've added 'Buy groceries' to your task list for tomorrow.",
                "tool_calls": {
                    "id": "call_123",
                    "type": "function",
                    "function": {
                        "name": "add_task",
                        "arguments": '{"user_id": "550e8400-e29b-41d4-a716-446655440000", "title": "Buy groceries"}',
                    },
                },
                "created_at": "2025-12-13T18:01:05Z",
            }
        }
