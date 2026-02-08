"""
Integration Tests for Chat API Endpoints

Tests the complete chat flow with agent integration.
"""

import json
from unittest.mock import patch, MagicMock
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from src.auth.jwt import create_access_token
from src.main import app
from src.models.conversation import Conversation, Message
from tests.conftest import create_test_user


class TestCreateConversation:
    """Test conversation creation endpoint."""

    def test_create_conversation_authenticated(self, authenticated_client: TestClient):
        """Test creating a conversation as authenticated user."""
        response = authenticated_client.post(
            "/api/chat/conversations",
            json={"title": "Weekend Planning"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Weekend Planning"
        assert data["message_count"] == 0
        assert "id" in data
        assert "created_at" in data

    def test_create_conversation_without_title(self, authenticated_client: TestClient):
        """Test creating conversation without title (optional)."""
        response = authenticated_client.post(
            "/api/chat/conversations",
            json={},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] is None
        assert data["message_count"] == 0

    def test_create_conversation_unauthenticated(self, client: TestClient):
        """Test creating conversation without authentication fails."""
        response = client.post(
            "/api/chat/conversations",
            json={"title": "Test"},
        )

        assert response.status_code == 401


class TestListConversations:
    """Test conversation listing endpoint."""

    def test_list_conversations_empty(self, authenticated_client: TestClient):
        """Test listing conversations when none exist."""
        response = authenticated_client.get("/api/chat/conversations")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_list_conversations_multiple(
        self, authenticated_client: TestClient, session: Session, test_user
    ):
        """Test listing multiple conversations."""
        # Create 3 conversations
        for i in range(3):
            conv = Conversation(
                user_id=test_user.id,
                title=f"Conversation {i}",
            )
            session.add(conv)
        session.commit()

        response = authenticated_client.get("/api/chat/conversations")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all(c["title"].startswith("Conversation") for c in data)

    def test_list_conversations_pagination(
        self, authenticated_client: TestClient, session: Session, test_user
    ):
        """Test pagination of conversations."""
        # Create 10 conversations
        for i in range(10):
            conv = Conversation(user_id=test_user.id, title=f"Conv {i}")
            session.add(conv)
        session.commit()

        # Get first page
        response = authenticated_client.get("/api/chat/conversations?limit=3&offset=0")
        assert response.status_code == 200
        assert len(response.json()) == 3

        # Get next page
        response = authenticated_client.get("/api/chat/conversations?limit=3&offset=3")
        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_list_conversations_unauthenticated(self, client: TestClient):
        """Test listing conversations without authentication fails."""
        response = client.get("/api/chat/conversations")

        assert response.status_code == 401


class TestGetConversation:
    """Test getting a specific conversation."""

    def test_get_conversation(
        self, authenticated_client: TestClient, session: Session, test_user
    ):
        """Test retrieving a specific conversation."""
        conv = Conversation(user_id=test_user.id, title="Test Conversation")
        session.add(conv)
        session.commit()

        response = authenticated_client.get(f"/api/chat/conversations/{conv.id}")

        assert response.status_code == 200
        data = response.json()
        assert str(data["id"]) == str(conv.id)
        assert data["title"] == "Test Conversation"
        assert data["message_count"] == 0

    def test_get_conversation_not_found(self, authenticated_client: TestClient):
        """Test getting non-existent conversation."""
        fake_id = "00000000-0000-0000-0000-000000000000"

        response = authenticated_client.get(f"/api/chat/conversations/{fake_id}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_conversation_unauthorized(
        self, authenticated_client: TestClient, session: Session
    ):
        """Test getting conversation owned by another user."""
        other_user = create_test_user(session, email="other@test.com")

        conv = Conversation(user_id=other_user.id, title="Other's Conversation")
        session.add(conv)
        session.commit()

        response = authenticated_client.get(f"/api/chat/conversations/{conv.id}")

        assert response.status_code == 403
        assert "not authorized" in response.json()["detail"].lower()


class TestDeleteConversation:
    """Test conversation deletion."""

    def test_delete_conversation(
        self, authenticated_client: TestClient, session: Session, test_user
    ):
        """Test deleting a conversation."""
        conv = Conversation(user_id=test_user.id, title="Delete Me")
        session.add(conv)
        session.commit()

        response = authenticated_client.delete(f"/api/chat/conversations/{conv.id}")

        assert response.status_code == 204

        # Verify conversation is gone
        deleted_conv = session.get(Conversation, conv.id)
        assert deleted_conv is None

    def test_delete_conversation_cascade(
        self, authenticated_client: TestClient, session: Session, test_user
    ):
        """Test that deleting conversation also deletes messages."""
        conv = Conversation(user_id=test_user.id, title="Delete with messages")
        session.add(conv)
        session.commit()

        # Add messages
        msg = Message(
            conversation_id=conv.id,
            user_id=test_user.id,
            role="user",
            content="Test message",
        )
        session.add(msg)
        session.commit()

        # Delete conversation
        response = authenticated_client.delete(f"/api/chat/conversations/{conv.id}")

        assert response.status_code == 204

        # Verify messages are gone
        deleted_msg = session.get(Message, msg.id)
        assert deleted_msg is None

    def test_delete_conversation_unauthorized(
        self, authenticated_client: TestClient, session: Session
    ):
        """Test deleting conversation owned by another user."""
        other_user = create_test_user(session, email="other2@test.com")

        conv = Conversation(user_id=other_user.id, title="Other's Conversation")
        session.add(conv)
        session.commit()

        response = authenticated_client.delete(f"/api/chat/conversations/{conv.id}")

        assert response.status_code == 403


class TestGetConversationMessages:
    """Test retrieving messages from a conversation."""

    def test_get_conversation_messages_empty(
        self, authenticated_client: TestClient, session: Session, test_user
    ):
        """Test getting messages from empty conversation."""
        conv = Conversation(user_id=test_user.id, title="Empty")
        session.add(conv)
        session.commit()

        response = authenticated_client.get(f"/api/chat/conversations/{conv.id}/messages")

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_get_conversation_messages(
        self, authenticated_client: TestClient, session: Session, test_user
    ):
        """Test getting messages from conversation."""
        conv = Conversation(user_id=test_user.id, title="Test")
        session.add(conv)
        session.commit()

        # Add messages
        msg1 = Message(
            conversation_id=conv.id,
            user_id=test_user.id,
            role="user",
            content="Hello",
        )
        msg2 = Message(
            conversation_id=conv.id,
            user_id=test_user.id,
            role="assistant",
            content="Hi there!",
        )
        session.add_all([msg1, msg2])
        session.commit()

        response = authenticated_client.get(f"/api/chat/conversations/{conv.id}/messages")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["role"] == "user"
        assert data[1]["role"] == "assistant"

    def test_get_conversation_messages_unauthorized(
        self, authenticated_client: TestClient, session: Session
    ):
        """Test getting messages from another user's conversation."""
        other_user = create_test_user(session, email="other3@test.com")

        conv = Conversation(user_id=other_user.id, title="Other's Conversation")
        session.add(conv)
        session.commit()

        response = authenticated_client.get(f"/api/chat/conversations/{conv.id}/messages")

        assert response.status_code == 403


@patch("src.services.agent_service.OpenAI")
class TestSendChatMessage:
    """Test sending messages to the chat agent."""

    def test_send_chat_message(
        self, mock_openai_class, authenticated_client: TestClient, session: Session, test_user
    ):
        """Test sending a message to the agent."""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "I'll help you!"
        mock_response.choices[0].message.tool_calls = None
        mock_response.choices[0].finish_reason = "stop"

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        # Create conversation
        conv = Conversation(user_id=test_user.id, title="Chat Test")
        session.add(conv)
        session.commit()

        # Send message
        response = authenticated_client.post(
            f"/api/chat/conversations/{conv.id}/messages",
            json={"content": "Show me my tasks"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["user_message"]["content"] == "Show me my tasks"
        assert data["user_message"]["role"] == "user"
        assert data["assistant_message"]["role"] == "assistant"
        assert "I'll help you!" in data["assistant_message"]["content"]

    def test_send_chat_message_conversation_not_found(
        self, mock_openai_class, authenticated_client: TestClient
    ):
        """Test sending message to non-existent conversation."""
        fake_id = "00000000-0000-0000-0000-000000000000"

        response = authenticated_client.post(
            f"/api/chat/conversations/{fake_id}/messages",
            json={"content": "Test"},
        )

        assert response.status_code == 404

    def test_send_chat_message_unauthorized(
        self, mock_openai_class, authenticated_client: TestClient, session: Session
    ):
        """Test sending message to another user's conversation."""
        other_user = create_test_user(session, email="other4@test.com")

        conv = Conversation(user_id=other_user.id, title="Other's Chat")
        session.add(conv)
        session.commit()

        response = authenticated_client.post(
            f"/api/chat/conversations/{conv.id}/messages",
            json={"content": "Hack attempt"},
        )

        assert response.status_code == 403

    def test_send_chat_message_unauthenticated(
        self, mock_openai_class, client: TestClient, session: Session, test_user
    ):
        """Test sending message without authentication."""
        conv = Conversation(user_id=test_user.id, title="Test")
        session.add(conv)
        session.commit()

        response = client.post(
            f"/api/chat/conversations/{conv.id}/messages",
            json={"content": "Test"},
        )

        assert response.status_code == 401

    def test_send_chat_message_stores_in_db(
        self, mock_openai_class, authenticated_client: TestClient, session: Session, test_user
    ):
        """Test that sent message is stored in database."""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Stored response"
        mock_response.choices[0].message.tool_calls = None
        mock_response.choices[0].finish_reason = "stop"

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        # Create conversation
        conv = Conversation(user_id=test_user.id, title="Persistence Test")
        session.add(conv)
        session.commit()

        # Send message
        response = authenticated_client.post(
            f"/api/chat/conversations/{conv.id}/messages",
            json={"content": "Test persistence"},
        )

        assert response.status_code == 201

        # Verify both messages are in database
        messages = session.query(Message).filter(Message.conversation_id == conv.id).all()
        assert len(messages) == 2
        assert messages[0].role == "user"
        assert messages[1].role == "assistant"
