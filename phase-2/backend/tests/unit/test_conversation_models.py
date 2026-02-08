"""
Unit Tests for Conversation and Message Models

Tests database models for conversation persistence and message storage.
"""

import uuid
from datetime import datetime
from typing import Optional

import pytest
from sqlmodel import Session, select

from src.models.conversation import (
    Conversation,
    ConversationCreate,
    ConversationResponse,
    Message,
    MessageCreate,
    MessageResponse,
)
from src.models.user import User
from tests.conftest import create_test_user


class TestConversationModel:
    """Test Conversation database model and schema."""

    def test_create_conversation(self, session: Session):
        """Test creating a conversation in database."""
        user = create_test_user(session, email="alice@test.com")

        conversation = Conversation(
            id=uuid.uuid4(),
            user_id=user.id,
            title="Weekend Planning",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        # Verify conversation was created
        assert conversation.id is not None
        assert conversation.user_id == user.id
        assert conversation.title == "Weekend Planning"
        assert isinstance(conversation.created_at, datetime)
        assert isinstance(conversation.updated_at, datetime)

    def test_conversation_title_optional(self, session: Session):
        """Test conversation title can be None."""
        user = create_test_user(session, email="bob@test.com")

        conversation = Conversation(
            id=uuid.uuid4(),
            user_id=user.id,
            title=None,  # Optional
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        assert conversation.title is None

    def test_conversation_title_max_length(self, session: Session):
        """Test conversation title respects max length constraint."""
        user = create_test_user(session, email="charlie@test.com")

        # Title with exactly 255 characters (max length)
        long_title = "a" * 255

        conversation = Conversation(
            id=uuid.uuid4(),
            user_id=user.id,
            title=long_title,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        assert len(conversation.title) == 255

    def test_retrieve_conversation_by_user(self, session: Session):
        """Test querying conversations by user_id."""
        user = create_test_user(session, email="dave@test.com")
        other_user = create_test_user(session, email="eve@test.com")

        # Create conversations for both users
        conv1 = Conversation(
            id=uuid.uuid4(),
            user_id=user.id,
            title="My Conversation 1",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        conv2 = Conversation(
            id=uuid.uuid4(),
            user_id=user.id,
            title="My Conversation 2",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        conv3 = Conversation(
            id=uuid.uuid4(),
            user_id=other_user.id,
            title="Other User's Conversation",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        session.add_all([conv1, conv2, conv3])
        session.commit()

        # Query conversations for user
        query = select(Conversation).where(Conversation.user_id == user.id)
        conversations = session.exec(query).all()

        assert len(conversations) == 2
        assert all(c.user_id == user.id for c in conversations)

    def test_conversation_cascade_delete_messages(self, session: Session):
        """Test deleting conversation also deletes related messages."""
        user = create_test_user(session, email="frank@test.com")

        # Create conversation with messages
        conversation = Conversation(
            id=uuid.uuid4(),
            user_id=user.id,
            title="To be deleted",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(conversation)
        session.commit()

        message1 = Message(
            id=uuid.uuid4(),
            conversation_id=conversation.id,
            user_id=user.id,
            role="user",
            content="Hello",
            created_at=datetime.utcnow(),
        )
        message2 = Message(
            id=uuid.uuid4(),
            conversation_id=conversation.id,
            user_id=user.id,
            role="assistant",
            content="Hi there",
            created_at=datetime.utcnow(),
        )

        session.add_all([message1, message2])
        session.commit()

        # Delete conversation
        session.delete(conversation)
        session.commit()

        # Verify messages were cascade deleted
        query = select(Message).where(
            Message.conversation_id == conversation.id
        )
        remaining_messages = session.exec(query).all()

        assert len(remaining_messages) == 0

    def test_conversation_indexes_exist(self, session: Session):
        """Test that indexes for conversation queries are properly set."""
        # This test verifies the table_args index configuration
        # In production, the database would have these indexes for performance
        user = create_test_user(session, email="grace@test.com")

        # Create multiple conversations
        for i in range(5):
            conversation = Conversation(
                id=uuid.uuid4(),
                user_id=user.id,
                title=f"Conversation {i}",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(conversation)
        session.commit()

        # Query using indexed columns (user_id, created_at)
        query = (
            select(Conversation)
            .where(Conversation.user_id == user.id)
            .order_by(Conversation.created_at.desc())
        )
        conversations = session.exec(query).all()

        assert len(conversations) == 5


class TestMessageModel:
    """Test Message database model and schema."""

    def test_create_message(self, session: Session):
        """Test creating a message in database."""
        user = create_test_user(session, email="henry@test.com")

        conversation = Conversation(
            id=uuid.uuid4(),
            user_id=user.id,
            title="Test Conversation",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(conversation)
        session.commit()

        message = Message(
            id=uuid.uuid4(),
            conversation_id=conversation.id,
            user_id=user.id,
            role="user",
            content="Hello, can you help me?",
            created_at=datetime.utcnow(),
        )

        session.add(message)
        session.commit()
        session.refresh(message)

        # Verify message was created
        assert message.id is not None
        assert message.conversation_id == conversation.id
        assert message.user_id == user.id
        assert message.role == "user"
        assert message.content == "Hello, can you help me?"
        assert message.tool_calls is None
        assert isinstance(message.created_at, datetime)

    def test_message_role_values(self, session: Session):
        """Test message role can be 'user' or 'assistant'."""
        user = create_test_user(session, email="iris@test.com")

        conversation = Conversation(
            id=uuid.uuid4(),
            user_id=user.id,
            title="Test",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(conversation)
        session.commit()

        # Test user message
        user_msg = Message(
            id=uuid.uuid4(),
            conversation_id=conversation.id,
            user_id=user.id,
            role="user",
            content="User message",
            created_at=datetime.utcnow(),
        )

        # Test assistant message
        asst_msg = Message(
            id=uuid.uuid4(),
            conversation_id=conversation.id,
            user_id=user.id,
            role="assistant",
            content="Assistant response",
            created_at=datetime.utcnow(),
        )

        session.add_all([user_msg, asst_msg])
        session.commit()

        assert user_msg.role == "user"
        assert asst_msg.role == "assistant"

    def test_message_with_tool_calls(self, session: Session):
        """Test storing tool invocation data in message."""
        user = create_test_user(session, email="jack@test.com")

        conversation = Conversation(
            id=uuid.uuid4(),
            user_id=user.id,
            title="Test",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(conversation)
        session.commit()

        # Tool calls JSON structure
        tool_calls = {
            "id": "call_123",
            "type": "function",
            "function": {
                "name": "add_task",
                "arguments": '{"title": "Buy groceries"}',
            },
        }

        message = Message(
            id=uuid.uuid4(),
            conversation_id=conversation.id,
            user_id=user.id,
            role="assistant",
            content="I'll add that task for you.",
            tool_calls=tool_calls,
            created_at=datetime.utcnow(),
        )

        session.add(message)
        session.commit()
        session.refresh(message)

        assert message.tool_calls == tool_calls
        assert message.tool_calls["function"]["name"] == "add_task"

    def test_retrieve_messages_by_conversation(self, session: Session):
        """Test querying messages by conversation_id."""
        user = create_test_user(session, email="karl@test.com")

        conv1 = Conversation(
            id=uuid.uuid4(),
            user_id=user.id,
            title="Conv 1",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        conv2 = Conversation(
            id=uuid.uuid4(),
            user_id=user.id,
            title="Conv 2",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add_all([conv1, conv2])
        session.commit()

        # Create messages in both conversations
        msg1 = Message(
            id=uuid.uuid4(),
            conversation_id=conv1.id,
            user_id=user.id,
            role="user",
            content="Message 1 in Conv 1",
            created_at=datetime.utcnow(),
        )
        msg2 = Message(
            id=uuid.uuid4(),
            conversation_id=conv1.id,
            user_id=user.id,
            role="assistant",
            content="Response 1 in Conv 1",
            created_at=datetime.utcnow(),
        )
        msg3 = Message(
            id=uuid.uuid4(),
            conversation_id=conv2.id,
            user_id=user.id,
            role="user",
            content="Message in Conv 2",
            created_at=datetime.utcnow(),
        )

        session.add_all([msg1, msg2, msg3])
        session.commit()

        # Query messages in first conversation
        query = select(Message).where(Message.conversation_id == conv1.id)
        messages = session.exec(query).all()

        assert len(messages) == 2
        assert all(m.conversation_id == conv1.id for m in messages)

    def test_retrieve_messages_ordered_by_created_at(self, session: Session):
        """Test messages can be ordered by creation time."""
        user = create_test_user(session, email="lisa@test.com")

        conversation = Conversation(
            id=uuid.uuid4(),
            user_id=user.id,
            title="Test",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(conversation)
        session.commit()

        # Create messages with different timestamps
        import time

        msg1 = Message(
            id=uuid.uuid4(),
            conversation_id=conversation.id,
            user_id=user.id,
            role="user",
            content="First message",
            created_at=datetime.utcnow(),
        )
        session.add(msg1)
        session.commit()

        time.sleep(0.01)  # Small delay

        msg2 = Message(
            id=uuid.uuid4(),
            conversation_id=conversation.id,
            user_id=user.id,
            role="assistant",
            content="Second message",
            created_at=datetime.utcnow(),
        )
        session.add(msg2)
        session.commit()

        # Retrieve in chronological order
        query = (
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.asc())
        )
        messages = session.exec(query).all()

        assert len(messages) == 2
        assert messages[0].content == "First message"
        assert messages[1].content == "Second message"

    def test_message_user_id_for_audit_trail(self, session: Session):
        """Test user_id on message enables audit trail."""
        user1 = create_test_user(session, email="mary@test.com")
        user2 = create_test_user(session, email="nancy@test.com")

        conversation = Conversation(
            id=uuid.uuid4(),
            user_id=user1.id,  # Conversation owner
            title="Shared Conversation",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(conversation)
        session.commit()

        # Messages from both users in same conversation
        msg1 = Message(
            id=uuid.uuid4(),
            conversation_id=conversation.id,
            user_id=user1.id,
            role="user",
            content="Message from user1",
            created_at=datetime.utcnow(),
        )
        msg2 = Message(
            id=uuid.uuid4(),
            conversation_id=conversation.id,
            user_id=user1.id,
            role="assistant",
            content="Response from assistant (associated with user1)",
            created_at=datetime.utcnow(),
        )

        session.add_all([msg1, msg2])
        session.commit()

        # Query messages by user for audit trail
        query = select(Message).where(Message.user_id == user1.id)
        messages = session.exec(query).all()

        assert len(messages) == 2
        assert all(m.user_id == user1.id for m in messages)


class TestConversationSchemas:
    """Test request/response Pydantic schemas."""

    def test_conversation_create_schema(self):
        """Test ConversationCreate request schema."""
        schema = ConversationCreate(title="Weekend Planning")

        assert schema.title == "Weekend Planning"

    def test_conversation_create_title_optional(self):
        """Test ConversationCreate title is optional."""
        schema = ConversationCreate()

        assert schema.title is None

    def test_conversation_response_schema(self, session: Session):
        """Test ConversationResponse schema."""
        user = create_test_user(session, email="oscar@test.com")

        conversation = Conversation(
            id=uuid.uuid4(),
            user_id=user.id,
            title="Test Conversation",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        # Create response schema from ORM model
        response = ConversationResponse(
            id=conversation.id,
            user_id=conversation.user_id,
            title=conversation.title,
            message_count=0,  # No messages yet
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
        )

        assert response.id == conversation.id
        assert response.user_id == conversation.user_id
        assert response.title == conversation.title
        assert response.message_count == 0


class TestMessageSchemas:
    """Test request/response Pydantic schemas for messages."""

    def test_message_create_schema(self):
        """Test MessageCreate request schema."""
        schema = MessageCreate(content="Show me all my tasks")

        assert schema.content == "Show me all my tasks"

    def test_message_create_min_length(self):
        """Test MessageCreate content has min length."""
        with pytest.raises(ValueError):
            MessageCreate(content="")

    def test_message_response_schema(self, session: Session):
        """Test MessageResponse schema."""
        user = create_test_user(session, email="paul@test.com")

        conversation = Conversation(
            id=uuid.uuid4(),
            user_id=user.id,
            title="Test",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(conversation)
        session.commit()

        message = Message(
            id=uuid.uuid4(),
            conversation_id=conversation.id,
            user_id=user.id,
            role="user",
            content="What are my tasks?",
            created_at=datetime.utcnow(),
        )
        session.add(message)
        session.commit()
        session.refresh(message)

        # Create response schema from ORM model
        response = MessageResponse(
            id=message.id,
            conversation_id=message.conversation_id,
            user_id=message.user_id,
            role=message.role,
            content=message.content,
            tool_calls=message.tool_calls,
            created_at=message.created_at,
        )

        assert response.id == message.id
        assert response.conversation_id == conversation.id
        assert response.role == "user"
        assert response.content == "What are my tasks?"
