"""
Tag API Endpoints

Thin controllers for tag CRUD operations.
All business logic delegated to TagService.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.auth.dependencies import get_current_user
from src.models.tag import Tag, TagCreate, TagResponse, TagUpdate
from src.models.task import TaskResponse
from src.models.user import User
from src.services.tag_service import TagService
from src.services.task_service import TaskService

router = APIRouter(prefix="/api/tags", tags=["tags"])


@router.get(
    "",
    response_model=List[TagResponse],
    status_code=200,
    responses={
        200: {
            "description": "List of tags",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "750e8400-e29b-41d4-a716-446655440002",
                            "name": "work",
                            "color": "#3b82f6",
                            "user_id": "550e8400-e29b-41d4-a716-446655440000",
                        }
                    ]
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
    },
)
async def list_tags(
    current_user: User = Depends(get_current_user),
    tag_service: TagService = Depends(),
):
    """
    Get all tags for authenticated user.

    Retrieves all tags owned by the current authenticated user.
    Tags are sorted alphabetically by name.

    **Response:**
    - 200: Array of tags
    - 401: Not authenticated (missing or invalid auth token)

    **Authentication:**
    - Requires valid JWT token in "auth_token" cookie

    **Example:**
    ```
    GET /api/tags
    Cookie: auth_token=eyJhbGc...

    Response 200:
    [
        {
            "id": "750e8400-e29b-41d4-a716-446655440002",
            "name": "work",
            "color": "#3b82f6",
            "user_id": "550e8400-e29b-41d4-a716-446655440000"
        }
    ]
    ```
    """
    tags = await tag_service.get_user_tags(current_user.id)
    return tags


@router.post(
    "",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Tag created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "750e8400-e29b-41d4-a716-446655440002",
                        "name": "work",
                        "color": "#3b82f6",
                        "user_id": "550e8400-e29b-41d4-a716-446655440000",
                    }
                }
            },
        },
        400: {
            "description": "Validation error or tag already exists",
            "content": {
                "application/json": {
                    "example": {"detail": "Tag 'work' already exists"}
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
    },
)
async def create_tag(
    tag_data: TagCreate,
    current_user: User = Depends(get_current_user),
    tag_service: TagService = Depends(),
):
    """
    Create new tag for authenticated user.

    Creates a new tag owned by the authenticated user. Tag names
    are unique per user (case-insensitive).

    **Request Body:**
    - name: Tag name (required, 1-50 characters)
    - color: Tag color as hex code (default: #3b82f6)

    **Response:**
    - 201: Tag created successfully
    - 400: Validation error or tag name already exists
    - 401: Not authenticated

    **Authentication:**
    - Requires valid JWT token in "auth_token" cookie

    **Example:**
    ```json
    POST /api/tags
    Cookie: auth_token=eyJhbGc...
    {
        "name": "work",
        "color": "#3b82f6"
    }

    Response 201:
    {
        "id": "750e8400-e29b-41d4-a716-446655440002",
        "name": "work",
        "color": "#3b82f6",
        "user_id": "550e8400-e29b-41d4-a716-446655440000"
    }
    ```
    """
    try:
        tag = await tag_service.create_tag(tag_data, current_user.id)
        return tag
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{tag_id}",
    response_model=TagResponse,
    status_code=200,
    responses={
        200: {
            "description": "Tag retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "750e8400-e29b-41d4-a716-446655440002",
                        "name": "work",
                        "color": "#3b82f6",
                        "user_id": "550e8400-e29b-41d4-a716-446655440000",
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
            "description": "Forbidden - tag belongs to different user",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authorized to access this tag"}
                }
            },
        },
        404: {
            "description": "Tag not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Tag not found"}
                }
            },
        },
    },
)
async def get_tag(
    tag_id: str,
    current_user: User = Depends(get_current_user),
    tag_service: TagService = Depends(),
):
    """
    Get single tag by ID.

    Retrieves a specific tag by its UUID with automatic ownership verification.
    Only the tag owner can retrieve the tag.

    **Path Parameters:**
    - tag_id: UUID of the tag to retrieve

    **Response:**
    - 200: Tag data retrieved successfully
    - 401: Not authenticated
    - 403: Forbidden (tag belongs to different user)
    - 404: Tag not found

    **Authentication:**
    - Requires valid JWT token in "auth_token" cookie

    **Example:**
    ```
    GET /api/tags/750e8400-e29b-41d4-a716-446655440002
    Cookie: auth_token=eyJhbGc...

    Response 200:
    {
        "id": "750e8400-e29b-41d4-a716-446655440002",
        "name": "work",
        "color": "#3b82f6",
        "user_id": "550e8400-e29b-41d4-a716-446655440000"
    }
    ```
    """
    tag = await tag_service.get_tag(tag_id, current_user.id)
    return tag


@router.put(
    "/{tag_id}",
    response_model=TagResponse,
    status_code=200,
    responses={
        200: {
            "description": "Tag updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "750e8400-e29b-41d4-a716-446655440002",
                        "name": "personal",
                        "color": "#22c55e",
                        "user_id": "550e8400-e29b-41d4-a716-446655440000",
                    }
                }
            },
        },
        400: {
            "description": "Validation error or tag name already exists",
            "content": {
                "application/json": {
                    "example": {"detail": "Tag 'personal' already exists"}
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
            "description": "Forbidden - tag belongs to different user",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authorized to access this tag"}
                }
            },
        },
        404: {
            "description": "Tag not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Tag not found"}
                }
            },
        },
    },
)
async def update_tag(
    tag_id: str,
    tag_data: TagUpdate,
    current_user: User = Depends(get_current_user),
    tag_service: TagService = Depends(),
):
    """
    Update tag fields.

    Performs partial update of tag properties. Only fields provided in the
    request body are updated.

    **Path Parameters:**
    - tag_id: UUID of the tag to update

    **Request Body (all fields optional):**
    - name: New tag name (1-50 characters if provided)
    - color: New tag color (hex code if provided)

    **Response:**
    - 200: Tag updated successfully
    - 400: Validation error or tag name conflict
    - 401: Not authenticated
    - 403: Forbidden (tag belongs to different user)
    - 404: Tag not found

    **Authentication:**
    - Requires valid JWT token in "auth_token" cookie

    **Example:**
    ```json
    PUT /api/tags/750e8400-e29b-41d4-a716-446655440002
    Cookie: auth_token=eyJhbGc...
    {
        "name": "personal",
        "color": "#22c55e"
    }

    Response 200:
    {
        "id": "750e8400-e29b-41d4-a716-446655440002",
        "name": "personal",
        "color": "#22c55e",
        "user_id": "550e8400-e29b-41d4-a716-446655440000"
    }
    ```
    """
    try:
        tag = await tag_service.update_tag(tag_id, tag_data, current_user.id)
        return tag
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {
            "description": "Tag deleted successfully (no content)",
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
            "description": "Forbidden - tag belongs to different user",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authorized to access this tag"}
                }
            },
        },
        404: {
            "description": "Tag not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Tag not found"}
                }
            },
        },
    },
)
async def delete_tag(
    tag_id: str,
    current_user: User = Depends(get_current_user),
    tag_service: TagService = Depends(),
):
    """
    Delete tag permanently.

    Removes the tag from the database permanently. All task-tag associations
    for this tag are also removed (tasks are not deleted). This operation
    cannot be undone. No response body is returned on success.

    **Path Parameters:**
    - tag_id: UUID of the tag to delete

    **Response:**
    - 204: Tag deleted successfully (no content)
    - 401: Not authenticated
    - 403: Forbidden (tag belongs to different user)
    - 404: Tag not found

    **Authentication:**
    - Requires valid JWT token in "auth_token" cookie

    **Example:**
    ```
    DELETE /api/tags/750e8400-e29b-41d4-a716-446655440002
    Cookie: auth_token=eyJhbGc...

    Response 204: (no content)
    ```
    """
    await tag_service.delete_tag(tag_id, current_user.id)
    return None


# Task-Tag Association Endpoints


@router.post(
    "/tasks/{task_id}/tags/{tag_id}",
    response_model=TaskResponse,
    status_code=200,
    responses={
        200: {
            "description": "Tag added to task successfully",
        },
        400: {
            "description": "Tag is already on task",
            "content": {
                "application/json": {
                    "example": {"detail": "Tag is already on this task"}
                }
            },
        },
        401: {
            "description": "Not authenticated",
        },
        403: {
            "description": "Forbidden - task or tag belongs to different user",
        },
        404: {
            "description": "Task or tag not found",
        },
    },
)
async def add_tag_to_task(
    task_id: str,
    tag_id: str,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(),
):
    """
    Add a tag to a task.

    Associates a tag with a task. Both the task and tag must belong to
    the authenticated user.

    **Path Parameters:**
    - task_id: UUID of the task
    - tag_id: UUID of the tag to add

    **Response:**
    - 200: Tag added successfully (returns updated task)
    - 400: Tag is already on this task
    - 401: Not authenticated
    - 403: Forbidden
    - 404: Task or tag not found

    **Authentication:**
    - Requires valid JWT token in "auth_token" cookie

    **Example:**
    ```
    POST /api/tags/tasks/650e8400-e29b-41d4-a716-446655440001/tags/750e8400-e29b-41d4-a716-446655440002
    Cookie: auth_token=eyJhbGc...

    Response 200:
    {
        "id": "650e8400-e29b-41d4-a716-446655440001",
        "title": "Complete project documentation",
        ...
        "tags": [
            {
                "id": "750e8400-e29b-41d4-a716-446655440002",
                "name": "work",
                "color": "#3b82f6"
            }
        ]
    }
    ```
    """
    try:
        task = await task_service.add_tag_to_task(task_id, tag_id, current_user.id)
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/tasks/{task_id}/tags/{tag_id}",
    response_model=TaskResponse,
    status_code=200,
    responses={
        200: {
            "description": "Tag removed from task successfully",
        },
        400: {
            "description": "Tag is not on task",
            "content": {
                "application/json": {
                    "example": {"detail": "Tag is not on this task"}
                }
            },
        },
        401: {
            "description": "Not authenticated",
        },
        403: {
            "description": "Forbidden - task belongs to different user",
        },
        404: {
            "description": "Task not found",
        },
    },
)
async def remove_tag_from_task(
    task_id: str,
    tag_id: str,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(),
):
    """
    Remove a tag from a task.

    Removes the association between a tag and a task. The task and tag
    themselves are not deleted.

    **Path Parameters:**
    - task_id: UUID of the task
    - tag_id: UUID of the tag to remove

    **Response:**
    - 200: Tag removed successfully (returns updated task)
    - 400: Tag is not on this task
    - 401: Not authenticated
    - 403: Forbidden
    - 404: Task not found

    **Authentication:**
    - Requires valid JWT token in "auth_token" cookie

    **Example:**
    ```
    DELETE /api/tags/tasks/650e8400-e29b-41d4-a716-446655440001/tags/750e8400-e29b-41d4-a716-446655440002
    Cookie: auth_token=eyJhbGc...

    Response 200:
    {
        "id": "650e8400-e29b-41d4-a716-446655440001",
        "title": "Complete project documentation",
        ...
        "tags": []
    }
    ```
    """
    try:
        task = await task_service.remove_tag_from_task(task_id, tag_id, current_user.id)
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/tasks/{task_id}/tags",
    response_model=TaskResponse,
    status_code=200,
    responses={
        200: {
            "description": "Task tags updated successfully",
        },
        400: {
            "description": "Invalid tag IDs",
            "content": {
                "application/json": {
                    "example": {"detail": "One or more tag IDs are invalid or don't belong to user"}
                }
            },
        },
        401: {
            "description": "Not authenticated",
        },
        403: {
            "description": "Forbidden - task belongs to different user",
        },
        404: {
            "description": "Task not found",
        },
    },
)
async def set_task_tags(
    task_id: str,
    tag_ids: List[str],
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends(),
):
    """
    Replace all tags on a task.

    Removes all existing tags from the task and adds the provided tags.
    Use this to completely replace the task's tags.

    **Path Parameters:**
    - task_id: UUID of the task

    **Request Body:**
    - tag_ids: Array of tag UUIDs to set on the task

    **Response:**
    - 200: Tags updated successfully (returns updated task)
    - 400: Invalid tag IDs
    - 401: Not authenticated
    - 403: Forbidden
    - 404: Task not found

    **Authentication:**
    - Requires valid JWT token in "auth_token" cookie

    **Example:**
    ```json
    PUT /api/tags/tasks/650e8400-e29b-41d4-a716-446655440001/tags
    Cookie: auth_token=eyJhbGc...
    {
        "tag_ids": [
            "750e8400-e29b-41d4-a716-446655440002",
            "750e8400-e29b-41d4-a716-446655440003"
        ]
    }

    Response 200:
    {
        "id": "650e8400-e29b-41d4-a716-446655440001",
        "title": "Complete project documentation",
        ...
        "tags": [
            {"id": "...", "name": "work", "color": "#3b82f6"},
            {"id": "...", "name": "urgent", "color": "#ef4444"}
        ]
    }
    ```
    """
    try:
        task = await task_service.set_task_tags(task_id, tag_ids, current_user.id)
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
