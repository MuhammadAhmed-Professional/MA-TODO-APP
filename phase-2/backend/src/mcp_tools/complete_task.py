"""
Complete Task - MCP Tool

Mark a task as completed for the authenticated user.

MCP tool that marks a task as complete by setting is_complete to True.
Returns success status with human-readable message.
"""

from typing import Any

from fastapi import HTTPException
from mcp.types import Tool
from sqlmodel import Session

from src.services.task_service import TaskService


def get_tool_definition() -> Tool:
    """
    Return JSON Schema definition for complete_task MCP tool.

    Returns:
        Tool: MCP tool definition with name, description, and input schema
    """
    return Tool(
        name="complete_task",
        description="Mark a task as completed. Changes status from 'pending' to 'completed'.",
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
                    "description": "UUID of the task to mark complete",
                },
            },
            "required": ["user_id", "task_id"],
            "additionalProperties": False,
        },
    )


async def execute_tool(arguments: dict[str, Any], session: Session) -> dict[str, Any]:
    """
    Execute complete_task tool logic.

    Marks a task as completed by setting is_complete to True.
    Handles the case where task is already complete gracefully.

    Args:
        arguments: Tool arguments containing user_id and task_id
        session: SQLModel database session

    Returns:
        Dictionary containing:
        - success (bool): Whether operation succeeded
        - message (str): Human-readable message indicating result
        - task_id (str): ID of completed task

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
        #     "message": "'Buy groceries' is now marked complete",
        #     "task_id": "660e8400-..."
        # }
    """
    # Extract arguments
    user_id: str = arguments["user_id"]
    task_id: str = arguments["task_id"]

    # Initialize service
    task_service = TaskService(session=session)

    # Check if task exists and get ownership verification
    try:
        task = await task_service.get_task(task_id, user_id)
    except HTTPException as e:
        # Preserve HTTP status codes from service
        raise

    # Check if already complete
    if task.is_complete:
        return {
            "success": False,
            "message": f"'{task.title}' is already marked complete",
            "task_id": task_id,
        }

    # Mark as complete
    updated_task = await task_service.toggle_complete(task_id, True, user_id)

    return {
        "success": True,
        "message": f"'{updated_task.title}' is now marked complete",
        "task_id": task_id,
    }
