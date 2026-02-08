# Tasks API Contract

**Feature**: 004-phase-2-web-app
**Base URL**: `/api/tasks`
**Authentication**: Required (JWT token in HttpOnly cookie)

## Overview

Tasks API provides CRUD operations for todo task management with user ownership enforcement.

---

## Endpoints

### 1. List Tasks

**Endpoint**: `GET /api/tasks`
**Authentication**: Required
**Description**: Retrieve all tasks for the authenticated user

#### Request

**Headers**:
```
Cookie: auth_token=<JWT>
```

**Query Parameters** (optional):
```
?is_complete=true         // Filter by completion status (true/false)
?limit=20                 // Pagination limit (default: 50, max: 100)
?offset=0                 // Pagination offset (default: 0)
?sort=created_at          // Sort field: created_at, updated_at, title (default: created_at)
?order=desc               // Sort order: asc, desc (default: desc)
```

#### Response

**Success (200 OK)**:
```json
{
  "tasks": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread, coffee",
      "is_complete": false,
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2025-12-06T10:30:00Z",
      "updated_at": "2025-12-06T10:30:00Z"
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440002",
      "title": "Finish hackathon",
      "description": null,
      "is_complete": true,
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2025-12-05T14:20:00Z",
      "updated_at": "2025-12-06T09:15:00Z"
    }
  ],
  "total": 2,
  "limit": 50,
  "offset": 0
}
```

**Errors**:
- `401 Unauthorized`: Missing or invalid token
  ```json
  {
    "detail": "Not authenticated"
  }
  ```

---

### 2. Create Task

**Endpoint**: `POST /api/tasks`
**Authentication**: Required
**Description**: Create a new task for the authenticated user

#### Request

**Headers**:
```
Content-Type: application/json
Cookie: auth_token=<JWT>
```

**Body**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread, coffee"
}
```

**Schema**:
```typescript
interface TaskCreate {
  title: string;              // Required, 1-200 characters
  description?: string | null; // Optional, max 2000 characters
}
```

#### Response

**Success (201 Created)**:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread, coffee",
  "is_complete": false,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-12-06T10:30:00Z",
  "updated_at": "2025-12-06T10:30:00Z"
}
```

**Headers**:
```
Location: /api/tasks/660e8400-e29b-41d4-a716-446655440001
```

**Errors**:
- `400 Bad Request`: Validation errors
  ```json
  {
    "detail": "Title is required"
  }
  ```
- `401 Unauthorized`: Missing or invalid token
- `422 Unprocessable Entity`: Invalid request format
  ```json
  {
    "detail": [
      {
        "loc": ["body", "title"],
        "msg": "ensure this value has at most 200 characters",
        "type": "value_error.any_str.max_length"
      }
    ]
  }
  ```

---

### 3. Get Task

**Endpoint**: `GET /api/tasks/{task_id}`
**Authentication**: Required
**Description**: Retrieve a single task by ID (with ownership check)

#### Request

**Headers**:
```
Cookie: auth_token=<JWT>
```

**Path Parameters**:
- `task_id` (UUID): Task unique identifier

#### Response

**Success (200 OK)**:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread, coffee",
  "is_complete": false,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-12-06T10:30:00Z",
  "updated_at": "2025-12-06T10:30:00Z"
}
```

**Errors**:
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Task belongs to different user
  ```json
  {
    "detail": "Not authorized to access this task"
  }
  ```
- `404 Not Found`: Task does not exist
  ```json
  {
    "detail": "Task not found"
  }
  ```

---

### 4. Update Task

**Endpoint**: `PUT /api/tasks/{task_id}`
**Authentication**: Required
**Description**: Update task title and/or description (with ownership check)

#### Request

**Headers**:
```
Content-Type: application/json
Cookie: auth_token=<JWT>
```

**Path Parameters**:
- `task_id` (UUID): Task unique identifier

**Body** (all fields optional):
```json
{
  "title": "Buy groceries and cook dinner",
  "description": "Updated description"
}
```

**Schema**:
```typescript
interface TaskUpdate {
  title?: string | null;       // Optional, 1-200 characters if provided
  description?: string | null; // Optional, max 2000 characters if provided
}
```

#### Response

**Success (200 OK)**:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "title": "Buy groceries and cook dinner",
  "description": "Updated description",
  "is_complete": false,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-12-06T10:30:00Z",
  "updated_at": "2025-12-06T11:45:00Z"  // Updated timestamp
}
```

**Errors**:
- `400 Bad Request`: Validation errors
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Task belongs to different user
- `404 Not Found`: Task does not exist

---

### 5. Toggle Task Completion

**Endpoint**: `PATCH /api/tasks/{task_id}/complete`
**Authentication**: Required
**Description**: Toggle task completion status (with ownership check)

#### Request

**Headers**:
```
Content-Type: application/json
Cookie: auth_token=<JWT>
```

**Path Parameters**:
- `task_id` (UUID): Task unique identifier

**Body**:
```json
{
  "is_complete": true
}
```

**Schema**:
```typescript
interface TaskToggleComplete {
  is_complete: boolean;   // Required, true or false
}
```

#### Response

**Success (200 OK)**:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread, coffee",
  "is_complete": true,  // Updated status
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-12-06T10:30:00Z",
  "updated_at": "2025-12-06T12:00:00Z"  // Updated timestamp
}
```

**Errors**:
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Task belongs to different user
- `404 Not Found`: Task does not exist

---

### 6. Delete Task

**Endpoint**: `DELETE /api/tasks/{task_id}`
**Authentication**: Required
**Description**: Permanently delete a task (with ownership check)

#### Request

**Headers**:
```
Cookie: auth_token=<JWT>
```

**Path Parameters**:
- `task_id` (UUID): Task unique identifier

#### Response

**Success (204 No Content)**:
- Empty body
- Task permanently deleted from database

**Errors**:
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Task belongs to different user
- `404 Not Found`: Task does not exist

---

## Common Response Types

### Task Object

```typescript
interface Task {
  id: string;              // UUID
  title: string;           // 1-200 characters
  description: string | null; // 0-2000 characters or null
  is_complete: boolean;    // Completion status
  user_id: string;         // Owner's UUID
  created_at: string;      // ISO 8601 timestamp
  updated_at: string;      // ISO 8601 timestamp
}
```

### Task List Response

```typescript
interface TaskListResponse {
  tasks: Task[];
  total: number;      // Total count (for pagination)
  limit: number;      // Current limit
  offset: number;     // Current offset
}
```

---

## Authorization Logic

**Ownership Check** (applied to all single-task operations):
1. Extract `user_id` from JWT token claims
2. Query task by `task_id`
3. If task not found → 404 Not Found
4. If `task.user_id != token.user_id` → 403 Forbidden
5. If authorized → proceed with operation

**Example (pseudocode)**:
```python
def get_task(task_id: UUID, current_user_id: UUID):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return task
```

---

## Frontend Integration Example

```typescript
// List tasks
const getTasks = async (filters?: { is_complete?: boolean }) => {
  const params = new URLSearchParams();
  if (filters?.is_complete !== undefined) {
    params.append("is_complete", String(filters.is_complete));
  }

  const response = await fetch(`/api/tasks?${params}`, {
    credentials: "include",
  });

  if (!response.ok) throw new Error("Failed to fetch tasks");
  return await response.json();
};

// Create task
const createTask = async (title: string, description?: string) => {
  const response = await fetch("/api/tasks", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, description }),
    credentials: "include",
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  return await response.json();
};

// Update task
const updateTask = async (
  taskId: string,
  updates: { title?: string; description?: string }
) => {
  const response = await fetch(`/api/tasks/${taskId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(updates),
    credentials: "include",
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  return await response.json();
};

// Toggle completion
const toggleTaskComplete = async (taskId: string, isComplete: boolean) => {
  const response = await fetch(`/api/tasks/${taskId}/complete`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ is_complete: isComplete }),
    credentials: "include",
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  return await response.json();
};

// Delete task
const deleteTask = async (taskId: string) => {
  const response = await fetch(`/api/tasks/${taskId}`, {
    method: "DELETE",
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error("Failed to delete task");
  }
};
```

---

## Performance Considerations

- **Pagination**: Use `limit` and `offset` for large task lists (default limit: 50)
- **Filtering**: Database-level filtering (not in-memory) for `is_complete`
- **Sorting**: Database-level sorting (indexes on `created_at`, `updated_at`, `title`)
- **Caching**: Consider HTTP caching headers for GET requests (optional)

---

## Rate Limiting

- **Read Operations** (GET): 100 requests per minute per user
- **Write Operations** (POST, PUT, PATCH, DELETE): 30 requests per minute per user

**Rate Limit Headers**:
```
X-RateLimit-Limit: 30
X-RateLimit-Remaining: 29
X-RateLimit-Reset: 1733485260
```
