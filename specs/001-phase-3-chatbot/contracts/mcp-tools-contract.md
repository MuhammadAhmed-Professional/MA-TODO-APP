# MCP Tools Contract - Phase III

**Version**: 1.0.0
**Status**: Active
**Created**: 2025-12-13
**Specification**: OpenAI Agents SDK + Official MCP SDK

---

## Overview

This document specifies the JSON schema contracts for the 5 MCP tools used by the Phase III AI chatbot. Each tool follows the OpenAI Agents SDK format with standardized parameter validation, return types, and error handling.

### Tool Inventory

| Tool | Purpose | Parameters | Returns |
|------|---------|-----------|---------|
| `add_task` | Create new task | user_id, title, description | task_id, title, status, created_at |
| `list_tasks` | List tasks with filter | user_id, status | tasks array |
| `complete_task` | Mark task complete | user_id, task_id | success, message |
| `delete_task` | Delete task | user_id, task_id | success, message |
| `update_task` | Update task details | user_id, task_id, title, description | task_id, title, description |

---

## Tool 1: add_task

**Purpose**: Create a new task for the authenticated user.

### JSON Schema Definition

```json
{
  "name": "add_task",
  "description": "Create a new task. Returns task_id, title, and status. Task is created with 'pending' status.",
  "input_schema": {
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
        "description": "Optional task description. Examples: 'milk, eggs, bread', 'authentication module'. Default: null"
      }
    },
    "required": ["user_id", "title"],
    "additionalProperties": false
  }
}
```

### Return Schema

```json
{
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
      "enum": ["pending"],
      "description": "Always 'pending' for new tasks"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "ISO8601 timestamp when task was created"
    }
  }
}
```

### Example Invocation

**Agent Call**:
```json
{
  "name": "add_task",
  "arguments": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries",
    "description": "milk, eggs, bread"
  }
}
```

**Response**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "Buy groceries",
  "description": "milk, eggs, bread",
  "status": "pending",
  "created_at": "2025-12-13T10:30:00Z"
}
```

### Error Handling

| Error Code | Status | Description | Example |
|-----------|--------|-------------|---------|
| VALIDATION_ERROR | 400 | Title empty, too long, or description > 2000 chars | `{"error": "Title must be 1-200 characters"}` |
| AUTHORIZATION_ERROR | 403 | user_id doesn't match authenticated user | `{"error": "Access denied"}` |
| SERVER_ERROR | 500 | Database or system failure | `{"error": "Failed to create task"}` |

---

## Tool 2: list_tasks

**Purpose**: Retrieve tasks with optional status filter.

### JSON Schema Definition

```json
{
  "name": "list_tasks",
  "description": "Retrieve tasks with optional status filter. Returns array of tasks for the user.",
  "input_schema": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "format": "uuid",
        "description": "UUID of the user retrieving tasks. Must match authenticated user."
      },
      "status": {
        "type": "string",
        "enum": ["all", "pending", "completed"],
        "description": "Filter tasks by status. Default: 'all'. Options: 'all'=all tasks, 'pending'=incomplete, 'completed'=done"
      }
    },
    "required": ["user_id"],
    "additionalProperties": false
  }
}
```

### Return Schema

```json
{
  "type": "object",
  "properties": {
    "tasks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {
            "type": "string",
            "format": "uuid",
            "description": "Task ID"
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
            "description": "ISO8601 creation timestamp"
          }
        }
      },
      "description": "Array of tasks matching filter"
    },
    "count": {
      "type": "integer",
      "description": "Total number of tasks returned"
    }
  }
}
```

### Example Invocations

**Agent Call - All Tasks**:
```json
{
  "name": "list_tasks",
  "arguments": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "all"
  }
}
```

**Response - All Tasks**:
```json
{
  "tasks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "title": "Buy groceries",
      "description": "milk, eggs, bread",
      "status": "pending",
      "created_at": "2025-12-13T10:30:00Z"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "title": "Fix bug in dashboard",
      "description": null,
      "status": "pending",
      "created_at": "2025-12-13T09:00:00Z"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440003",
      "title": "Finish report",
      "description": null,
      "status": "completed",
      "created_at": "2025-12-12T14:00:00Z"
    }
  ],
  "count": 3
}
```

**Agent Call - Pending Only**:
```json
{
  "name": "list_tasks",
  "arguments": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "pending"
  }
}
```

**Response - Pending Only**:
```json
{
  "tasks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "title": "Buy groceries",
      "description": "milk, eggs, bread",
      "status": "pending",
      "created_at": "2025-12-13T10:30:00Z"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "title": "Fix bug in dashboard",
      "description": null,
      "status": "pending",
      "created_at": "2025-12-13T09:00:00Z"
    }
  ],
  "count": 2
}
```

### Error Handling

| Error Code | Status | Description | Example |
|-----------|--------|-------------|---------|
| AUTHORIZATION_ERROR | 403 | user_id doesn't match authenticated user | `{"error": "Access denied"}` |
| SERVER_ERROR | 500 | Database failure | `{"error": "Failed to retrieve tasks"}` |

---

## Tool 3: complete_task

**Purpose**: Mark a task as completed.

### JSON Schema Definition

```json
{
  "name": "complete_task",
  "description": "Mark a task as completed. Changes status from 'pending' to 'completed'.",
  "input_schema": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "format": "uuid",
        "description": "UUID of the task owner. Must match authenticated user."
      },
      "task_id": {
        "type": "string",
        "format": "uuid",
        "description": "UUID of the task to mark complete"
      }
    },
    "required": ["user_id", "task_id"],
    "additionalProperties": false
  }
}
```

### Return Schema

```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean",
      "description": "Whether operation succeeded"
    },
    "message": {
      "type": "string",
      "description": "Human-readable message"
    },
    "task_id": {
      "type": "string",
      "format": "uuid",
      "description": "ID of completed task"
    }
  }
}
```

### Example Invocation

**Agent Call**:
```json
{
  "name": "complete_task",
  "arguments": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "task_id": "550e8400-e29b-41d4-a716-446655440001"
  }
}
```

**Response - Success**:
```json
{
  "success": true,
  "message": "'Buy groceries' is now marked complete",
  "task_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

**Response - Already Completed**:
```json
{
  "success": false,
  "message": "'Buy groceries' is already marked complete",
  "task_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

### Error Handling

| Error Code | Status | Description | Example |
|-----------|--------|-------------|---------|
| NOT_FOUND | 404 | Task doesn't exist | `{"error": "Task not found"}` |
| AUTHORIZATION_ERROR | 403 | Task belongs to different user | `{"error": "Access denied"}` |
| SERVER_ERROR | 500 | Database failure | `{"error": "Failed to update task"}` |

---

## Tool 4: delete_task

**Purpose**: Delete a task permanently.

### JSON Schema Definition

```json
{
  "name": "delete_task",
  "description": "Delete a task permanently. This is irreversible.",
  "input_schema": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "format": "uuid",
        "description": "UUID of the task owner. Must match authenticated user."
      },
      "task_id": {
        "type": "string",
        "format": "uuid",
        "description": "UUID of the task to delete"
      }
    },
    "required": ["user_id", "task_id"],
    "additionalProperties": false
  }
}
```

### Return Schema

```json
{
  "type": "object",
  "properties": {
    "success": {
      "type": "boolean",
      "description": "Whether operation succeeded"
    },
    "message": {
      "type": "string",
      "description": "Human-readable message"
    },
    "task_id": {
      "type": "string",
      "format": "uuid",
      "description": "ID of deleted task"
    }
  }
}
```

### Example Invocation

**Agent Call**:
```json
{
  "name": "delete_task",
  "arguments": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "task_id": "550e8400-e29b-41d4-a716-446655440002"
  }
}
```

**Response - Success**:
```json
{
  "success": true,
  "message": "'Fix bug in dashboard' has been deleted",
  "task_id": "550e8400-e29b-41d4-a716-446655440002"
}
```

### Agent Behavior Requirement

The agent MUST ask for user confirmation before calling this tool:
```
Agent: "Do you want to delete 'Fix bug in dashboard'? (yes/no)"
User: "yes"
Agent: [calls delete_task tool]
```

### Error Handling

| Error Code | Status | Description | Example |
|-----------|--------|-------------|---------|
| NOT_FOUND | 404 | Task doesn't exist | `{"error": "Task not found"}` |
| AUTHORIZATION_ERROR | 403 | Task belongs to different user | `{"error": "Access denied"}` |
| SERVER_ERROR | 500 | Database failure | `{"error": "Failed to delete task"}` |

---

## Tool 5: update_task

**Purpose**: Update task title and/or description.

### JSON Schema Definition

```json
{
  "name": "update_task",
  "description": "Update task title and/or description. At least one field must be provided.",
  "input_schema": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "format": "uuid",
        "description": "UUID of the task owner. Must match authenticated user."
      },
      "task_id": {
        "type": "string",
        "format": "uuid",
        "description": "UUID of the task to update"
      },
      "title": {
        "type": "string",
        "minLength": 1,
        "maxLength": 200,
        "description": "New task title (optional). If provided, replaces current title."
      },
      "description": {
        "type": "string",
        "maxLength": 2000,
        "description": "New task description (optional). If provided, replaces current description."
      }
    },
    "required": ["user_id", "task_id"],
    "additionalProperties": false
  }
}
```

### Return Schema

```json
{
  "type": "object",
  "properties": {
    "task_id": {
      "type": "string",
      "format": "uuid",
      "description": "UUID of updated task"
    },
    "title": {
      "type": "string",
      "description": "Updated task title"
    },
    "description": {
      "type": "string",
      "description": "Updated task description (null if not set)"
    },
    "status": {
      "type": "string",
      "enum": ["pending", "completed"],
      "description": "Task status (unchanged)"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time",
      "description": "ISO8601 timestamp of update"
    }
  }
}
```

### Example Invocations

**Update Title Only**:
```json
{
  "name": "update_task",
  "arguments": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "task_id": "550e8400-e29b-41d4-a716-446655440001",
    "title": "Buy groceries and cook dinner"
  }
}
```

**Response**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "Buy groceries and cook dinner",
  "description": "milk, eggs, bread",
  "status": "pending",
  "updated_at": "2025-12-13T10:35:00Z"
}
```

**Update Description Only**:
```json
{
  "name": "update_task",
  "arguments": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "task_id": "550e8400-e29b-41d4-a716-446655440001",
    "description": "High priority: milk, eggs, bread, butter"
  }
}
```

**Update Both Title and Description**:
```json
{
  "name": "update_task",
  "arguments": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "task_id": "550e8400-e29b-41d4-a716-446655440001",
    "title": "Weekly shopping",
    "description": "grocery store: milk, eggs, bread, butter, cheese"
  }
}
```

### Error Handling

| Error Code | Status | Description | Example |
|-----------|--------|-------------|---------|
| VALIDATION_ERROR | 400 | No fields provided or invalid field format | `{"error": "Provide at least one field to update"}` |
| NOT_FOUND | 404 | Task doesn't exist | `{"error": "Task not found"}` |
| AUTHORIZATION_ERROR | 403 | Task belongs to different user | `{"error": "Access denied"}` |
| SERVER_ERROR | 500 | Database failure | `{"error": "Failed to update task"}` |

---

## Standardized Error Response Format

All tools return errors in standardized format:

```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable error message",
  "details": {
    "field": "value",
    "reason": "explanation"
  }
}
```

**Error Codes**:
- `VALIDATION_ERROR` (400): Input validation failed
- `AUTHORIZATION_ERROR` (403): User lacks permission
- `NOT_FOUND` (404): Resource doesn't exist
- `CONFLICT_ERROR` (409): Operation conflicts with current state
- `SERVER_ERROR` (500): Unexpected server error

---

## Implementation Checklist

- [ ] All 5 tools registered with MCP server
- [ ] JSON schemas match this contract exactly
- [ ] Input parameters validated per schema
- [ ] Return values match schema format
- [ ] Error responses in standardized format
- [ ] All user_id checks validate authorization
- [ ] Database queries use parameterized statements (no SQL injection)
- [ ] Tool logging includes trace_id and tool name
- [ ] Tool latency < 1 second for all tools
- [ ] Concurrent tool calls supported (stateless)
- [ ] Connection pooling enabled for database
- [ ] Rate limiting enforced per user_id

---

## Integration with Agent

### System Prompt Section

```
You have access to these tools for managing tasks:

1. add_task(user_id, title, description?) - Create a new task
2. list_tasks(user_id, status="all"|"pending"|"completed") - List tasks
3. complete_task(user_id, task_id) - Mark task complete
4. delete_task(user_id, task_id) - Delete task (ask for confirmation first!)
5. update_task(user_id, task_id, title?, description?) - Update task details

Always:
- Ask for confirmation before deleting
- Call list_tasks first if you need to identify a task by title
- Use exact user_id from conversation context
- Report results naturally to user
```

### Example Agent Flow

```
User: "Add a task to buy milk"
↓
Agent: Recognizes intent = add_task, extracts title = "buy milk"
↓
Agent calls: add_task(user_id="550e8400...", title="buy milk")
↓
Agent receives: {task_id: "660f9511...", title: "buy milk", status: "pending", ...}
↓
Agent responds: "I've created a task: 'Buy milk'"
```

---

**Status**: ✅ Complete
**Next**: Quickstart Guide
