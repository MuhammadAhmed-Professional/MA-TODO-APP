"""Storage layer for task management.

This module provides an abstract storage interface and an in-memory implementation
for managing tasks. The abstraction allows future database implementations without
modifying business logic.
"""

from abc import ABC, abstractmethod
from typing import Optional
from .models import Task


class TaskStorage(ABC):
    """Abstract base class for task storage operations."""

    @abstractmethod
    def add(self, title: str, description: str = "") -> Task:
        """Create and store a new task with auto-generated ID.

        Callers do not provide task IDs; the storage layer creates
        the Task object internally with an auto-incremented ID.
        Returns the newly created Task with assigned ID.

        Args:
            title: The task title (1-200 characters)
            description: Optional task description (max 1000 characters)

        Returns:
            The newly created Task with assigned ID
        """
        ...

    @abstractmethod
    def get(self, task_id: int) -> Optional[Task]:
        """Retrieve a task by its ID.

        Args:
            task_id: The unique task identifier

        Returns:
            The Task if found, None otherwise
        """
        ...

    @abstractmethod
    def get_all(self) -> list[Task]:
        """Retrieve all tasks sorted by ID (ascending).

        Returns:
            List of all tasks ordered by ID
        """
        ...

    @abstractmethod
    def update(
        self, task_id: int, title: Optional[str] = None, description: Optional[str] = None
    ) -> bool:
        """Update a task's title and/or description.

        Args:
            task_id: The task ID to update
            title: New title (None to keep current)
            description: New description (None to keep current)

        Returns:
            True if task was updated, False if task not found
        """
        ...

    @abstractmethod
    def delete(self, task_id: int) -> bool:
        """Delete a task by ID.

        Args:
            task_id: The task ID to delete

        Returns:
            True if task was deleted, False if task not found
        """
        ...

    @abstractmethod
    def toggle_complete(self, task_id: int) -> bool:
        """Toggle the completion status of a task.

        Args:
            task_id: The task ID to toggle

        Returns:
            True if task was toggled, False if task not found
        """
        ...


class InMemoryStorage(TaskStorage):
    """In-memory implementation of TaskStorage using dict.

    Tasks are stored in a dictionary keyed by task ID. IDs are auto-incremented
    and never reused after deletion to maintain consistency and avoid confusion.
    """

    def __init__(self) -> None:
        """Initialize empty storage with ID counter starting at 1."""
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def add(self, title: str, description: str = "") -> Task:
        """Create and store a new task with auto-generated ID.

        Args:
            title: The task title
            description: Optional task description (defaults to empty string)

        Returns:
            The newly created Task with assigned ID
        """
        task = Task(
            id=self._next_id, title=title, description=description, completed=False
        )
        self._tasks[self._next_id] = task
        self._next_id += 1
        return task

    def get(self, task_id: int) -> Optional[Task]:
        """Retrieve a task by its ID.

        Args:
            task_id: The unique task identifier

        Returns:
            The Task if found, None otherwise
        """
        return self._tasks.get(task_id)

    def get_all(self) -> list[Task]:
        """Retrieve all tasks sorted by ID (ascending).

        Returns:
            List of all tasks ordered by ID
        """
        return sorted(self._tasks.values(), key=lambda task: task.id)

    def update(
        self, task_id: int, title: Optional[str] = None, description: Optional[str] = None
    ) -> bool:
        """Update a task's title and/or description.

        Args:
            task_id: The task ID to update
            title: New title (None to keep current)
            description: New description (None to keep current)

        Returns:
            True if task was updated, False if task not found
        """
        task = self._tasks.get(task_id)
        if task is None:
            return False

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description

        return True

    def delete(self, task_id: int) -> bool:
        """Delete a task by ID.

        Args:
            task_id: The task ID to delete

        Returns:
            True if task was deleted, False if task not found
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def toggle_complete(self, task_id: int) -> bool:
        """Toggle the completion status of a task.

        Args:
            task_id: The task ID to toggle

        Returns:
            True if task was toggled, False if task not found
        """
        task = self._tasks.get(task_id)
        if task is None:
            return False

        task.completed = not task.completed
        return True
