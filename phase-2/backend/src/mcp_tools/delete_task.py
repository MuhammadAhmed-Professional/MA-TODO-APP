"""
Delete Task - MCP Tool

Delete a task permanently for the authenticated user.

MCP tool that permanently removes a task from the database.
This operation cannot be undone.
"""

from typing import Any

from fastapi import HTTPException
from mcp.types import Tool
from sqlmodel import Session

from src.services.task_service import TaskService


def get_tool_definition() -> Tool:
    """
    Return JSON Schema definition for delete_task MCP tool.

    Returns:
        Tool: MCP tool definition with name, description, and input schema
    """
    return Tool(
        name="delete_task",
        description="Delete a task permanently. This is irreversible.",
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
                    "description": "UUID of the task to delete",
                },
            },
            "required": ["user_id", "task_id"],
            "additionalProperties": False,
        },
    )


async def execute_tool(arguments: dict[str, Any], session: Session) -> dict[str, Any]:
    """
    Execute delete_task tool logic.

    Permanently removes the task from the database.
    This operation cannot be undone.

    Note: The agent layer should ask for user confirmation before
    calling this tool. This is not enforced at the tool level.

    Args:
        arguments: Tool arguments containing user_id and task_id
        session: SQLModel database session

    Returns:
        Dictionary containing:
        - success (bool): Whether operation succeeded (always True if no exception)
        - message (str): Human-readable message with task title
        - task_id (str): ID of deleted task

    Raises:
        HTTPException: If task not found (404), authorization fails (403),
                       or other server errors (500)

    Example:
        result = await execute_tool(
            {"user_id": "550e8400-...", "task_id": "660e8400-..."},
            session
        )
        # Returns: {
        #     "success": True,
        #     "message": "'Fix bug in dashboard' has been deleted",
        #     "task_id": "660e8400-..."
        # }
    """
    # Extract arguments
    user_id: str = arguments["user_id"]
    task_id: str = arguments["task_id"]

    # Initialize service
    task_service = TaskService(session=session)

    # Get task title for message (before deletion)
    try:
        task = await task_service.get_task(task_id, user_id)
        task_title = task.title
    except HTTPException as e:
        # Preserve HTTP status codes from service
        raise

    # Delete the task
    await task_service.delete_task(task_id, user_id)

    return {
        "success": True,
        "message": f"'{task_title}' has been deleted",
        "task_id": task_id,
    }
