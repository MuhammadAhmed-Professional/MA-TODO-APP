"""
MCP Tools Service for Todo App

Implements the Model Context Protocol (MCP) tools for managing tasks.
These are stateless tools that query the database directly.
Used by the OpenAI Agent to manage tasks via natural language.
"""

import json
import uuid
from typing import Any, Optional

from sqlalchemy import func
from sqlmodel import Session, select

from src.models.task import Task


class MCPToolsService:
    """Service providing MCP-compatible tools for task management."""

    def __init__(self, session: Session):
        """Initialize MCP tools service with database session."""
        self.session = session

    def add_task(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Add a new task for the user.

        Args:
            user_id: ID of the task owner (Better Auth string ID)
            title: Task title (1-200 characters)
            description: Optional task description (max 2000 characters)

        Returns:
            Dictionary containing created task details with success status

        Raises:
            ValueError: If title is empty or too long
        """
        # Validate inputs
        if not title or not title.strip():
            return {
                "success": False,
                "error": "Title cannot be empty",
            }

        if len(title) > 200:
            return {
                "success": False,
                "error": "Title must be 200 characters or less",
            }

        if description and len(description) > 2000:
            return {
                "success": False,
                "error": "Description must be 2000 characters or less",
            }

        try:
            # Create task
            task = Task(
                id=uuid.uuid4(),
                user_id=user_id,
                title=title.strip(),
                description=description.strip() if description else None,
                is_complete=False,
            )

            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)

            return {
                "success": True,
                "task": {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "is_complete": task.is_complete,
                    "created_at": task.created_at.isoformat(),
                },
            }
        except Exception as e:
            self.session.rollback()
            return {
                "success": False,
                "error": f"Failed to create task: {str(e)}",
            }

    def list_tasks(
        self,
        user_id: str,
        is_complete: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        """
        List tasks for the user with optional filtering.

        Args:
            user_id: UUID of the user
            is_complete: Optional filter for completion status (True/False/None for all)
            limit: Maximum number of tasks to return (1-100, default 50)
            offset: Number of tasks to skip (default 0)

        Returns:
            Dictionary containing list of tasks and metadata
        """
        try:
            # Build query
            query = select(Task).where(Task.user_id == user_id)

            # Apply completion filter
            if is_complete is not None:
                query = query.where(Task.is_complete == is_complete)

            # Get total count
            count_query = select(func.count(Task.id)).where(Task.user_id == user_id)
            if is_complete is not None:
                count_query = count_query.where(Task.is_complete == is_complete)
            total = self.session.exec(count_query).one()

            # Apply pagination and ordering
            query = query.order_by(Task.created_at.desc()).limit(limit).offset(offset)

            tasks = self.session.exec(query).all()

            return {
                "success": True,
                "tasks": [
                    {
                        "id": str(task.id),
                        "title": task.title,
                        "description": task.description,
                        "is_complete": task.is_complete,
                        "created_at": task.created_at.isoformat(),
                        "updated_at": task.updated_at.isoformat(),
                    }
                    for task in tasks
                ],
                "total": total,
                "limit": limit,
                "offset": offset,
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to list tasks: {str(e)}",
            }

    def complete_task(
        self,
        user_id: str,
        task_id: uuid.UUID,
    ) -> dict[str, Any]:
        """
        Mark a task as complete.

        Args:
            user_id: UUID of the user (for ownership verification)
            task_id: UUID of the task to mark complete

        Returns:
            Dictionary containing updated task details or error message
        """
        try:
            # Convert UUID to string since Task.id is stored as str
            task_id_str = str(task_id)

            # Retrieve and verify ownership
            task = self.session.get(Task, task_id_str)

            if not task:
                return {
                    "success": False,
                    "error": "Task not found",
                }

            if task.user_id != user_id:
                return {
                    "success": False,
                    "error": "Not authorized to access this task",
                }

            # Mark as complete
            task.is_complete = True
            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)

            return {
                "success": True,
                "task": {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "is_complete": task.is_complete,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat(),
                },
            }
        except Exception as e:
            self.session.rollback()
            return {
                "success": False,
                "error": f"Failed to complete task: {str(e)}",
            }

    def delete_task(
        self,
        user_id: str,
        task_id: uuid.UUID,
    ) -> dict[str, Any]:
        """
        Delete a task.

        Args:
            user_id: UUID of the user (for ownership verification)
            task_id: UUID of the task to delete

        Returns:
            Dictionary confirming deletion or error message
        """
        try:
            # Convert UUID to string since Task.id is stored as str
            task_id_str = str(task_id)

            # Retrieve and verify ownership
            task = self.session.get(Task, task_id_str)

            if not task:
                return {
                    "success": False,
                    "error": "Task not found",
                }

            if task.user_id != user_id:
                return {
                    "success": False,
                    "error": "Not authorized to access this task",
                }

            # Delete task
            self.session.delete(task)
            self.session.commit()

            return {
                "success": True,
                "message": f"Task '{task.title}' deleted successfully",
            }
        except Exception as e:
            self.session.rollback()
            return {
                "success": False,
                "error": f"Failed to delete task: {str(e)}",
            }

    def update_task(
        self,
        user_id: str,
        task_id: uuid.UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        is_complete: Optional[bool] = None,
    ) -> dict[str, Any]:
        """
        Update task details (title, description, or completion status).

        Args:
            user_id: UUID of the user (for ownership verification)
            task_id: UUID of the task to update
            title: Optional new title (1-200 characters)
            description: Optional new description (max 2000 characters)
            is_complete: Optional new completion status

        Returns:
            Dictionary containing updated task details or error message
        """
        try:
            # Convert UUID to string since Task.id is stored as str
            task_id_str = str(task_id)

            # Retrieve and verify ownership
            task = self.session.get(Task, task_id_str)

            if not task:
                return {
                    "success": False,
                    "error": "Task not found",
                }

            if task.user_id != user_id:
                return {
                    "success": False,
                    "error": "Not authorized to access this task",
                }

            # Validate and apply updates
            if title is not None:
                if not title or not title.strip():
                    return {
                        "success": False,
                        "error": "Title cannot be empty",
                    }
                if len(title) > 200:
                    return {
                        "success": False,
                        "error": "Title must be 200 characters or less",
                    }
                task.title = title.strip()

            if description is not None:
                if len(description) > 2000:
                    return {
                        "success": False,
                        "error": "Description must be 2000 characters or less",
                    }
                task.description = description.strip() if description else None

            if is_complete is not None:
                task.is_complete = is_complete

            # Save changes
            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)

            return {
                "success": True,
                "task": {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "is_complete": task.is_complete,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat(),
                },
            }
        except Exception as e:
            self.session.rollback()
            return {
                "success": False,
                "error": f"Failed to update task: {str(e)}",
            }


# MCP Tool Schema Definitions (for OpenAI Agents SDK)
MCP_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task for the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "UUID of the task owner",
                    },
                    "title": {
                        "type": "string",
                        "description": "Task title (required, 1-200 characters)",
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional task description (max 2000 characters)",
                    },
                },
                "required": ["user_id", "title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List all tasks for a user with optional filtering",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "UUID of the user",
                    },
                    "is_complete": {
                        "type": "boolean",
                        "description": "Optional filter: true for completed tasks, false for incomplete, null for all",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of tasks to return (1-100, default 50)",
                        "default": 50,
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Number of tasks to skip (default 0)",
                        "default": 0,
                    },
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as complete",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "UUID of the user (for ownership verification)",
                    },
                    "task_id": {
                        "type": "string",
                        "description": "UUID of the task to mark complete",
                    },
                },
                "required": ["user_id", "task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "UUID of the user (for ownership verification)",
                    },
                    "task_id": {
                        "type": "string",
                        "description": "UUID of the task to delete",
                    },
                },
                "required": ["user_id", "task_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update task details (title, description, or completion status)",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "UUID of the user (for ownership verification)",
                    },
                    "task_id": {
                        "type": "string",
                        "description": "UUID of the task to update",
                    },
                    "title": {
                        "type": "string",
                        "description": "Optional new title (1-200 characters)",
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional new description (max 2000 characters)",
                    },
                    "is_complete": {
                        "type": "boolean",
                        "description": "Optional new completion status",
                    },
                },
                "required": ["user_id", "task_id"],
            },
        },
    },
]
