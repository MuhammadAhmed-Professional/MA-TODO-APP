# Phase III Chatbot - Data Models (Phase 1: Design)

**Created**: 2025-12-13
**Stage**: design
**Status**: Complete - SQLModel definitions ready for implementation
**Branch**: 001-phase-3-chatbot

---

## 1. Overview

This document specifies the SQLModel data models for Phase III chatbot persistence. These models extend Phase II's Task model with Conversation and Message tables for maintaining multi-turn conversation state.

### Model Hierarchy

```
User (from Phase II)
├── Conversation
│   └── Message
└── Task (existing)
```

### Storage Strategy

- **Conversation**: Tracks chat sessions with metadata
- **Message**: Stores individual messages (user and assistant) with tool call history
- **Relationships**: Enforced via foreign keys and SQLAlchemy relationships

---

## 2. Conversation Model

### Purpose
Represents a chat session between a user and the AI assistant. Groups related messages into conversations for context management.

### SQLModel Definition

```python
# phase-2/backend/src/models/conversation.py

from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from typing import List, Optional

class Conversation(SQLModel, table=True):
    """
    Represents a chat conversation session.

    Attributes:
        id: Unique conversation identifier (UUID)
        user_id: Reference to User who created the conversation
        title: Optional conversation title (auto-generated from first message if None)
        created_at: Timestamp when conversation was created
        updated_at: Timestamp when conversation was last updated

    Relationships:
        messages: List of Message objects in this conversation
        user: Reference to User who owns this conversation
    """

    __tablename__ = "conversations"

    # Primary Key
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Foreign Keys
    user_id: UUID = Field(foreign_key="user.id", index=True)

    # Data Fields
    title: Optional[str] = Field(None, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        cascade_delete=True
    )
    user: "User" = Relationship(back_populates="conversations")

    # Indexes
    __table_args__ = (
        # Composite index for efficient user conversation queries
        # Used in: SELECT * FROM conversations WHERE user_id = ? ORDER BY created_at DESC
        Index("ix_conversations_user_id_created_at", "user_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Conversation id={self.id} user_id={self.user_id}>"
```

### Usage Patterns

#### Create New Conversation
```python
conversation = Conversation(
    user_id=current_user.id,
    title=None  # Will be generated from first message
)
session.add(conversation)
session.commit()
```

#### Fetch User's Conversations
```python
conversations = session.exec(
    select(Conversation)
    .where(Conversation.user_id == user_id)
    .order_by(Conversation.created_at.desc())
    .limit(50)  # Last 50 conversations
).all()
```

#### Update Conversation Title
```python
conversation.title = "Planning my week"
conversation.updated_at = datetime.utcnow()
session.add(conversation)
session.commit()
```

#### Get Conversation with All Messages
```python
conversation = session.get(Conversation, conversation_id)
messages = conversation.messages  # Loaded via relationship
```

---

## 3. Message Model

### Purpose
Represents individual messages within a conversation, storing both user input and AI responses, including tool invocations and results.

### SQLModel Definition

```python
class Message(SQLModel, table=True):
    """
    Represents a single message in a conversation.

    Attributes:
        id: Unique message identifier (UUID)
        conversation_id: Reference to parent Conversation
        user_id: Reference to User (for audit trail)
        role: Message origin - "user" or "assistant"
        content: Text content of the message
        tool_calls: JSON structure of tool invocations (if any)
        created_at: Timestamp when message was created

    Relationships:
        conversation: Reference to parent Conversation
        user: Reference to User (for audit trail)

    Message Format:
        - User message: {"role": "user", "content": "Add task to buy milk"}
        - Assistant message: {
            "role": "assistant",
            "content": "I've created a task: 'Buy milk'. Would you like to add details?",
            "tool_calls": [
              {
                "id": "call_123",
                "type": "function",
                "function": {
                  "name": "add_task",
                  "arguments": "{\"user_id\": \"...\", \"title\": \"Buy milk\"}"
                }
              }
            ]
          }
    """

    __tablename__ = "messages"

    # Primary Key
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Foreign Keys
    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        index=True,
        nullable=False
    )
    user_id: UUID = Field(
        foreign_key="user.id",
        index=True,
        nullable=False
    )

    # Data Fields
    role: str = Field(...)  # "user" or "assistant"
    content: str = Field(..., nullable=False)  # Message text
    tool_calls: Optional[dict] = Field(None, sa_column=Column(JSON))  # Tool invocations
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")
    user: "User" = Relationship(back_populates="messages")

    # Indexes
    __table_args__ = (
        # Composite index for efficient history retrieval
        # Used in: SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at DESC
        Index("ix_messages_conversation_id_created_at", "conversation_id", "created_at"),
        # Additional index for user message queries (audit trail)
        Index("ix_messages_user_id_created_at", "user_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Message id={self.id} role={self.role} conversation_id={self.conversation_id}>"

    @property
    def is_user_message(self) -> bool:
        """Check if this is a user message"""
        return self.role == "user"

    @property
    def is_assistant_message(self) -> bool:
        """Check if this is an assistant message"""
        return self.role == "assistant"

    @property
    def has_tool_calls(self) -> bool:
        """Check if this message contains tool calls"""
        return self.tool_calls is not None and len(self.tool_calls) > 0
```

### Tool Call Structure

```python
# Example tool_calls JSON structure (OpenAI Agents SDK format)

tool_calls_example = {
    "calls": [
        {
            "id": "call_abc123",
            "type": "function",
            "function": {
                "name": "add_task",
                "arguments": {
                    "user_id": "550e8400-e29b-41d4-a716-446655440000",
                    "title": "Buy groceries",
                    "description": "milk, eggs, bread"
                }
            },
            "result": {
                "task_id": "550e8400-e29b-41d4-a716-446655440001",
                "title": "Buy groceries",
                "status": "pending",
                "created_at": "2025-12-13T10:30:00Z"
            }
        }
    ]
}
```

### Usage Patterns

#### Store User Message
```python
user_message = Message(
    conversation_id=conversation.id,
    user_id=current_user.id,
    role="user",
    content="Add a task to buy groceries"
)
session.add(user_message)
session.commit()
```

#### Store Assistant Message with Tool Calls
```python
assistant_message = Message(
    conversation_id=conversation.id,
    user_id=current_user.id,
    role="assistant",
    content="I've created a task: 'Buy groceries'. Would you like to add details?",
    tool_calls={
        "calls": [
            {
                "id": "call_123",
                "type": "function",
                "function": {
                    "name": "add_task",
                    "arguments": {
                        "user_id": str(current_user.id),
                        "title": "Buy groceries"
                    }
                },
                "result": {
                    "task_id": str(task.id),
                    "title": "Buy groceries",
                    "status": "pending",
                    "created_at": task.created_at.isoformat()
                }
            }
        ]
    }
)
session.add(assistant_message)
session.commit()
```

#### Fetch Conversation History (Last 20 Messages)
```python
messages = session.exec(
    select(Message)
    .where(Message.conversation_id == conversation_id)
    .order_by(Message.created_at.asc())
    .limit(20)
).all()
```

#### Convert Messages to Agent Context Format
```python
def messages_to_agent_context(messages: List[Message]) -> List[dict]:
    """Convert Message objects to OpenAI Agents SDK format"""
    return [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in messages
    ]

# Usage:
agent_history = messages_to_agent_context(messages)
```

#### Query Recent User Messages (For Pronoun Resolution)
```python
# Get last 5 user messages for pronoun resolution context
recent_user_messages = session.exec(
    select(Message)
    .where(
        Message.conversation_id == conversation_id,
        Message.role == "user"
    )
    .order_by(Message.created_at.desc())
    .limit(5)
).all()
```

---

## 4. User Model Extension (from Phase II)

The User model from Phase II requires a relationship update:

```python
# Update to phase-2/backend/src/models/user.py

class User(SQLModel, table=True):
    # ... existing fields ...

    # NEW: Relationships to Phase III models
    conversations: List[Conversation] = Relationship(back_populates="user")
    messages: List[Message] = Relationship(back_populates="user")
```

---

## 5. Database Schema (SQL)

### Conversation Table

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    title VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_conversations_user_id_created_at ON conversations(user_id, created_at);
```

### Message Table

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    role VARCHAR(10) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    tool_calls JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_messages_conversation_id_created_at ON messages(conversation_id, created_at);
CREATE INDEX ix_messages_user_id_created_at ON messages(user_id, created_at);
```

---

## 6. Migration File

### Alembic Migration (003)

```python
# phase-2/backend/src/db/migrations/versions/003_add_conversation_tables.py

"""Add conversation and message tables for Phase III chatbot

Revision ID: 003
Revises: 002
Create Date: 2025-12-13 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create conversations and messages tables"""

    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        mysql_default='utf8mb4'
    )

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(length=10), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tool_calls', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("role IN ('user', 'assistant')", name='check_role'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        mysql_default='utf8mb4'
    )

    # Create indexes
    op.create_index(
        'ix_conversations_user_id_created_at',
        'conversations',
        ['user_id', 'created_at']
    )

    op.create_index(
        'ix_messages_conversation_id_created_at',
        'messages',
        ['conversation_id', 'created_at']
    )

    op.create_index(
        'ix_messages_user_id_created_at',
        'messages',
        ['user_id', 'created_at']
    )


def downgrade() -> None:
    """Drop conversations and messages tables"""

    op.drop_index('ix_messages_user_id_created_at', table_name='messages')
    op.drop_index('ix_messages_conversation_id_created_at', table_name='messages')
    op.drop_index('ix_conversations_user_id_created_at', table_name='conversations')
    op.drop_table('messages')
    op.drop_table('conversations')
```

---

## 7. Validation Rules

### Conversation Validation

```python
class ConversationCreate(SQLModel):
    """Pydantic model for creating conversations"""
    title: Optional[str] = Field(None, max_length=255)

class ConversationResponse(SQLModel):
    """Response model for conversations"""
    id: UUID
    user_id: UUID
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
```

### Message Validation

```python
class MessageCreate(SQLModel):
    """Pydantic model for creating messages"""
    conversation_id: UUID
    role: str = Field(..., min_length=4, max_length=10)
    content: str = Field(..., min_length=1, max_length=10000)
    tool_calls: Optional[dict] = None

class MessageResponse(SQLModel):
    """Response model for messages"""
    id: UUID
    conversation_id: UUID
    user_id: UUID
    role: str
    content: str
    tool_calls: Optional[dict]
    created_at: datetime

    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in ('user', 'assistant'):
            raise ValueError("role must be 'user' or 'assistant'")
        return v

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("content cannot be empty")
        if len(v) > 10000:
            raise ValueError("content cannot exceed 10000 characters")
        return v.strip()
```

---

## 8. Performance Considerations

### Query Optimization

1. **Conversation History Retrieval**
   - Index: `(conversation_id, created_at)`
   - Query: `SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at DESC LIMIT 20`
   - Expected time: < 10ms

2. **User Conversations List**
   - Index: `(user_id, created_at)`
   - Query: `SELECT * FROM conversations WHERE user_id = ? ORDER BY created_at DESC LIMIT 50`
   - Expected time: < 20ms

3. **Recent Messages for Pronoun Resolution**
   - Index: `(conversation_id, created_at)`
   - Query: `SELECT * FROM messages WHERE conversation_id = ? AND role = 'user' ORDER BY created_at DESC LIMIT 5`
   - Expected time: < 5ms

### Pagination Strategy

```python
def get_conversation_messages(
    conversation_id: UUID,
    limit: int = 20,
    offset: int = 0
) -> List[Message]:
    """Fetch paginated messages from conversation"""
    return session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
        .offset(offset)
    ).all()
```

---

## 9. Data Integrity Constraints

### Foreign Key Constraints
- `messages.conversation_id` → `conversations.id` (CASCADE DELETE)
- `messages.user_id` → `user.id` (CASCADE DELETE)
- `conversations.user_id` → `user.id` (CASCADE DELETE)

### Check Constraints
- `messages.role` must be 'user' or 'assistant'
- `conversations.title` max 255 characters (optional)
- `messages.content` must be non-empty

### NOT NULL Constraints
- `messages.conversation_id` (required)
- `messages.user_id` (required)
- `messages.role` (required)
- `messages.content` (required)
- `conversations.created_at` (required)

---

## 10. Testing Fixtures

### Sample Data

```python
# tests/fixtures/conversation_fixtures.py

import pytest
from uuid import uuid4
from datetime import datetime

@pytest.fixture
def sample_conversation(db_session, sample_user):
    """Create a sample conversation"""
    conversation = Conversation(
        user_id=sample_user.id,
        title="Planning my week"
    )
    db_session.add(conversation)
    db_session.commit()
    return conversation

@pytest.fixture
def sample_messages(db_session, sample_conversation, sample_user):
    """Create sample messages in conversation"""
    messages = [
        Message(
            conversation_id=sample_conversation.id,
            user_id=sample_user.id,
            role="user",
            content="Add a task to buy groceries"
        ),
        Message(
            conversation_id=sample_conversation.id,
            user_id=sample_user.id,
            role="assistant",
            content="I've created a task: 'Buy groceries'",
            tool_calls={
                "calls": [{
                    "id": "call_123",
                    "type": "function",
                    "function": {
                        "name": "add_task",
                        "arguments": {
                            "user_id": str(sample_user.id),
                            "title": "Buy groceries"
                        }
                    }
                }]
            }
        )
    ]
    for msg in messages:
        db_session.add(msg)
    db_session.commit()
    return messages
```

---

## Summary

The Conversation and Message models provide:

✅ **Structured Persistence**: Multi-turn conversations with full history
✅ **Tool Call Tracking**: JSON storage of MCP tool invocations
✅ **User Isolation**: Foreign keys enforce per-user data access
✅ **Efficient Queries**: Composite indexes for common access patterns
✅ **Audit Trail**: Timestamps and user_id references for tracking
✅ **Scalability**: Pagination support for large conversations
✅ **Data Integrity**: Check constraints and foreign keys

---

**Status**: ✅ Phase 1 (Design) - Data Models Complete
**Next Step**: Create API contracts and deployment guide
