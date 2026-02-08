"""Business logic operations for task management.

This module contains validation functions and business logic operations
that coordinate between the UI layer and storage layer.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .storage import TaskStorage
    from .models import Task


class ValidationError(Exception):
    """Custom exception raised for invalid input data."""

    pass


class TaskNotFoundError(Exception):
    """Custom exception raised when a task ID is not found."""

    pass


def validate_title(title: str) -> str:
    """Validate task title meets requirements.

    Args:
        title: The task title to validate

    Returns:
        The validated title (stripped of leading/trailing whitespace)

    Raises:
        ValidationError: If title is empty/whitespace-only or exceeds 200 characters
    """
    cleaned = title.strip()

    if not cleaned:
        raise ValidationError("Title cannot be empty")

    if len(cleaned) > 200:
        raise ValidationError("Title must be between 1-200 characters")

    return cleaned


def validate_description(description: str) -> str:
    """Validate task description meets requirements.

    Args:
        description: The task description to validate (can be empty)

    Returns:
        The validated description

    Raises:
        ValidationError: If description exceeds 1000 characters
    """
    if len(description) > 1000:
        raise ValidationError("Description cannot exceed 1000 characters")

    return description


def create_task(
    storage: "TaskStorage", title: str, description: str = ""
) -> "Task":
    """Create a new task with validation.

    This function validates inputs, creates a task via the storage layer,
    and returns the created task with its assigned ID.

    Args:
        storage: The storage instance to use for task creation
        title: The task title (1-200 characters, will be stripped)
        description: Optional task description (max 1000 characters, defaults to empty)

    Returns:
        The newly created Task with assigned ID

    Raises:
        ValidationError: If title or description fail validation
    """
    # Validate inputs
    validated_title = validate_title(title)
    validated_description = validate_description(description)

    # Create task via storage layer
    task = storage.add(validated_title, validated_description)

    return task


def list_tasks(storage: "TaskStorage") -> list["Task"]:
    """Retrieve all tasks from storage.

    This function delegates to the storage layer's get_all() method
    to retrieve all tasks sorted by ID in ascending order.

    Args:
        storage: The storage instance to retrieve tasks from

    Returns:
        List of all tasks sorted by ID (empty list if no tasks exist)
    """
    return storage.get_all()


def toggle_task_complete(storage: "TaskStorage", task_id: int) -> None:
    """Toggle the completion status of a task.

    This function changes the task's completed status from True to False
    or from False to True.

    Args:
        storage: The storage instance to use
        task_id: The ID of the task to toggle

    Raises:
        TaskNotFoundError: If the task ID does not exist
    """
    success = storage.toggle_complete(task_id)

    if not success:
        raise TaskNotFoundError(f"Task with ID {task_id} not found")


def update_task(
    storage: "TaskStorage",
    task_id: int,
    title: str | None = None,
    description: str | None = None,
) -> None:
    """Update a task's title and/or description with validation.

    This function validates any new values provided and updates the task.
    Fields set to None are not updated (current values retained).

    Args:
        storage: The storage instance to use
        task_id: The ID of the task to update
        title: New title (None to keep current), validated if provided
        description: New description (None to keep current), validated if provided

    Raises:
        TaskNotFoundError: If the task ID does not exist
        ValidationError: If new title or description fail validation
    """
    # Validate new values if provided
    validated_title = None
    validated_description = None

    if title is not None:
        validated_title = validate_title(title)

    if description is not None:
        validated_description = validate_description(description)

    # Update via storage layer
    success = storage.update(task_id, validated_title, validated_description)

    if not success:
        raise TaskNotFoundError(f"Task with ID {task_id} not found")


def delete_task(storage: "TaskStorage", task_id: int) -> None:
    """Delete a task from storage.

    Args:
        storage: The storage instance to use
        task_id: The ID of the task to delete

    Raises:
        TaskNotFoundError: If the task ID does not exist
    """
    success = storage.delete(task_id)

    if not success:
        raise TaskNotFoundError(f"Task with ID {task_id} not found")