"""
Update Task - MCP Tool

Update task title and/or description for the authenticated user.

MCP tool that performs partial update of task properties.
Only fields provided in the arguments are updated.
"""

from datetime import datetime
from typing import Any

from fastapi import HTTPException
from mcp.types import Tool
from sqlmodel import Session

from src.models.task import TaskUpdate
from src.services.task_service import TaskService


def get_tool_definition() -> Tool:
    """
    Return JSON Schema definition for update_task MCP tool.

    Returns:
        Tool: MCP tool definition with name, description, and input schema
    """
    return Tool(
        name="update_task",
        description=(
            "Update task title and/or description. At least one field must be provided."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "format": "uuid",
                    "description": "UUID of the task owner. Must match authenticated user.",
                },
                "task_id": {
                    "type": "string",
                    "format": "uuid",
                    "description": "UUID of the task to update",
                },
                "title": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 200,
                    "description": "New task title (optional). If provided, replaces current title.",
                },
                "description": {
                    "type": "string",
                    "maxLength": 2000,
                    "description": (
                        "New task description (optional). If provided, replaces current description."
                    ),
                },
            },
            "required": ["user_id", "task_id"],
            "additionalProperties": False,
        },
    )


async def execute_tool(arguments: dict[str, Any], session: Session) -> dict[str, Any]:
    """
    Execute update_task tool logic.

    Performs partial update of task properties. Only fields provided in the
    arguments are updated. The updated_at timestamp is automatically set
    to the current UTC time.

    Args:
        arguments: Tool arguments containing user_id, task_id, and optional title/description
        session: SQLModel database session

    Returns:
        Dictionary containing:
        - task_id (str): UUID of updated task
        - title (str): Updated task title
        - description (str | None): Updated task description
        - status (str): Task status (unchanged)
        - updated_at (str): ISO8601 timestamp of update

    Raises:
        ValueError: If no fields provided or validation fails
        HTTPException: If task not found (404), authorization fails (403),
                       or other server errors (500)

    Example:
        result = await execute_tool(
            {"user_id": "550e8400-...", "task_id": "660e8400-...", "title": "New title"},
            session
        )
        # Returns: {
        #     "task_id": "660e8400-...",
        #     "title": "New title",
        #     "description": "milk, eggs",
        #     "status": "pending",
        #     "updated_at": "2025-12-13T10:35:00Z"
        # }
    """
    # Extract arguments
    user_id: str = arguments["user_id"]
    task_id: str = arguments["task_id"]
    title: str | None = arguments.get("title")
    description: str | None = arguments.get("description")

    # Validate at least one field is provided
    if title is None and description is None:
        raise ValueError("Provide at least one field to update (title or description)")

    # Create task update data
    task_data = TaskUpdate(title=title, description=description)

    # Initialize service
    task_service = TaskService(session=session)

    # Update task
    try:
        updated_task = await task_service.update_task(task_id, task_data, user_id)
    except ValueError as e:
        # Preserve validation errors
        raise
    except HTTPException as e:
        # Preserve HTTP status codes from service
        raise

    # Format response according to MCP contract
    return {
        "task_id": updated_task.id,
        "title": updated_task.title,
        "description": updated_task.description,
        "status": "completed" if updated_task.is_complete else "pending",
        "updated_at": updated_task.updated_at.isoformat() if updated_task.updated_at else datetime.utcnow().isoformat(),
    }
