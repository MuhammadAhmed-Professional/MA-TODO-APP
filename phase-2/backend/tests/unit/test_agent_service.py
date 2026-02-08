"""
Unit Tests for Agent Service

Tests the OpenAI Agent service integration with MCP tools.
Note: These tests use mocking to avoid actual OpenAI API calls.
"""

import json
import uuid
from unittest.mock import Mock, patch, MagicMock

import pytest
from sqlmodel import Session

from src.services.agent_service import AgentService, create_agent_service
from src.services.mcp_tools import MCP_TOOLS
from tests.conftest import create_test_user


class TestAgentServiceInitialization:
    """Test Agent Service initialization."""

    def test_agent_service_creation(self, session: Session):
        """Test creating an AgentService instance."""
        with patch("src.services.agent_service.OpenAI"):
            service = AgentService(session, openai_api_key="test-key")

            assert service.session is session
            assert service.mcp_service is not None
            assert len(service.system_prompt) > 0

    def test_factory_function(self, session: Session):
        """Test create_agent_service factory function."""
        with patch("src.services.agent_service.OpenAI"):
            service = create_agent_service(session)

            assert isinstance(service, AgentService)
            assert service.session is session

    def test_initialize_agent(self, session: Session):
        """Test agent initialization returns correct status."""
        with patch("src.services.agent_service.OpenAI"):
            service = AgentService(session, openai_api_key="test-key")
            result = service.initialize_agent()

            assert result["status"] == "initialized"
            assert result["model"] == "gpt-4-turbo"
            assert result["temperature"] == 0.7
            assert result["tools_count"] == 5
            assert len(result["tools"]) == 5


class TestAgentToolExecution:
    """Test agent tool execution."""

    def test_execute_add_task_tool(self, session: Session):
        """Test executing add_task tool."""
        with patch("src.services.agent_service.OpenAI"):
            user = create_test_user(session, email="alice@test.com")
            service = AgentService(session, openai_api_key="test-key")

            result = service._execute_tool_call(
                user_id=user.id,
                tool_name="add_task",
                tool_args={"title": "Test Task", "description": "Test Description"},
            )

            assert result["success"] is True
            assert result["task"]["title"] == "Test Task"

    def test_execute_list_tasks_tool(self, session: Session):
        """Test executing list_tasks tool."""
        with patch("src.services.agent_service.OpenAI"):
            user = create_test_user(session, email="bob@test.com")
            service = AgentService(session, openai_api_key="test-key")

            # Add a task first
            service._execute_tool_call(
                user_id=user.id,
                tool_name="add_task",
                tool_args={"title": "Task 1"},
            )

            # List tasks
            result = service._execute_tool_call(
                user_id=user.id,
                tool_name="list_tasks",
                tool_args={},
            )

            assert result["success"] is True
            assert result["total"] == 1

    def test_execute_complete_task_tool(self, session: Session):
        """Test executing complete_task tool."""
        with patch("src.services.agent_service.OpenAI"):
            user = create_test_user(session, email="charlie@test.com")
            service = AgentService(session, openai_api_key="test-key")

            # Add task
            add_result = service._execute_tool_call(
                user_id=user.id,
                tool_name="add_task",
                tool_args={"title": "Task"},
            )
            task_id = add_result["task"]["id"]

            # Complete task
            result = service._execute_tool_call(
                user_id=user.id,
                tool_name="complete_task",
                tool_args={"task_id": task_id},
            )

            assert result["success"] is True
            assert result["task"]["is_complete"] is True

    def test_execute_delete_task_tool(self, session: Session):
        """Test executing delete_task tool."""
        with patch("src.services.agent_service.OpenAI"):
            user = create_test_user(session, email="dave@test.com")
            service = AgentService(session, openai_api_key="test-key")

            # Add task
            add_result = service._execute_tool_call(
                user_id=user.id,
                tool_name="add_task",
                tool_args={"title": "Delete me"},
            )
            task_id = add_result["task"]["id"]

            # Delete task
            result = service._execute_tool_call(
                user_id=user.id,
                tool_name="delete_task",
                tool_args={"task_id": task_id},
            )

            assert result["success"] is True
            assert "deleted" in result["message"].lower()

    def test_execute_update_task_tool(self, session: Session):
        """Test executing update_task tool."""
        with patch("src.services.agent_service.OpenAI"):
            user = create_test_user(session, email="eve@test.com")
            service = AgentService(session, openai_api_key="test-key")

            # Add task
            add_result = service._execute_tool_call(
                user_id=user.id,
                tool_name="add_task",
                tool_args={"title": "Original"},
            )
            task_id = add_result["task"]["id"]

            # Update task
            result = service._execute_tool_call(
                user_id=user.id,
                tool_name="update_task",
                tool_args={"task_id": task_id, "title": "Updated"},
            )

            assert result["success"] is True
            assert result["task"]["title"] == "Updated"

    def test_execute_unknown_tool(self, session: Session):
        """Test executing unknown tool returns error."""
        with patch("src.services.agent_service.OpenAI"):
            user = create_test_user(session, email="frank@test.com")
            service = AgentService(session, openai_api_key="test-key")

            result = service._execute_tool_call(
                user_id=user.id,
                tool_name="unknown_tool",
                tool_args={},
            )

            assert result["success"] is False
            assert "unknown" in result["error"].lower()

    def test_tool_call_adds_user_id_if_missing(self, session: Session):
        """Test that user_id is added to tool args if not provided."""
        with patch("src.services.agent_service.OpenAI"):
            user = create_test_user(session, email="grace@test.com")
            service = AgentService(session, openai_api_key="test-key")

            # Call without user_id in args (should be added by service)
            result = service._execute_tool_call(
                user_id=user.id,
                tool_name="add_task",
                tool_args={"title": "Task"},
            )

            assert result["success"] is True


class TestAgentProcessUserMessage:
    """Test agent message processing."""

    @patch("src.services.agent_service.OpenAI")
    def test_process_user_message_simple_response(
        self, mock_openai_class, session: Session
    ):
        """Test processing user message with simple text response."""
        user = create_test_user(session, email="henry@test.com")

        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "I'll help you with that."
        mock_response.choices[0].message.tool_calls = None
        mock_response.choices[0].finish_reason = "stop"

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        service = AgentService(session, openai_api_key="test-key")

        result = service.process_user_message(
            user_id=user.id,
            user_message="Show me my tasks",
            conversation_history=[],
        )

        assert result["success"] is True
        assert result["assistant_message"] == "I'll help you with that."
        assert result["finish_reason"] == "stop"
        assert result["tool_calls"] == []

    @patch("src.services.agent_service.OpenAI")
    def test_process_user_message_with_tool_calls(
        self, mock_openai_class, session: Session
    ):
        """Test processing user message with tool calls."""
        user = create_test_user(session, email="iris@test.com")

        # Mock tool call in response
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_123"
        mock_tool_call.function.name = "add_task"
        mock_tool_call.function.arguments = '{"title": "Buy milk"}'

        mock_response = MagicMock()
        mock_response.choices[0].message.content = "I'll add that task for you."
        mock_response.choices[0].message.tool_calls = [mock_tool_call]
        mock_response.choices[0].finish_reason = "tool_calls"

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        service = AgentService(session, openai_api_key="test-key")

        result = service.process_user_message(
            user_id=user.id,
            user_message="Add a task: buy milk",
            conversation_history=[],
        )

        assert result["success"] is True
        assert len(result["tool_calls"]) == 1
        assert result["tool_calls"][0]["name"] == "add_task"

    @patch("src.services.agent_service.OpenAI")
    def test_process_user_message_with_conversation_history(
        self, mock_openai_class, session: Session
    ):
        """Test processing message includes conversation history."""
        user = create_test_user(session, email="jack@test.com")

        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Got it!"
        mock_response.choices[0].message.tool_calls = None
        mock_response.choices[0].finish_reason = "stop"

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        service = AgentService(session, openai_api_key="test-key")

        # Include conversation history
        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]

        result = service.process_user_message(
            user_id=user.id,
            user_message="How are you?",
            conversation_history=history,
        )

        # Verify API was called with history
        assert result["success"] is True
        call_args = mock_client.chat.completions.create.call_args
        messages = call_args.kwargs["messages"]
        assert len(messages) == 3  # 2 history + 1 new message

    @patch("src.services.agent_service.OpenAI")
    def test_process_user_message_api_error_handling(
        self, mock_openai_class, session: Session
    ):
        """Test error handling when OpenAI API fails."""
        user = create_test_user(session, email="karl@test.com")

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai_class.return_value = mock_client

        service = AgentService(session, openai_api_key="test-key")

        result = service.process_user_message(
            user_id=user.id,
            user_message="Add a task",
            conversation_history=[],
        )

        assert result["success"] is False
        assert "failed" in result["error"].lower()


class TestFormatToolCalls:
    """Test tool call formatting for storage."""

    def test_format_tool_calls_for_storage(self, session: Session):
        """Test formatting tool calls for database storage."""
        with patch("src.services.agent_service.OpenAI"):
            service = AgentService(session, openai_api_key="test-key")

            tool_calls = [
                {
                    "id": "call_123",
                    "name": "add_task",
                    "result": {"success": True, "task": {"id": "task-123"}},
                },
            ]

            result = service.format_tool_calls_for_storage(tool_calls)

            assert result is not None
            assert "tool_calls" in result
            assert len(result["tool_calls"]) == 1
            assert result["tool_calls"][0]["id"] == "call_123"

    def test_format_empty_tool_calls(self, session: Session):
        """Test formatting empty tool calls returns None."""
        with patch("src.services.agent_service.OpenAI"):
            service = AgentService(session, openai_api_key="test-key")

            result = service.format_tool_calls_for_storage([])

            assert result is None

    def test_format_none_tool_calls(self, session: Session):
        """Test formatting None tool calls returns None."""
        with patch("src.services.agent_service.OpenAI"):
            service = AgentService(session, openai_api_key="test-key")

            result = service.format_tool_calls_for_storage(None)

            assert result is None


class TestSystemPrompt:
    """Test agent system prompt."""

    def test_system_prompt_exists(self, session: Session):
        """Test that agent has a system prompt."""
        with patch("src.services.agent_service.OpenAI"):
            service = AgentService(session, openai_api_key="test-key")

            assert service.system_prompt is not None
            assert len(service.system_prompt) > 0
            assert "task" in service.system_prompt.lower()

    def test_system_prompt_mentions_tools(self, session: Session):
        """Test that system prompt mentions available tools."""
        with patch("src.services.agent_service.OpenAI"):
            service = AgentService(session, openai_api_key="test-key")

            prompt = service.system_prompt
            assert "add" in prompt.lower() or "create" in prompt.lower()
            assert "list" in prompt.lower()
