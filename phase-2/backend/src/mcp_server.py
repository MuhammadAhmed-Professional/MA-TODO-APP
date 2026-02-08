"""
MCP Server for Todo App

Model Context Protocol (MCP) server implementation using the official MCP Python SDK.
Exposes 5 task management tools (add_task, list_tasks, complete_task, delete_task,
update_task) via stdio transport for local development.

This server integrates with the existing mcp_tools module, which provides:
- Tool definitions (JSON Schema for input validation)
- Tool execution logic (calling TaskService for database operations)

Usage:
    # Run as standalone process
    uv run python -m src.mcp_server

    # Or directly
    uv run uvicorn src.mcp_server:app

Environment Variables:
    DATABASE_URL: PostgreSQL connection string (required)

Resources:
    - MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
    - Tool definitions: src/mcp_tools/
    - Task service: src/services/task_service.py
"""

import asyncio
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.models import InitializationOptions
from mcp.types import Tool
from sqlmodel import Session

from src.db.session import get_session_context
from src.mcp_tools import (
    get_tool_definitions,
    execute_tool,
    ADD_TASK,
    LIST_TASKS,
    COMPLETE_TASK,
    DELETE_TASK,
    UPDATE_TASK,
)

# Server metadata
SERVER_NAME = "todo-app-mcp-server"
SERVER_VERSION = "0.1.0"

# Create MCP server instance
app = Server(SERVER_NAME)


@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """
    List all available MCP tools.

    Returns tool definitions for all 5 task management operations.
    Each tool includes:
    - name: Tool identifier (e.g., "add_task")
    - description: Human-readable tool description
    - inputSchema: JSON Schema for argument validation

    Returns:
        list[Tool]: List of MCP tool definitions
    """
    return get_tool_definitions()


@app.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """
    Execute an MCP tool by name.

    Dispatches tool calls to the appropriate execute function from mcp_tools.
    All tools require a database session for database operations.

    Args:
        name: Tool name (add_task, list_tasks, complete_task, delete_task, update_task)
        arguments: Tool arguments matching the tool's JSON Schema

    Returns:
        dict[str, Any]: Tool execution result (structure varies by tool)

    Raises:
        ValueError: If tool name is not recognized
        Exception: For database or service layer errors

    Examples:
        # Add a task
        await handle_call_tool("add_task", {
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "title": "Buy groceries",
            "description": "milk, eggs, bread"
        })
        # Returns: {"task_id": "...", "title": "Buy groceries", ...}

        # List tasks
        await handle_call_tool("list_tasks", {
            "user_id": "550e8400-e29b-41d4-a716-446655440000"
        })
        # Returns: {"tasks": [...], "total": 5}
    """
    # Validate tool name
    valid_tools = {ADD_TASK, LIST_TASKS, COMPLETE_TASK, DELETE_TASK, UPDATE_TASK}
    if name not in valid_tools:
        available = ", ".join(sorted(valid_tools))
        raise ValueError(
            f"Unknown tool: {name}. Available tools: {available}"
        )

    # Get database session
    with get_session_context() as session:
        # Execute tool with database session
        result = await execute_tool(name, arguments, session)
        return result


async def main() -> None:
    """
    Run the MCP server with stdio transport.

    This is the entry point for running the server as a standalone process.
    The server communicates via stdin/stdout using the MCP protocol.

    Usage:
        uv run python -m src.mcp_server
    """
    # Run server with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=SERVER_NAME,
                server_version=SERVER_VERSION,
                capabilities=app.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    # Run the server
    asyncio.run(main())


__all__ = [
    "app",
    "main",
    "SERVER_NAME",
    "SERVER_VERSION",
]
