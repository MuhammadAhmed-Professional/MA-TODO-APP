# Phase III: MCP Tools Specification

**Version**: 1.0.0
**Status**: Active
**Created**: 2025-12-13
**Last Updated**: 2025-12-13

---

## Overview

This document specifies the five MCP (Model Context Protocol) tools that the Phase III AI chatbot uses to perform todo operations. Each tool is defined as a JSON schema compatible with the official MCP SDK, with complete parameter specifications, return types, error handling, and implementation examples.

**Tool Inventory**:
1. `add_task` - Create a new task
2. `list_tasks` - List tasks with status filter
3. `complete_task` - Mark a task as completed
4. `delete_task` - Delete a task
5. `update_task` - Update task details

---

## Tool 1: add_task

### Purpose
Create a new task for the authenticated user.

### JSON Schema Definition

```json
{
  "name": "add_task",
  "description": "Create a new task for the user. Returns task_id, title, and status.",
  "parameters": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "format": "uuid",
        "description": "UUID of the user creating the task. Must match authenticated user."
      },
      "title": {
        "type": "string",
        "minLength": 1,
        "maxLength": 200,
        "description": "Task title (required). Examples: 'Buy groceries', 'Fix bug in dashboard'"
      },
      "description": {
        "type": "string",
        "maxLength": 2000,
        "description": "Optional task description. Examples: 'milk, eggs, bread', 'authentication module'"
      }
    },
    "required": ["user_id", "title"],
    "additionalProperties": false
  },
  "returns": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "string",
        "format": "uuid",
        "description": "UUID of created task"
      },
      "title": {
        "type": "string",
        "description": "Task title as stored"
      },
      "description": {
        "type": "string",
        "description": "Task description as stored (null if not provided)"
      },
      "status": {
        "type": "string",
        "enum": ["pending", "completed"],
        "description": "Always 'pending' for new tasks"
      },
      "created_at": {
        "type": "string",
        "format": "date-time",
        "description": "Timestamp when task was created (ISO8601)"
      }
    }
  },
  "errors": [
    {
      "code": "VALIDATION_ERROR",
      "status": 400,
      "description": "Title is empty, too long (>200), or description too long (>2000)",
      "example": {
        "error": "VALIDATION_ERROR",
        "message": "Task title must be between 1 and 200 characters"
      }
    },
    {
      "code": "AUTHORIZATION_ERROR",
      "status": 403,
      "description": "user_id doesn't match authenticated user or user not found",
      "example": {
        "error": "AUTHORIZATION_ERROR",
        "message": "Access denied"
      }
    },
    {
      "code": "SERVER_ERROR",
      "status": 500,
      "description": "Database error or system failure",
      "example": {
        "error": "SERVER_ERROR",
        "message": "Failed to create task. Please try again."
      }
    }
  ]
}
```

### Implementation (Python/FastAPI)

```python
from fastapi import HTTPException, Depends
from sqlmodel import Session
from uuid import UUID
import json
import logging

logger = logging.getLogger(__name__)

async def handle_add_task(
    user_id: UUID,
    title: str,
    description: str | None = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    MCP Tool handler for add_task.

    Args:
        user_id: UUID of task creator (must match authenticated user)
        title: Task title (1-200 chars)
        description: Optional task description (0-2000 chars)
        session: Database session
        current_user: Authenticated user from JWT

    Returns:
        dict with task_id, title, description, status, created_at

    Raises:
        HTTPException: Validation error (400), authorization error (403), server error (500)
    """
    trace_id = str(uuid4())

    try:
        # 1. Validate authorization
        if user_id != current_user.id:
            logger.warning(
                json.dumps({
                    "timestamp": datetime.utcnow().isoformat(),
                    "trace_id": trace_id,
                    "component": "mcp_tool",
                    "tool": "add_task",
                    "action": "authorization_error",
                    "attempted_user": str(user_id),
                    "authenticated_user": str(current_user.id)
                })
            )
            raise HTTPException(status_code=403, detail="Access denied")

        # 2. Validate input
        title = title.strip()
        if not title:
            raise HTTPException(
                status_code=400,
                detail="Task title cannot be empty"
            )
        if len(title) > 200:
            raise HTTPException(
                status_code=400,
                detail="Task title must be 200 characters or less"
            )

        if description and len(description) > 2000:
            raise HTTPException(
                status_code=400,
                detail="Task description must be 2000 characters or less"
            )

        # 3. Create task
        task = Task(
            user_id=user_id,
            title=title,
            description=description.strip() if description else None,
            status="pending"
        )
        session.add(task)
        session.flush()  # Get the ID without committing

        # 4. Log operation
        logger.info(
            json.dumps({
                "timestamp": datetime.utcnow().isoformat(),
                "trace_id": trace_id,
                "component": "mcp_tool",
                "tool": "add_task",
                "action": "task_created",
                "user_id": str(user_id),
                "task_id": str(task.id),
                "title_length": len(title)
            })
        )

        # 5. Return result
        return {
            "task_id": str(task.id),
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "created_at": task.created_at.isoformat()
        }

    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(
            json.dumps({
                "timestamp": datetime.utcnow().isoformat(),
                "trace_id": trace_id,
                "component": "mcp_tool",
                "tool": "add_task",
                "action": "error",
                "error": str(e),
                "user_id": str(user_id)
            })
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to create task. Please try again."
        )
```

### Example Usage

```python
# Via API
POST /mcp/add_task
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "milk, eggs, bread"
}

# Response (200)
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Buy groceries",
  "description": "milk, eggs, bread",
  "status": "pending",
  "created_at": "2025-12-13T14:30:45.123Z"
}

# Via Agent
User: "Add a task to buy groceries"
Agent: Invokes add_task(user_id=..., title="Buy groceries")
Agent Response: "I've created a task: 'Buy groceries'. Would you like to add any details?"
```

---

## Tool 2: list_tasks

### Purpose
List tasks for the authenticated user, optionally filtered by status.

### JSON Schema Definition

```json
{
  "name": "list_tasks",
  "description": "List tasks for the user with optional status filter. Returns array of tasks.",
  "parameters": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "format": "uuid",
        "description": "UUID of the user whose tasks to list"
      },
      "status": {
        "type": "string",
        "enum": ["all", "pending", "completed"],
        "default": "all",
        "description": "Filter tasks by status. Default: 'all'"
      }
    },
    "required": ["user_id"],
    "additionalProperties": false
  },
  "returns": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "task_id": {
          "type": "string",
          "format": "uuid",
          "description": "UUID of task"
        },
        "title": {
          "type": "string",
          "description": "Task title"
        },
        "description": {
          "type": "string",
          "description": "Task description (null if not set)"
        },
        "status": {
          "type": "string",
          "enum": ["pending", "completed"],
          "description": "Task status"
        },
        "created_at": {
          "type": "string",
          "format": "date-time",
          "description": "When task was created"
        }
      }
    },
    "description": "Array of tasks (empty if no matching tasks)"
  },
  "errors": [
    {
      "code": "VALIDATION_ERROR",
      "status": 400,
      "description": "Invalid status value (must be 'all', 'pending', or 'completed')",
      "example": {
        "error": "VALIDATION_ERROR",
        "message": "Invalid status: 'invalid'. Must be 'all', 'pending', or 'completed'"
      }
    },
    {
      "code": "AUTHORIZATION_ERROR",
      "status": 403,
      "description": "user_id doesn't match authenticated user",
      "example": {
        "error": "AUTHORIZATION_ERROR",
        "message": "Access denied"
      }
    }
  ]
}
```

### Implementation (Python/FastAPI)

```python
async def handle_list_tasks(
    user_id: UUID,
    status: str = "all",
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    """
    MCP Tool handler for list_tasks.

    Args:
        user_id: UUID of user whose tasks to list
        status: Filter by 'all', 'pending', or 'completed'
        session: Database session
        current_user: Authenticated user

    Returns:
        List of task dicts with id, title, description, status, created_at

    Raises:
        HTTPException: Validation error (400), authorization error (403)
    """
    trace_id = str(uuid4())

    try:
        # 1. Validate authorization
        if user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

        # 2. Validate status
        if status not in ["all", "pending", "completed"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status: '{status}'. Must be 'all', 'pending', or 'completed'"
            )

        # 3. Query tasks
        query = select(Task).where(Task.user_id == user_id)

        if status != "all":
            query = query.where(Task.status == status)

        # Order by creation date (newest first)
        query = query.order_by(Task.created_at.desc())

        tasks = session.exec(query).all()

        # 4. Log operation
        logger.info(
            json.dumps({
                "timestamp": datetime.utcnow().isoformat(),
                "trace_id": trace_id,
                "component": "mcp_tool",
                "tool": "list_tasks",
                "action": "tasks_listed",
                "user_id": str(user_id),
                "status_filter": status,
                "task_count": len(tasks)
            })
        )

        # 5. Return results
        return [
            {
                "task_id": str(task.id),
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "created_at": task.created_at.isoformat()
            }
            for task in tasks
        ]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            json.dumps({
                "timestamp": datetime.utcnow().isoformat(),
                "trace_id": trace_id,
                "component": "mcp_tool",
                "tool": "list_tasks",
                "action": "error",
                "error": str(e),
                "user_id": str(user_id)
            })
        )
        raise HTTPException(status_code=500, detail="Failed to list tasks")
```

### Example Usage

```python
# Via API
POST /mcp/list_tasks
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending"
}

# Response (200)
[
  {
    "task_id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Buy groceries",
    "description": "milk, eggs, bread",
    "status": "pending",
    "created_at": "2025-12-13T14:30:45.123Z"
  },
  {
    "task_id": "234e5678-e89b-12d3-a456-426614174001",
    "title": "Fix bug in dashboard",
    "description": null,
    "status": "pending",
    "created_at": "2025-12-12T10:15:30.456Z"
  }
]

# Via Agent
User: "Show me all my pending tasks"
Agent: Invokes list_tasks(user_id=..., status="pending")
Agent Response: "You have 2 pending tasks:
1. Buy groceries
2. Fix bug in dashboard"
```

---

## Tool 3: complete_task

### Purpose
Mark a task as completed.

### JSON Schema Definition

```json
{
  "name": "complete_task",
  "description": "Mark a task as completed. Returns updated task.",
  "parameters": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "format": "uuid",
        "description": "UUID of user who owns the task"
      },
      "task_id": {
        "type": "string",
        "format": "uuid",
        "description": "UUID of task to complete"
      }
    },
    "required": ["user_id", "task_id"],
    "additionalProperties": false
  },
  "returns": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "string",
        "format": "uuid"
      },
      "title": {
        "type": "string"
      },
      "status": {
        "type": "string",
        "enum": ["pending", "completed"]
      },
      "updated_at": {
        "type": "string",
        "format": "date-time"
      }
    }
  },
  "errors": [
    {
      "code": "NOT_FOUND",
      "status": 404,
      "description": "Task doesn't exist or doesn't belong to user",
      "example": {
        "error": "NOT_FOUND",
        "message": "Task not found"
      }
    },
    {
      "code": "INVALID_STATE",
      "status": 409,
      "description": "Task is already completed",
      "example": {
        "error": "INVALID_STATE",
        "message": "Task is already completed"
      }
    },
    {
      "code": "AUTHORIZATION_ERROR",
      "status": 403,
      "description": "user_id doesn't match authenticated user"
    }
  ]
}
```

### Implementation (Python/FastAPI)

```python
async def handle_complete_task(
    user_id: UUID,
    task_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    MCP Tool handler for complete_task.

    Args:
        user_id: User UUID
        task_id: Task UUID to complete
        session: Database session
        current_user: Authenticated user

    Returns:
        Updated task with id, title, status, updated_at

    Raises:
        HTTPException: Not found (404), already completed (409), authorization (403)
    """
    trace_id = str(uuid4())

    try:
        # 1. Validate authorization
        if user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

        # 2. Fetch task
        task = session.get(Task, task_id)
        if not task or task.user_id != user_id:
            raise HTTPException(status_code=404, detail="Task not found")

        # 3. Check if already completed
        if task.status == "completed":
            raise HTTPException(
                status_code=409,
                detail="Task is already completed"
            )

        # 4. Update task
        task.status = "completed"
        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()

        # 5. Log operation
        logger.info(
            json.dumps({
                "timestamp": datetime.utcnow().isoformat(),
                "trace_id": trace_id,
                "component": "mcp_tool",
                "tool": "complete_task",
                "action": "task_completed",
                "user_id": str(user_id),
                "task_id": str(task_id)
            })
        )

        # 6. Return result
        return {
            "task_id": str(task.id),
            "title": task.title,
            "status": task.status,
            "updated_at": task.updated_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            json.dumps({
                "timestamp": datetime.utcnow().isoformat(),
                "trace_id": trace_id,
                "component": "mcp_tool",
                "tool": "complete_task",
                "action": "error",
                "error": str(e),
                "task_id": str(task_id)
            })
        )
        raise HTTPException(status_code=500, detail="Failed to complete task")
```

### Example Usage

```python
# Via API
POST /mcp/complete_task
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_id": "123e4567-e89b-12d3-a456-426614174000"
}

# Response (200)
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Buy groceries",
  "status": "completed",
  "updated_at": "2025-12-13T14:35:22.789Z"
}

# Via Agent
User: "Mark the first task complete"
Agent: Invokes complete_task(user_id=..., task_id=...(resolve from list))
Agent Response: "Done! 'Buy groceries' is now marked complete."
```

---

## Tool 4: delete_task

### Purpose
Delete a task. Requires agent to request user confirmation first.

### JSON Schema Definition

```json
{
  "name": "delete_task",
  "description": "Delete a task permanently. IMPORTANT: Agent must request user confirmation before calling this tool.",
  "parameters": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "format": "uuid",
        "description": "UUID of user who owns the task"
      },
      "task_id": {
        "type": "string",
        "format": "uuid",
        "description": "UUID of task to delete"
      }
    },
    "required": ["user_id", "task_id"],
    "additionalProperties": false
  },
  "returns": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "string",
        "format": "uuid"
      },
      "title": {
        "type": "string"
      },
      "status": {
        "type": "string",
        "enum": ["deleted"]
      }
    }
  },
  "errors": [
    {
      "code": "NOT_FOUND",
      "status": 404,
      "description": "Task doesn't exist or doesn't belong to user"
    },
    {
      "code": "AUTHORIZATION_ERROR",
      "status": 403,
      "description": "user_id doesn't match authenticated user"
    }
  ]
}
```

### Implementation (Python/FastAPI)

```python
async def handle_delete_task(
    user_id: UUID,
    task_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    MCP Tool handler for delete_task.

    IMPORTANT: This tool should only be called after agent confirms with user.

    Args:
        user_id: User UUID
        task_id: Task UUID to delete
        session: Database session
        current_user: Authenticated user

    Returns:
        Deleted task info with status='deleted'

    Raises:
        HTTPException: Not found (404), authorization (403)
    """
    trace_id = str(uuid4())

    try:
        # 1. Validate authorization
        if user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

        # 2. Fetch task
        task = session.get(Task, task_id)
        if not task or task.user_id != user_id:
            raise HTTPException(status_code=404, detail="Task not found")

        # 3. Store title for response (before deletion)
        title = task.title

        # 4. Delete task
        session.delete(task)
        session.commit()

        # 5. Log operation
        logger.info(
            json.dumps({
                "timestamp": datetime.utcnow().isoformat(),
                "trace_id": trace_id,
                "component": "mcp_tool",
                "tool": "delete_task",
                "action": "task_deleted",
                "user_id": str(user_id),
                "task_id": str(task_id),
                "title": title
            })
        )

        # 6. Return result
        return {
            "task_id": str(task_id),
            "title": title,
            "status": "deleted"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            json.dumps({
                "timestamp": datetime.utcnow().isoformat(),
                "trace_id": trace_id,
                "component": "mcp_tool",
                "tool": "delete_task",
                "action": "error",
                "error": str(e),
                "task_id": str(task_id)
            })
        )
        raise HTTPException(status_code=500, detail="Failed to delete task")
```

### Example Usage

```python
# Confirmation Flow Required
User: "Delete task 1"
Agent: "Are you sure you want to delete 'Buy groceries'? This can't be undone. (yes/no)"
User: "yes"
Agent: Invokes delete_task(user_id=..., task_id=...)
Agent Response: "Task deleted."

# Error Case
User: "Delete my oldest task"
[Task doesn't exist]
Agent Response: "I couldn't find that task. Would you like to see all your tasks?"
```

---

## Tool 5: update_task

### Purpose
Update task details (title and/or description).

### JSON Schema Definition

```json
{
  "name": "update_task",
  "description": "Update task title and/or description. Returns updated task.",
  "parameters": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "format": "uuid",
        "description": "UUID of user who owns the task"
      },
      "task_id": {
        "type": "string",
        "format": "uuid",
        "description": "UUID of task to update"
      },
      "title": {
        "type": "string",
        "minLength": 1,
        "maxLength": 200,
        "description": "New task title (optional, if provided must be 1-200 chars)"
      },
      "description": {
        "type": "string",
        "maxLength": 2000,
        "description": "New task description (optional, max 2000 chars)"
      }
    },
    "required": ["user_id", "task_id"],
    "additionalProperties": false
  },
  "returns": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "string",
        "format": "uuid"
      },
      "title": {
        "type": "string"
      },
      "description": {
        "type": "string"
      },
      "updated_at": {
        "type": "string",
        "format": "date-time"
      }
    }
  },
  "errors": [
    {
      "code": "NOT_FOUND",
      "status": 404,
      "description": "Task doesn't exist or doesn't belong to user"
    },
    {
      "code": "VALIDATION_ERROR",
      "status": 400,
      "description": "Title too long (>200) or description too long (>2000)"
    },
    {
      "code": "AUTHORIZATION_ERROR",
      "status": 403,
      "description": "user_id doesn't match authenticated user"
    }
  ]
}
```

### Implementation (Python/FastAPI)

```python
async def handle_update_task(
    user_id: UUID,
    task_id: UUID,
    title: str | None = None,
    description: str | None = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    MCP Tool handler for update_task.

    Args:
        user_id: User UUID
        task_id: Task UUID to update
        title: New title (optional, 1-200 chars)
        description: New description (optional, 0-2000 chars)
        session: Database session
        current_user: Authenticated user

    Returns:
        Updated task with id, title, description, updated_at

    Raises:
        HTTPException: Not found (404), validation error (400), authorization (403)
    """
    trace_id = str(uuid4())

    try:
        # 1. Validate authorization
        if user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")

        # 2. Validate that at least one field is provided
        if not title and not description:
            raise HTTPException(
                status_code=400,
                detail="At least one field (title or description) must be provided"
            )

        # 3. Fetch task
        task = session.get(Task, task_id)
        if not task or task.user_id != user_id:
            raise HTTPException(status_code=404, detail="Task not found")

        # 4. Validate and update title
        if title:
            title = title.strip()
            if not title:
                raise HTTPException(
                    status_code=400,
                    detail="Task title cannot be empty"
                )
            if len(title) > 200:
                raise HTTPException(
                    status_code=400,
                    detail="Task title must be 200 characters or less"
                )
            task.title = title

        # 5. Validate and update description
        if description:
            description = description.strip()
            if len(description) > 2000:
                raise HTTPException(
                    status_code=400,
                    detail="Task description must be 2000 characters or less"
                )
            task.description = description if description else None

        # 6. Update timestamp
        task.updated_at = datetime.utcnow()
        session.add(task)
        session.commit()

        # 7. Log operation
        logger.info(
            json.dumps({
                "timestamp": datetime.utcnow().isoformat(),
                "trace_id": trace_id,
                "component": "mcp_tool",
                "tool": "update_task",
                "action": "task_updated",
                "user_id": str(user_id),
                "task_id": str(task_id),
                "fields_updated": [k for k, v in {"title": title, "description": description}.items() if v]
            })
        )

        # 8. Return result
        return {
            "task_id": str(task.id),
            "title": task.title,
            "description": task.description,
            "updated_at": task.updated_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            json.dumps({
                "timestamp": datetime.utcnow().isoformat(),
                "trace_id": trace_id,
                "component": "mcp_tool",
                "tool": "update_task",
                "action": "error",
                "error": str(e),
                "task_id": str(task_id)
            })
        )
        raise HTTPException(status_code=500, detail="Failed to update task")
```

### Example Usage

```python
# Via API
POST /mcp/update_task
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Buy groceries and cook dinner"
}

# Response (200)
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Buy groceries and cook dinner",
  "description": "milk, eggs, bread",
  "updated_at": "2025-12-13T14:40:15.999Z"
}

# Via Agent
User: "Change task 1 to 'Call mom tonight'"
Agent: Invokes update_task(user_id=..., task_id=..., title="Call mom tonight")
Agent Response: "Updated! New task: 'Call mom tonight'"
```

---

## Integration with Agent

### Tool Registration

```python
from mcp_sdk import Tool, ToolResult

async def create_mcp_tools(session: AsyncSession) -> list[Tool]:
    """Create all 5 MCP tools for the chatbot agent."""

    tools = [
        Tool(
            name="add_task",
            description="Create a new task",
            parameters=ADD_TASK_SCHEMA,
            handler=lambda params: handle_add_task(**params, session=session)
        ),
        Tool(
            name="list_tasks",
            description="List tasks with optional status filter",
            parameters=LIST_TASKS_SCHEMA,
            handler=lambda params: handle_list_tasks(**params, session=session)
        ),
        Tool(
            name="complete_task",
            description="Mark a task as completed",
            parameters=COMPLETE_TASK_SCHEMA,
            handler=lambda params: handle_complete_task(**params, session=session)
        ),
        Tool(
            name="delete_task",
            description="Delete a task (requires user confirmation)",
            parameters=DELETE_TASK_SCHEMA,
            handler=lambda params: handle_delete_task(**params, session=session)
        ),
        Tool(
            name="update_task",
            description="Update task details (title and/or description)",
            parameters=UPDATE_TASK_SCHEMA,
            handler=lambda params: handle_update_task(**params, session=session)
        ),
    ]

    return tools
```

### Agent Invocation

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def run_agent(messages: list, mcp_tools: list, user_context: dict):
    """Run agent with MCP tools."""

    response = await client.agents.run(
        model="gpt-4-turbo",
        tools=mcp_tools,
        messages=messages,
        system_prompt=SYSTEM_PROMPT,
        temperature=0.7,
        max_tokens=4096
    )

    return response
```

---

## Error Handling Strategy

### Error Categories

1. **VALIDATION_ERROR (400)**
   - Invalid input format (empty string, too long, wrong type)
   - Invalid status value
   - Missing required parameter

2. **AUTHORIZATION_ERROR (403)**
   - user_id doesn't match authenticated user
   - User doesn't have permission for task

3. **NOT_FOUND (404)**
   - Task doesn't exist
   - Task belongs to different user

4. **INVALID_STATE (409)**
   - Task already completed (can't complete twice)
   - Task in invalid state for operation

5. **SERVER_ERROR (500)**
   - Database connection failure
   - Unexpected exception

### User-Facing Error Messages

```
Tool Error (400): "Task title must be 1-200 characters"
→ Agent: "I couldn't create that task because the title is too long. Please keep it under 200 characters."

Tool Error (404): "Task not found"
→ Agent: "I couldn't find that task. Would you like to see all your tasks?"

Tool Error (403): "Access denied"
→ Agent: "I'm unable to access that task. Please try again or contact support."

Tool Error (500): "Failed to create task. Please try again."
→ Agent: "Sorry, I had trouble with that operation. Please try again."
```

---

## Performance Budgets

- Tool execution time: < 500ms (p95)
- Database query: < 100ms
- Tool validation: < 50ms
- Error logging: < 10ms

---

## Testing Requirements

### Unit Tests
```python
def test_add_task_creates_task_correctly():
    result = await handle_add_task(
        user_id=user_id,
        title="Test task",
        description="Test description"
    )
    assert result["status"] == "pending"
    assert result["title"] == "Test task"

def test_list_tasks_filters_by_status():
    results = await handle_list_tasks(user_id=user_id, status="completed")
    assert all(task["status"] == "completed" for task in results)

def test_delete_task_requires_confirmation():
    # Agent should ask for confirmation before calling tool
    assert requires_confirmation(tool_name="delete_task")
```

---

## Next Steps

1. Implement tool handlers in `backend/src/services/mcp_service.py`
2. Register tools with OpenAI Agents SDK
3. Test each tool with unit tests
4. Integration test with chat endpoint
5. E2E test with agent behavior tests

---

**Status**: ✅ Specification Complete
**Next**: Create Agent Behavior Specification (agent-spec.md)
