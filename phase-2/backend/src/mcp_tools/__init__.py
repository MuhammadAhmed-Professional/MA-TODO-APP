"""
MCP Tools Module

Model Context Protocol (MCP) tools for Phase III AI chatbot.
Provides task management capabilities via the official MCP SDK format.

This module exports all MCP tool definitions and execute functions for
integration with the chatbot agent layer.

Usage:
    from src.mcp_tools import (
        get_tool_definitions,
        execute_tool,
        ADD_TASK,
        LIST_TASKS,
        COMPLETE_TASK,
        DELETE_TASK,
        UPDATE_TASK,
    )

    # Get all tool definitions for MCP registration
    tools = get_tool_definitions()

    # Execute a tool by name
    result = await execute_tool("add_task", {"user_id": "...", "title": "Buy groceries"}, session)
"""

from mcp.types import Tool
from sqlmodel import Session

from src.mcp_tools.add_task import get_tool_definition as add_task_def
from src.mcp_tools.add_task import execute_tool as add_task_exec
from src.mcp_tools.complete_task import get_tool_definition as complete_task_def
from src.mcp_tools.complete_task import execute_tool as complete_task_exec
from src.mcp_tools.delete_task import get_tool_definition as delete_task_def
from src.mcp_tools.delete_task import execute_tool as delete_task_exec
from src.mcp_tools.list_tasks import get_tool_definition as list_tasks_def
from src.mcp_tools.list_tasks import execute_tool as list_tasks_exec
from src.mcp_tools.update_task import get_tool_definition as update_task_def
from src.mcp_tools.update_task import execute_tool as update_task_exec

# Tool name constants
ADD_TASK = "add_task"
LIST_TASKS = "list_tasks"
COMPLETE_TASK = "complete_task"
DELETE_TASK = "delete_task"
UPDATE_TASK = "update_task"

# Tool registry mapping names to their definitions and execute functions
_TOOL_REGISTRY: dict[str, tuple[Tool, callable]] = {
    ADD_TASK: (add_task_def(), add_task_exec),
    LIST_TASKS: (list_tasks_def(), list_tasks_exec),
    COMPLETE_TASK: (complete_task_def(), complete_task_exec),
    DELETE_TASK: (delete_task_def(), delete_task_exec),
    UPDATE_TASK: (update_task_def(), update_task_exec),
}


def get_tool_definitions() -> list[Tool]:
    """
    Get all MCP tool definitions.

    Returns a list of Tool objects containing the JSON Schema definitions
    for all 5 task management tools. Use this to register tools with the
    MCP server or agent framework.

    Returns:
        list[Tool]: List of MCP tool definitions

    Example:
        tools = get_tool_definitions()
        for tool in tools:
            print(f"{tool.name}: {tool.description}")
    """
    return [definition for definition, _ in _TOOL_REGISTRY.values()]


def get_tool_definition(tool_name: str) -> Tool | None:
    """
    Get a specific tool definition by name.

    Args:
        tool_name: Name of the tool (add_task, list_tasks, etc.)

    Returns:
        Tool object if found, None otherwise

    Example:
        tool_def = get_tool_definition("add_task")
        if tool_def:
            print(tool_def.inputSchema)
    """
    if tool_name in _TOOL_REGISTRY:
        definition, _ = _TOOL_REGISTRY[tool_name]
        return definition
    return None


async def execute_tool(tool_name: str, arguments: dict, session: Session) -> dict:
    """
    Execute an MCP tool by name.

    Dispatches to the appropriate tool's execute function based on the tool name.
    All tools require a database session for database operations.

    Args:
        tool_name: Name of the tool to execute
        arguments: Tool arguments as defined in the tool's JSON Schema
        session: SQLModel database session

    Returns:
        Dictionary with the tool's result (structure varies by tool)

    Raises:
        ValueError: If tool_name is not recognized
        HTTPException: For 404/403 errors from service layer
        Exception: For other server errors

    Example:
        result = await execute_tool(
            "add_task",
            {"user_id": "550e8400-...", "title": "Buy groceries"},
            session
        )
        print(result)  # {"task_id": "...", "title": "Buy groceries", ...}
    """
    if tool_name not in _TOOL_REGISTRY:
        available = ", ".join(_TOOL_REGISTRY.keys())
        raise ValueError(
            f"Unknown tool: {tool_name}. Available tools: {available}"
        )

    _, execute_func = _TOOL_REGISTRY[tool_name]
    return await execute_func(arguments, session)


__all__ = [
    # Tool name constants
    "ADD_TASK",
    "LIST_TASKS",
    "COMPLETE_TASK",
    "DELETE_TASK",
    "UPDATE_TASK",
    # Public API
    "get_tool_definitions",
    "get_tool_definition",
    "execute_tool",
    # Individual tool imports (for direct access)
    "add_task_def",
    "add_task_exec",
    "list_tasks_def",
    "list_tasks_exec",
    "complete_task_def",
    "complete_task_exec",
    "delete_task_def",
    "delete_task_exec",
    "update_task_def",
    "update_task_exec",
]
