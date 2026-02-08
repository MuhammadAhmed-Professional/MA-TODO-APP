"""
List Tasks - MCP Tool

Retrieve tasks with optional status filter for the authenticated user.

MCP tool that retrieves all tasks or filtered by completion status.
Returns array of tasks with count.
"""

from datetime import datetime
from typing import Any

from mcp.types import Tool
from sqlmodel import Session

from src.services.task_service import TaskService


def get_tool_definition() -> Tool:
    """
    Return JSON Schema definition for list_tasks MCP tool.

    Returns:
        Tool: MCP tool definition with name, description, and input schema
    """
    return Tool(
        name="list_tasks",
        description=(
            "Retrieve tasks with optional status filter. Returns array of tasks for the user."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "format": "uuid",
                    "description": "UUID of the user retrieving tasks. Must match authenticated user.",
                },
                "status": {
                    "type": "string",
                    "enum": ["all", "pending", "completed"],
                    "description": (
                        "Filter tasks by status. Default: 'all'. "
                        "Options: 'all'=all tasks, 'pending'=incomplete, 'completed'=done"
                    ),
                },
            },
            "required": ["user_id"],
            "additionalProperties": False,
        },
    )


async def execute_tool(arguments: dict[str, Any], session: Session) -> dict[str, Any]:
    """
    Execute list_tasks tool logic.

    Retrieves tasks for the user with optional status filtering.
    Tasks are returned sorted by creation date (newest first).

    Args:
        arguments: Tool arguments containing user_id and optional status
        session: SQLModel database session

    Returns:
        Dictionary containing:
        - tasks (list): Array of task objects with id, title, description, status, created_at
        - count (int): Total number of tasks returned

    Raises:
        HTTPException: If authorization fails (403) or other server errors (500)

    Example:
        result = await execute_tool(
            {"user_id": "550e8400-...", "status": "pending"},
            session
        )
        # Returns: {
        #     "tasks": [
        #         {
        #             "id": "660e8400-...",
        #             "title": "Buy groceries",
        #             "description": "milk, eggs",
        #             "status": "pending",
        #             "created_at": "2025-12-13T10:30:00Z"
        #         }
        #     ],
        #     "count": 1
        # }
    """
    # Extract arguments
    user_id: str = arguments["user_id"]
    status_filter: str = arguments.get("status", "all")

    # Map status string to is_complete boolean filter
    is_complete_filter: bool | None = None
    if status_filter == "pending":
        is_complete_filter = False
    elif status_filter == "completed":
        is_complete_filter = True
    # else: "all" → None (no filter)

    # Initialize service and get tasks
    task_service = TaskService(session=session)
    tasks = await task_service.get_user_tasks(
        user_id=user_id,
        is_complete=is_complete_filter,
        limit=100,  # MCP tools have higher limit than API
        offset=0,
    )

    # Format tasks for MCP response
    formatted_tasks = []
    for task in tasks:
        formatted_tasks.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": "completed" if task.is_complete else "pending",
            "created_at": task.created_at.isoformat() if task.created_at else datetime.utcnow().isoformat(),
        })

    # Return response with count
    return {
        "tasks": formatted_tasks,
        "count": len(formatted_tasks),
    }
