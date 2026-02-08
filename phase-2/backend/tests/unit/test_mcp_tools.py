"""
Unit Tests for MCP Tools Service

Tests the Model Context Protocol tools for task management.
"""

import uuid

import pytest
from sqlmodel import Session

from src.models.task import Task
from src.services.mcp_tools import MCPToolsService, MCP_TOOLS
from tests.conftest import create_test_user


class TestAddTask:
    """Test add_task MCP tool."""

    def test_add_task_success(self, session: Session):
        """Test successfully adding a new task."""
        user = create_test_user(session, email="alice@test.com")
        service = MCPToolsService(session)

        result = service.add_task(
            user_id=user.id,
            title="Complete project documentation",
            description="Write comprehensive README and API docs",
        )

        assert result["success"] is True
        assert result["task"]["title"] == "Complete project documentation"
        assert result["task"]["description"] == "Write comprehensive README and API docs"
        assert result["task"]["is_complete"] is False

    def test_add_task_without_description(self, session: Session):
        """Test adding task without description (optional)."""
        user = create_test_user(session, email="bob@test.com")
        service = MCPToolsService(session)

        result = service.add_task(user_id=user.id, title="Buy groceries")

        assert result["success"] is True
        assert result["task"]["title"] == "Buy groceries"
        assert result["task"]["description"] is None

    def test_add_task_empty_title(self, session: Session):
        """Test adding task with empty title fails."""
        user = create_test_user(session, email="charlie@test.com")
        service = MCPToolsService(session)

        result = service.add_task(user_id=user.id, title="")

        assert result["success"] is False
        assert "empty" in result["error"].lower()

    def test_add_task_title_too_long(self, session: Session):
        """Test adding task with title > 200 chars fails."""
        user = create_test_user(session, email="dave@test.com")
        service = MCPToolsService(session)

        long_title = "a" * 201

        result = service.add_task(user_id=user.id, title=long_title)

        assert result["success"] is False
        assert "200" in result["error"]

    def test_add_task_description_too_long(self, session: Session):
        """Test adding task with description > 2000 chars fails."""
        user = create_test_user(session, email="eve@test.com")
        service = MCPToolsService(session)

        long_desc = "a" * 2001

        result = service.add_task(
            user_id=user.id,
            title="Task",
            description=long_desc,
        )

        assert result["success"] is False
        assert "2000" in result["error"]

    def test_add_task_whitespace_stripped(self, session: Session):
        """Test title and description whitespace is stripped."""
        user = create_test_user(session, email="frank@test.com")
        service = MCPToolsService(session)

        result = service.add_task(
            user_id=user.id,
            title="  My Task  ",
            description="  Task description  ",
        )

        assert result["success"] is True
        assert result["task"]["title"] == "My Task"
        assert result["task"]["description"] == "Task description"


class TestListTasks:
    """Test list_tasks MCP tool."""

    def test_list_all_tasks(self, session: Session):
        """Test listing all tasks for a user."""
        user = create_test_user(session, email="grace@test.com")
        service = MCPToolsService(session)

        # Add tasks
        service.add_task(user_id=user.id, title="Task 1")
        service.add_task(user_id=user.id, title="Task 2")
        service.add_task(user_id=user.id, title="Task 3")

        result = service.list_tasks(user_id=user.id)

        assert result["success"] is True
        assert result["total"] == 3
        assert len(result["tasks"]) == 3

    def test_list_tasks_filter_incomplete(self, session: Session):
        """Test filtering tasks by incomplete status."""
        user = create_test_user(session, email="henry@test.com")
        service = MCPToolsService(session)

        # Add and complete one task
        add_result = service.add_task(user_id=user.id, title="Task 1")
        task_id = uuid.UUID(add_result["task"]["id"])

        service.add_task(user_id=user.id, title="Task 2")
        service.complete_task(user_id=user.id, task_id=task_id)

        # Get incomplete tasks
        result = service.list_tasks(user_id=user.id, is_complete=False)

        assert result["success"] is True
        assert result["total"] == 1
        assert result["tasks"][0]["title"] == "Task 2"

    def test_list_tasks_filter_complete(self, session: Session):
        """Test filtering tasks by complete status."""
        user = create_test_user(session, email="iris@test.com")
        service = MCPToolsService(session)

        # Add and complete tasks
        add_result = service.add_task(user_id=user.id, title="Task 1")
        task_id = uuid.UUID(add_result["task"]["id"])
        service.add_task(user_id=user.id, title="Task 2")
        service.complete_task(user_id=user.id, task_id=task_id)

        # Get completed tasks
        result = service.list_tasks(user_id=user.id, is_complete=True)

        assert result["success"] is True
        assert result["total"] == 1
        assert result["tasks"][0]["title"] == "Task 1"

    def test_list_tasks_pagination(self, session: Session):
        """Test pagination with limit and offset."""
        user = create_test_user(session, email="jack@test.com")
        service = MCPToolsService(session)

        # Add 10 tasks
        for i in range(10):
            service.add_task(user_id=user.id, title=f"Task {i}")

        # Get first 3 tasks
        result = service.list_tasks(user_id=user.id, limit=3, offset=0)
        assert result["total"] == 10
        assert len(result["tasks"]) == 3

        # Get next 3 tasks
        result = service.list_tasks(user_id=user.id, limit=3, offset=3)
        assert len(result["tasks"]) == 3

    def test_list_tasks_empty(self, session: Session):
        """Test listing tasks when user has no tasks."""
        user = create_test_user(session, email="karl@test.com")
        service = MCPToolsService(session)

        result = service.list_tasks(user_id=user.id)

        assert result["success"] is True
        assert result["total"] == 0
        assert len(result["tasks"]) == 0

    def test_list_tasks_different_users(self, session: Session):
        """Test that tasks are isolated by user."""
        user1 = create_test_user(session, email="lisa@test.com")
        user2 = create_test_user(session, email="mike@test.com")
        service = MCPToolsService(session)

        # Add tasks for each user
        service.add_task(user_id=user1.id, title="User 1 Task")
        service.add_task(user_id=user2.id, title="User 2 Task")

        # List for user1
        result = service.list_tasks(user_id=user1.id)

        assert result["total"] == 1
        assert result["tasks"][0]["title"] == "User 1 Task"


class TestCompleteTask:
    """Test complete_task MCP tool."""

    def test_complete_task_success(self, session: Session):
        """Test successfully completing a task."""
        user = create_test_user(session, email="nancy@test.com")
        service = MCPToolsService(session)

        # Add task
        add_result = service.add_task(user_id=user.id, title="Complete task")
        task_id = uuid.UUID(add_result["task"]["id"])

        # Complete task
        result = service.complete_task(user_id=user.id, task_id=task_id)

        assert result["success"] is True
        assert result["task"]["is_complete"] is True

    def test_complete_nonexistent_task(self, session: Session):
        """Test completing nonexistent task fails."""
        user = create_test_user(session, email="oscar@test.com")
        service = MCPToolsService(session)

        fake_task_id = uuid.uuid4()

        result = service.complete_task(user_id=user.id, task_id=fake_task_id)

        assert result["success"] is False
        assert "not found" in result["error"].lower()

    def test_complete_task_unauthorized(self, session: Session):
        """Test completing task owned by another user fails."""
        user1 = create_test_user(session, email="paul@test.com")
        user2 = create_test_user(session, email="quinn@test.com")
        service = MCPToolsService(session)

        # Add task for user1
        add_result = service.add_task(user_id=user1.id, title="User1 task")
        task_id = uuid.UUID(add_result["task"]["id"])

        # Try to complete as user2
        result = service.complete_task(user_id=user2.id, task_id=task_id)

        assert result["success"] is False
        assert "not authorized" in result["error"].lower()


class TestDeleteTask:
    """Test delete_task MCP tool."""

    def test_delete_task_success(self, session: Session):
        """Test successfully deleting a task."""
        user = create_test_user(session, email="rachel@test.com")
        service = MCPToolsService(session)

        # Add task
        add_result = service.add_task(user_id=user.id, title="Delete me")
        task_id = uuid.UUID(add_result["task"]["id"])

        # Delete task
        result = service.delete_task(user_id=user.id, task_id=task_id)

        assert result["success"] is True
        assert "deleted" in result["message"].lower()

        # Verify task is gone
        list_result = service.list_tasks(user_id=user.id)
        assert list_result["total"] == 0

    def test_delete_nonexistent_task(self, session: Session):
        """Test deleting nonexistent task fails."""
        user = create_test_user(session, email="sam@test.com")
        service = MCPToolsService(session)

        fake_task_id = uuid.uuid4()

        result = service.delete_task(user_id=user.id, task_id=fake_task_id)

        assert result["success"] is False
        assert "not found" in result["error"].lower()

    def test_delete_task_unauthorized(self, session: Session):
        """Test deleting task owned by another user fails."""
        user1 = create_test_user(session, email="tina@test.com")
        user2 = create_test_user(session, email="uma@test.com")
        service = MCPToolsService(session)

        # Add task for user1
        add_result = service.add_task(user_id=user1.id, title="User1 task")
        task_id = uuid.UUID(add_result["task"]["id"])

        # Try to delete as user2
        result = service.delete_task(user_id=user2.id, task_id=task_id)

        assert result["success"] is False
        assert "not authorized" in result["error"].lower()


class TestUpdateTask:
    """Test update_task MCP tool."""

    def test_update_task_title(self, session: Session):
        """Test updating task title."""
        user = create_test_user(session, email="victor@test.com")
        service = MCPToolsService(session)

        # Add task
        add_result = service.add_task(user_id=user.id, title="Original Title")
        task_id = uuid.UUID(add_result["task"]["id"])

        # Update title
        result = service.update_task(
            user_id=user.id,
            task_id=task_id,
            title="Updated Title",
        )

        assert result["success"] is True
        assert result["task"]["title"] == "Updated Title"

    def test_update_task_description(self, session: Session):
        """Test updating task description."""
        user = create_test_user(session, email="wendy@test.com")
        service = MCPToolsService(session)

        # Add task
        add_result = service.add_task(user_id=user.id, title="Task")
        task_id = uuid.UUID(add_result["task"]["id"])

        # Update description
        result = service.update_task(
            user_id=user.id,
            task_id=task_id,
            description="New description",
        )

        assert result["success"] is True
        assert result["task"]["description"] == "New description"

    def test_update_task_completion_status(self, session: Session):
        """Test updating task completion status."""
        user = create_test_user(session, email="xavier@test.com")
        service = MCPToolsService(session)

        # Add task
        add_result = service.add_task(user_id=user.id, title="Task")
        task_id = uuid.UUID(add_result["task"]["id"])

        # Mark complete
        result = service.update_task(
            user_id=user.id,
            task_id=task_id,
            is_complete=True,
        )

        assert result["success"] is True
        assert result["task"]["is_complete"] is True

    def test_update_task_all_fields(self, session: Session):
        """Test updating all task fields at once."""
        user = create_test_user(session, email="yara@test.com")
        service = MCPToolsService(session)

        # Add task
        add_result = service.add_task(
            user_id=user.id,
            title="Old Title",
            description="Old description",
        )
        task_id = uuid.UUID(add_result["task"]["id"])

        # Update all fields
        result = service.update_task(
            user_id=user.id,
            task_id=task_id,
            title="New Title",
            description="New description",
            is_complete=True,
        )

        assert result["success"] is True
        assert result["task"]["title"] == "New Title"
        assert result["task"]["description"] == "New description"
        assert result["task"]["is_complete"] is True

    def test_update_task_invalid_title(self, session: Session):
        """Test updating with invalid title fails."""
        user = create_test_user(session, email="zoe@test.com")
        service = MCPToolsService(session)

        # Add task
        add_result = service.add_task(user_id=user.id, title="Task")
        task_id = uuid.UUID(add_result["task"]["id"])

        # Try to update with empty title
        result = service.update_task(
            user_id=user.id,
            task_id=task_id,
            title="",
        )

        assert result["success"] is False
        assert "empty" in result["error"].lower()

    def test_update_nonexistent_task(self, session: Session):
        """Test updating nonexistent task fails."""
        user = create_test_user(session, email="alex@test.com")
        service = MCPToolsService(session)

        fake_task_id = uuid.uuid4()

        result = service.update_task(
            user_id=user.id,
            task_id=fake_task_id,
            title="New Title",
        )

        assert result["success"] is False
        assert "not found" in result["error"].lower()

    def test_update_task_unauthorized(self, session: Session):
        """Test updating task owned by another user fails."""
        user1 = create_test_user(session, email="anna@test.com")
        user2 = create_test_user(session, email="brad@test.com")
        service = MCPToolsService(session)

        # Add task for user1
        add_result = service.add_task(user_id=user1.id, title="User1 task")
        task_id = uuid.UUID(add_result["task"]["id"])

        # Try to update as user2
        result = service.update_task(
            user_id=user2.id,
            task_id=task_id,
            title="Hacked",
        )

        assert result["success"] is False
        assert "not authorized" in result["error"].lower()


class TestMCPToolSchemas:
    """Test MCP tool schema definitions."""

    def test_mcp_tools_defined(self):
        """Test that all 5 MCP tools are defined."""
        assert len(MCP_TOOLS) == 5

        tool_names = [tool["function"]["name"] for tool in MCP_TOOLS]
        expected_names = ["add_task", "list_tasks", "complete_task", "delete_task", "update_task"]

        for name in expected_names:
            assert name in tool_names

    def test_mcp_tool_schema_structure(self):
        """Test that each MCP tool has required schema fields."""
        for tool in MCP_TOOLS:
            assert tool["type"] == "function"
            assert "function" in tool
            assert "name" in tool["function"]
            assert "description" in tool["function"]
            assert "parameters" in tool["function"]

            # Check parameters structure
            params = tool["function"]["parameters"]
            assert params["type"] == "object"
            assert "properties" in params
            assert "required" in params

    def test_add_task_schema(self):
        """Test add_task tool schema is correct."""
        add_task = next(t for t in MCP_TOOLS if t["function"]["name"] == "add_task")

        assert "user_id" in add_task["function"]["parameters"]["properties"]
        assert "title" in add_task["function"]["parameters"]["properties"]
        assert "description" in add_task["function"]["parameters"]["properties"]
        assert "user_id" in add_task["function"]["parameters"]["required"]
        assert "title" in add_task["function"]["parameters"]["required"]

    def test_list_tasks_schema(self):
        """Test list_tasks tool schema is correct."""
        list_tasks = next(t for t in MCP_TOOLS if t["function"]["name"] == "list_tasks")

        params = list_tasks["function"]["parameters"]["properties"]
        assert "user_id" in params
        assert "is_complete" in params
        assert "limit" in params
        assert "offset" in params
        assert "user_id" in list_tasks["function"]["parameters"]["required"]

    def test_complete_task_schema(self):
        """Test complete_task tool schema is correct."""
        complete_task = next(t for t in MCP_TOOLS if t["function"]["name"] == "complete_task")

        params = complete_task["function"]["parameters"]["properties"]
        assert "user_id" in params
        assert "task_id" in params
        required = complete_task["function"]["parameters"]["required"]
        assert "user_id" in required
        assert "task_id" in required

    def test_delete_task_schema(self):
        """Test delete_task tool schema is correct."""
        delete_task = next(t for t in MCP_TOOLS if t["function"]["name"] == "delete_task")

        params = delete_task["function"]["parameters"]["properties"]
        assert "user_id" in params
        assert "task_id" in params
        required = delete_task["function"]["parameters"]["required"]
        assert "user_id" in required
        assert "task_id" in required

    def test_update_task_schema(self):
        """Test update_task tool schema is correct."""
        update_task = next(t for t in MCP_TOOLS if t["function"]["name"] == "update_task")

        params = update_task["function"]["parameters"]["properties"]
        assert "user_id" in params
        assert "task_id" in params
        assert "title" in params
        assert "description" in params
        assert "is_complete" in params
        required = update_task["function"]["parameters"]["required"]
        assert "user_id" in required
        assert "task_id" in required
