"""
Add Task - MCP Tool

Create a new task for the authenticated user.

MCP tool that creates a new task with automatic timestamp generation
and UUID assignment. Task is created with 'pending' status.
"""

from datetime import datetime
from typing import Any

from mcp.types import Tool
from sqlmodel import Session

from src.models.task import TaskCreate
from src.services.task_service import TaskService


def get_tool_definition() -> Tool:
    """
    Return JSON Schema definition for add_task MCP tool.

    Returns:
        Tool: MCP tool definition with name, description, and input schema
    """
    return Tool(
        name="add_task",
        description=(
            "Create a new task. Returns task_id, title, and status. "
            "Task is created with 'pending' status."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "format": "uuid",
                    "description": "UUID of the user creating the task. Must match authenticated user.",
                },
                "title": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 200,
                    "description": "Task title (required). Examples: 'Buy groceries', 'Fix bug in dashboard'",
                },
                "description": {
                    "type": "string",
                    "maxLength": 2000,
                    "description": (
                        "Optional task description. Examples: 'milk, eggs, bread', "
                        "'authentication module'. Default: null"
                    ),
                },
            },
            "required": ["user_id", "title"],
            "additionalProperties": False,
        },
    )


async def execute_tool(arguments: dict[str, Any], session: Session) -> dict[str, Any]:
    """
    Execute add_task tool logic.

    Creates a new task owned by the authenticated user with automatic
    timestamp generation and UUID assignment.

    Args:
        arguments: Tool arguments containing user_id, title, and optional description
        session: SQLModel database session

    Returns:
        Dictionary containing:
        - task_id (str): UUID of created task
        - title (str): Task title as stored
        - description (str | None): Task description as stored
        - status (str): Always "pending" for new tasks
        - created_at (str): ISO8601 timestamp when task was created

    Raises:
        ValueError: If validation fails (empty title, title too long)
        HTTPException: If authorization fails (403) or other server errors (500)

    Example:
        result = await execute_tool(
            {"user_id": "550e8400-...", "title": "Buy groceries", "description": "milk, eggs"},
            session
        )
        # Returns: {
        #     "task_id": "660e8400-...",
        #     "title": "Buy groceries",
        #     "description": "milk, eggs",
        #     "status": "pending",
        #     "created_at": "2025-12-13T10:30:00Z"
        # }
    """
    # Extract arguments
    user_id: str = arguments["user_id"]
    title: str = arguments["title"]
    description: str | None = arguments.get("description")

    # Create task data model
    task_data = TaskCreate(title=title, description=description)

    # Initialize service and create task
    task_service = TaskService(session=session)
    task = await task_service.create_task(task_data, user_id)

    # Format response according to MCP contract
    return {
        "task_id": task.id,
        "title": task.title,
        "description": task.description,
        "status": "pending",  # Always pending for new tasks
        "created_at": task.created_at.isoformat() if task.created_at else datetime.utcnow().isoformat(),
    }
