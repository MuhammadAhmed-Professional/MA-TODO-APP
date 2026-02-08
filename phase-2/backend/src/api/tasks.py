"""
Task API Endpoints

Thin controllers for task CRUD operations.
All business logic delegated to TaskService.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.dependencies import get_event_publisher
from src.auth.dependencies import get_current_user
from src.events.dapr_publisher import DaprEventPublisher
from src.models.priority import Priority
from src.models.task import Task, TaskCreate, TaskResponse, TaskToggleComplete, TaskUpdate
from src.models.user import User
from src.services.task_service import TaskService

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get(
    "",
    response_model=List[TaskResponse],
    status_code=200,
    responses={
        200: {
            "description": "List of tasks",
        },
        401: {
            "description": "Not authenticated",
        },
    },
)
async def list_tasks(
    is_complete: Optional[bool] = Query(None, description="Filter by completion status"),
    priority: Optional[int] = Query(None, ge=Priority.LOW, le=Priority.HIGH, description="Filter by priority (1=low, 2=medium, 3=high)"),
    tags: Optional[str] = Query(None, description="Filter by tag IDs (comma-separated)"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    due_date_before: Optional[datetime] = Query(None, description="Filter by due date before (ISO 8601)"),
    due_date_after: Optional[datetime] = Query(None, description="Filter by due date after (ISO 8601)"),
    sort_by: str = Query("created_at", description="Sort field (created_at, due_date, priority, title, updated_at)"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order (asc or desc)"),
    limit: int = Query(50, ge=1, le=100, description="Maximum tasks to return"),
    offset: int = Query(0, ge=0, description="Number of tasks to skip"),
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(),
):
    """
    Get all tasks for authenticated user with advanced filtering and sorting.

    Retrieves paginated list of tasks owned by the current authenticated user.
    Supports filtering by completion status, priority, tags, search, and due date.
    Supports sorting by multiple fields.

    **Query Parameters:**
    - is_complete: Optional boolean to filter by completion status
    - priority: Optional priority filter (1=low, 2=medium, 3=high)
    - tags: Comma-separated list of tag IDs to filter (tasks must have ALL tags)
    - search: Search query for title and description (case-insensitive partial match)
    - due_date_before: Filter by due date before this ISO 8601 datetime
    - due_date_after: Filter by due date after this ISO 8601 datetime
    - sort_by: Field to sort by (default: created_at)
    - sort_order: Sort direction (asc or desc, default: desc)
    - limit: Maximum tasks to return (1-100, default: 50)
    - offset: Number of tasks to skip for pagination (default: 0)

    **Response:**
    - 200: Array of tasks matching the filter criteria
    - 401: Not authenticated

    **Authentication:**
    - Requires valid JWT token in "auth_token" cookie

    **Examples:**
    ```
    # Get incomplete high-priority tasks
    GET /api/tasks?is_complete=false&priority=3&sort_by=priority&sort_order=desc

    # Search for tasks with "urgent"
    GET /api/tasks?search=urgent

    # Filter by tags and due date
    GET /api/tasks?tags=tag_id1,tag_id2&due_date_after=2025-12-01T00:00:00Z

    # Sort by due date, oldest first
    GET /api/tasks?sort_by=due_date&sort_order=asc
    ```
    """
    # Parse tags parameter
    tag_ids = None
    if tags:
        tag_ids = [t.strip() for t in tags.split(",") if t.strip()]

    tasks = await task_service.get_user_tasks(
        user_id=current_user.id,
        is_complete=is_complete,
        priority=priority,
        tag_ids=tag_ids,
        search=search,
        due_date_before=due_date_before,
        due_date_after=due_date_after,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset,
    )
    return tasks


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Task created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "650e8400-e29b-41d4-a716-446655440001",
                        "title": "Complete project documentation",
                        "description": "Write comprehensive README and API docs",
                        "is_complete": False,
                        "user_id": "550e8400-e29b-41d4-a716-446655440000",
                        "created_at": "2025-12-07T16:00:00Z",
                        "updated_at": "2025-12-07T16:00:00Z",
                    }
                }
            },
        },
        400: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {"detail": "Title cannot be empty or only whitespace"}
                }
            },
        },
        401: {
            "description": "Not authenticated",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authenticated"}
                }
            },
        },
        422: {
            "description": "Request validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "title"],
                                "msg": "ensure this value has at most 200 characters",
                                "type": "value_error.any_str.max_length",
                            }
                        ]
                    }
                }
            },
        },
    },
)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(),
    event_publisher: DaprEventPublisher = Depends(get_event_publisher),
):
    """
    Create new task for authenticated user.

    Creates a new task owned by the authenticated user with automatic
    timestamp generation and UUID assignment.

    **Request Body:**
    - title: Task title (required, 1-200 characters)
    - description: Task description (optional, max 2000 characters)

    **Response:**
    - 201: Task created successfully (includes generated ID and timestamps)
    - 400: Validation error (empty title, title too long, description too long)
    - 401: Not authenticated (missing or invalid auth token)

    **Authentication:**
    - Requires valid JWT token in "auth_token" cookie

    **Side Effects:**
    - Task ownership is automatically set to current authenticated user
    - is_complete defaults to false
    - created_at and updated_at timestamps are set to current UTC time

    **Example:**
    ```json
    POST /api/tasks
    Cookie: auth_token=eyJhbGc...
    {
        "title": "Complete project documentation",
        "description": "Write comprehensive README and API docs"
    }

    Response 201:
    {
        "id": "650e8400-e29b-41d4-a716-446655440001",
        "title": "Complete project documentation",
        "description": "Write comprehensive README and API docs",
        "is_complete": false,
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "created_at": "2025-12-07T16:00:00Z",
        "updated_at": "2025-12-07T16:00:00Z"
    }
    ```
    """
    try:
        task = await task_service.create_task(task_data, current_user.id)

        # Publish task.created event (fire-and-forget, non-blocking)
        await event_publisher.publish_task_event(
            event_type="task.created",
            task_data={
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": task.is_complete,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "user_id": task.user_id,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
            },
            user_id=current_user.id,
        )

        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=200,
    responses={
        200: {
            "description": "Task retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "650e8400-e29b-41d4-a716-446655440001",
                        "title": "Complete project documentation",
                        "description": "Write comprehensive README and API docs",
                        "is_complete": False,
                        "user_id": "550e8400-e29b-41d4-a716-446655440000",
                        "created_at": "2025-12-07T16:00:00Z",
                        "updated_at": "2025-12-07T16:00:00Z",
                    }
                }
            },
        },
        401: {
            "description": "Not authenticated",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authenticated"}
                }
            },
        },
        403: {
            "description": "Forbidden - task belongs to different user",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authorized to access this task"}
                }
            },
        },
        404: {
            "description": "Task not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Task not found"}
                }
            },
        },
    },
)
async def get_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(),
):
    """
    Get single task by ID.

    Retrieves a specific task by its UUID with automatic ownership verification.
    Only the task owner can retrieve the task.

    **Path Parameters:**
    - task_id: UUID of the task to retrieve

    **Response:**
    - 200: Task data retrieved successfully
    - 401: Not authenticated (missing or invalid auth token)
    - 403: Forbidden (task belongs to different user)
    - 404: Task not found

    **Authentication:**
    - Requires valid JWT token in "auth_token" cookie

    **Authorization:**
    - User must own the task (task.user_id must match current_user.id)

    **Example:**
    ```
    GET /api/tasks/650e8400-e29b-41d4-a716-446655440001
    Cookie: auth_token=eyJhbGc...

    Response 200:
    {
        "id": "650e8400-e29b-41d4-a716-446655440001",
        "title": "Complete project documentation",
        "description": "Write comprehensive README and API docs",
        "is_complete": false,
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "created_at": "2025-12-07T16:00:00Z",
        "updated_at": "2025-12-07T16:00:00Z"
    }
    ```
    """
    task = await task_service.get_task(task_id, current_user.id)
    return task


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=200,
    responses={
        200: {
            "description": "Task updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "650e8400-e29b-41d4-a716-446655440001",
                        "title": "Complete project documentation (updated)",
                        "description": "Write README, API docs, and deployment guide",
                        "is_complete": False,
                        "user_id": "550e8400-e29b-41d4-a716-446655440000",
                        "created_at": "2025-12-07T16:00:00Z",
                        "updated_at": "2025-12-07T16:30:00Z",
                    }
                }
            },
        },
        400: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {"detail": "Title cannot be empty or only whitespace"}
                }
            },
        },
        401: {
            "description": "Not authenticated",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authenticated"}
                }
            },
        },
        403: {
            "description": "Forbidden - task belongs to different user",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authorized to access this task"}
                }
            },
        },
        404: {
            "description": "Task not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Task not found"}
                }
            },
        },
    },
)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(),
    event_publisher: DaprEventPublisher = Depends(get_event_publisher),
):
    """
    Update task fields.

    Performs partial update of task properties. Only fields provided in the
    request body are updated. The updated_at timestamp is automatically set
    to the current UTC time.

    **Path Parameters:**
    - task_id: UUID of the task to update

    **Request Body (all fields optional):**
    - title: New task title (1-200 characters if provided)
    - description: New task description (max 2000 characters if provided)

    **Response:**
    - 200: Task updated successfully
    - 400: Validation error (empty title, title too long, etc.)
    - 401: Not authenticated (missing or invalid auth token)
    - 403: Forbidden (task belongs to different user)
    - 404: Task not found

    **Authentication:**
    - Requires valid JWT token in "auth_token" cookie

    **Authorization:**
    - User must own the task (task.user_id must match current_user.id)

    **Side Effects:**
    - updated_at timestamp is set to current UTC time
    - Title and description are trimmed of leading/trailing whitespace

    **Example:**
    ```json
    PUT /api/tasks/650e8400-e29b-41d4-a716-446655440001
    Cookie: auth_token=eyJhbGc...
    {
        "title": "Complete project documentation (updated)",
        "description": "Write README, API docs, and deployment guide"
    }

    Response 200:
    {
        "id": "650e8400-e29b-41d4-a716-446655440001",
        "title": "Complete project documentation (updated)",
        "description": "Write README, API docs, and deployment guide",
        "is_complete": false,
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "created_at": "2025-12-07T16:00:00Z",
        "updated_at": "2025-12-07T16:30:00Z"
    }
    ```
    """
    try:
        task = await task_service.update_task(task_id, task_data, current_user.id)

        # Publish task.updated event (fire-and-forget, non-blocking)
        await event_publisher.publish_task_event(
            event_type="task.updated",
            task_data={
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": task.is_complete,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "user_id": task.user_id,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
            },
            user_id=current_user.id,
        )

        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=200,
    responses={
        200: {
            "description": "Task updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "650e8400-e29b-41d4-a716-446655440001",
                        "title": "Complete project documentation (updated)",
                        "description": "Write README, API docs, and deployment guide",
                        "is_complete": True,
                        "user_id": "550e8400-e29b-41d4-a716-446655440000",
                        "created_at": "2025-12-07T16:00:00Z",
                        "updated_at": "2025-12-07T16:30:00Z",
                    }
                }
            },
        },
        400: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {"detail": "Title cannot be empty or only whitespace"}
                }
            },
        },
        401: {
            "description": "Not authenticated",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authenticated"}
                }
            },
        },
        403: {
            "description": "Forbidden - task belongs to different user",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authorized to access this task"}
                }
            },
        },
        404: {
            "description": "Task not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Task not found"}
                }
            },
        },
    },
)
async def patch_task(
    task_id: str,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(),
    event_publisher: DaprEventPublisher = Depends(get_event_publisher),
):
    """
    Partially update task fields (PATCH method).

    Performs partial update of task properties including completion status.
    Only fields provided in the request body are updated. The updated_at
    timestamp is automatically set to the current UTC time.

    This endpoint accepts the same updates as PUT but follows REST semantics
    for partial updates. Supports updating title, description, and is_complete.

    **Path Parameters:**
    - task_id: UUID of the task to update

    **Request Body (all fields optional):**
    - title: New task title (1-200 characters if provided)
    - description: New task description (max 2000 characters if provided)
    - is_complete: Mark task complete (true) or incomplete (false)

    **Response:**
    - 200: Task updated successfully
    - 400: Validation error (empty title, title too long, etc.)
    - 401: Not authenticated (missing or invalid auth token)
    - 403: Forbidden (task belongs to different user)
    - 404: Task not found

    **Authentication:**
    - Requires valid JWT token in "auth_token" cookie or Authorization header

    **Authorization:**
    - User must own the task (task.user_id must match current_user.id)

    **Side Effects:**
    - updated_at timestamp is set to current UTC time
    - Title and description are trimmed of leading/trailing whitespace

    **Example:**
    ```json
    PATCH /api/tasks/650e8400-e29b-41d4-a716-446655440001
    Authorization: Bearer eyJhbGc...
    {
        "title": "Complete project documentation (updated)",
        "is_complete": true
    }

    Response 200:
    {
        "id": "650e8400-e29b-41d4-a716-446655440001",
        "title": "Complete project documentation (updated)",
        "description": "Write README, API docs, and deployment guide",
        "is_complete": true,
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "created_at": "2025-12-07T16:00:00Z",
        "updated_at": "2025-12-07T16:30:00Z"
    }
    ```
    """
    try:
        task = await task_service.update_task(task_id, task_data, current_user.id)

        # Publish task.updated event (fire-and-forget, non-blocking)
        # Note: If only is_complete changed to True, this will also trigger task.completed
        await event_publisher.publish_task_event(
            event_type="task.updated",
            task_data={
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": task.is_complete,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "user_id": task.user_id,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
            },
            user_id=current_user.id,
        )

        # If task was marked complete, also publish task.completed event
        if task.is_complete:
            await event_publisher.publish_task_event(
                event_type="task.completed",
                task_data={
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "is_complete": task.is_complete,
                    "priority": task.priority,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "user_id": task.user_id,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat(),
                },
                user_id=current_user.id,
            )

        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch(
    "/{task_id}/complete",
    response_model=TaskResponse,
    status_code=200,
    responses={
        200: {
            "description": "Task completion status updated",
            "content": {
                "application/json": {
                    "example": {
                        "id": "650e8400-e29b-41d4-a716-446655440001",
                        "title": "Complete project documentation",
                        "description": "Write comprehensive README and API docs",
                        "is_complete": True,
                        "user_id": "550e8400-e29b-41d4-a716-446655440000",
                        "created_at": "2025-12-07T16:00:00Z",
                        "updated_at": "2025-12-07T16:45:00Z",
                    }
                }
            },
        },
        401: {
            "description": "Not authenticated",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authenticated"}
                }
            },
        },
        403: {
            "description": "Forbidden - task belongs to different user",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authorized to access this task"}
                }
            },
        },
        404: {
            "description": "Task not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Task not found"}
                }
            },
        },
    },
)
async def toggle_task_complete(
    task_id: str,
    toggle_data: TaskToggleComplete,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(),
    event_publisher: DaprEventPublisher = Depends(get_event_publisher),
):
    """
    Toggle task completion status.

    Updates the is_complete field to mark a task as complete or incomplete.
    The updated_at timestamp is automatically updated to reflect the change.

    **Path Parameters:**
    - task_id: UUID of the task to update

    **Request Body:**
    - is_complete: Boolean indicating new completion status (true = complete, false = incomplete)

    **Response:**
    - 200: Task completion status updated successfully
    - 401: Not authenticated (missing or invalid auth token)
    - 403: Forbidden (task belongs to different user)
    - 404: Task not found

    **Authentication:**
    - Requires valid JWT token in "auth_token" cookie

    **Authorization:**
    - User must own the task (task.user_id must match current_user.id)

    **Side Effects:**
    - updated_at timestamp is set to current UTC time
    - is_complete field is set to the provided value

    **Example:**
    ```json
    PATCH /api/tasks/650e8400-e29b-41d4-a716-446655440001/complete
    Cookie: auth_token=eyJhbGc...
    {
        "is_complete": true
    }

    Response 200:
    {
        "id": "650e8400-e29b-41d4-a716-446655440001",
        "title": "Complete project documentation",
        "description": "Write comprehensive README and API docs",
        "is_complete": true,
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "created_at": "2025-12-07T16:00:00Z",
        "updated_at": "2025-12-07T16:45:00Z"
    }
    ```
    """
    task = await task_service.toggle_complete(
        task_id, toggle_data.is_complete, current_user.id
    )

    # Publish appropriate event based on new completion status
    if toggle_data.is_complete:
        # Task was completed
        await event_publisher.publish_task_event(
            event_type="task.completed",
            task_data={
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": task.is_complete,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "user_id": task.user_id,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
            },
            user_id=current_user.id,
        )
    else:
        # Task was uncompleted (still publish as updated event)
        await event_publisher.publish_task_event(
            event_type="task.updated",
            task_data={
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "is_complete": task.is_complete,
                "priority": task.priority,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "user_id": task.user_id,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
            },
            user_id=current_user.id,
        )

    return task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {
            "description": "Task deleted successfully (no content)",
        },
        401: {
            "description": "Not authenticated",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authenticated"}
                }
            },
        },
        403: {
            "description": "Forbidden - task belongs to different user",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authorized to access this task"}
                }
            },
        },
        404: {
            "description": "Task not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Task not found"}
                }
            },
        },
    },
)
async def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(),
    event_publisher: DaprEventPublisher = Depends(get_event_publisher),
):
    """
    Delete task permanently.

    Removes the task from the database permanently. This operation cannot be
    undone. No response body is returned on success.

    **Path Parameters:**
    - task_id: UUID of the task to delete

    **Response:**
    - 204: Task deleted successfully (no content)
    - 401: Not authenticated (missing or invalid auth token)
    - 403: Forbidden (task belongs to different user)
    - 404: Task not found

    **Authentication:**
    - Requires valid JWT token in "auth_token" cookie

    **Authorization:**
    - User must own the task (task.user_id must match current_user.id)

    **Side Effects:**
    - Task is permanently removed from the database
    - Operation is irreversible

    **Example:**
    ```
    DELETE /api/tasks/650e8400-e29b-41d4-a716-446655440001
    Cookie: auth_token=eyJhbGc...

    Response 204: (no content)
    ```
    """
    # Get task before deletion for event publishing
    task = await task_service.get_task(task_id, current_user.id)

    # Delete the task
    await task_service.delete_task(task_id, current_user.id)

    # Publish task.deleted event (fire-and-forget, non-blocking)
    await event_publisher.publish_task_event(
        event_type="task.deleted",
        task_data={
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.is_complete,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "user_id": task.user_id,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
        },
        user_id=current_user.id,
    )

    return None
