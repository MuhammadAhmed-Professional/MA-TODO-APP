# Python CRUD Implementation Patterns Skill

## Purpose
Implement production-ready Create-Read-Update-Delete operations with validation, error handling, and clean separation of concerns for various data persistence backends.

## When to Use
- Building data access layers
- Implementing repository/storage patterns
- Creating data persistence abstractions
- Ensuring data integrity during operations
- Migrating between storage backends

## Prerequisites
- Python 3.13+ with type hints
- Understanding of CRUD principles
- Familiarity with exception handling
- Knowledge of abstract base classes (ABC)

## Architecture

### CRUD Layer Structure
```
Storage Layer
├── Abstract Interface (ABC)
│   ├── create() / add()
│   ├── read() / get()
│   ├── update()
│   ├── delete()
│   └── list() / get_all()
├── In-Memory Implementation
│   └── For development/testing
├── File-Based Implementation
│   └── JSON/CSV persistence
└── Database Implementation
    └── SQLite/PostgreSQL
```

## Workflow

### Phase 1: Define the Storage Interface

```python
# src/todo_app/storage.py
from abc import ABC, abstractmethod
from typing import Optional
from .models import Task

class TaskStorage(ABC):
    """Abstract storage interface for tasks."""

    @abstractmethod
    def add(self, title: str, description: str = "") -> Task:
        """Create and store a new task.

        Args:
            title: Task title
            description: Optional task description

        Returns:
            The created task with assigned ID
        """
        pass

    @abstractmethod
    def get(self, task_id: int) -> Optional[Task]:
        """Retrieve a task by ID.

        Args:
            task_id: The task ID to retrieve

        Returns:
            The task if found, None otherwise
        """
        pass

    @abstractmethod
    def get_all(self) -> list[Task]:
        """Retrieve all tasks.

        Returns:
            List of all tasks sorted by ID
        """
        pass

    @abstractmethod
    def update(self, task_id: int, title: str | None = None,
               description: str | None = None) -> bool:
        """Update a task's fields.

        Args:
            task_id: The task ID to update
            title: New title (None to keep current)
            description: New description (None to keep current)

        Returns:
            True if updated, False if task not found
        """
        pass

    @abstractmethod
    def delete(self, task_id: int) -> bool:
        """Delete a task by ID.

        Args:
            task_id: The task ID to delete

        Returns:
            True if deleted, False if task not found
        """
        pass

    @abstractmethod
    def toggle_complete(self, task_id: int) -> bool:
        """Toggle task completion status.

        Args:
            task_id: The task ID to toggle

        Returns:
            True if toggled, False if task not found
        """
        pass
```

**Validation**: Verify interface is importable.

### Phase 2: Implement In-Memory Storage

```python
# src/todo_app/storage.py (continued)
from datetime import datetime

class InMemoryStorage(TaskStorage):
    """In-memory task storage using dict."""

    def __init__(self):
        """Initialize empty storage."""
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def add(self, title: str, description: str = "") -> Task:
        """Create and store task with auto-incremented ID."""
        task = Task(
            id=self._next_id,
            title=title,
            description=description,
            completed=False,
            created_at=datetime.now()
        )
        self._tasks[self._next_id] = task
        self._next_id += 1
        return task

    def get(self, task_id: int) -> Optional[Task]:
        """Retrieve task by ID."""
        return self._tasks.get(task_id)

    def get_all(self) -> list[Task]:
        """Return all tasks sorted by ID."""
        return sorted(self._tasks.values(), key=lambda task: task.id)

    def update(self, task_id: int, title: str | None = None,
               description: str | None = None) -> bool:
        """Update task fields."""
        task = self._tasks.get(task_id)
        if task is None:
            return False

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description

        return True

    def delete(self, task_id: int) -> bool:
        """Delete task if exists."""
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def toggle_complete(self, task_id: int) -> bool:
        """Toggle completion status."""
        task = self._tasks.get(task_id)
        if task is None:
            return False
        task.completed = not task.completed
        return True
```

**Validation**: `pytest tests/test_storage.py -v`

### Phase 3: Implement Operations Layer

```python
# src/todo_app/operations.py
from .storage import TaskStorage
from .models import Task

class ValidationError(Exception):
    """Raised when validation fails."""
    pass

class TaskNotFoundError(Exception):
    """Raised when task ID not found."""
    pass

def create_task(storage: TaskStorage, title: str, description: str = "") -> Task:
    """Create task with validation.

    Args:
        storage: Storage instance
        title: Task title (1-200 chars)
        description: Task description (max 1000 chars)

    Returns:
        Created task

    Raises:
        ValidationError: If validation fails
    """
    # Validate inputs
    validated_title = validate_title(title)
    validated_description = validate_description(description)

    # Create via storage layer
    task = storage.add(validated_title, validated_description)
    return task

def list_tasks(storage: TaskStorage) -> list[Task]:
    """Retrieve all tasks."""
    return storage.get_all()

def toggle_task_complete(storage: TaskStorage, task_id: int) -> None:
    """Toggle task completion.

    Raises:
        TaskNotFoundError: If task not found
    """
    success = storage.toggle_complete(task_id)
    if not success:
        raise TaskNotFoundError(f"Task with ID {task_id} not found")

def update_task(storage: TaskStorage, task_id: int,
                title: str | None = None, description: str | None = None) -> None:
    """Update task with validation.

    Raises:
        TaskNotFoundError: If task not found
        ValidationError: If validation fails
    """
    # Validate new values
    validated_title = validate_title(title) if title is not None else None
    validated_description = validate_description(description) if description is not None else None

    # Update via storage
    success = storage.update(task_id, validated_title, validated_description)
    if not success:
        raise TaskNotFoundError(f"Task with ID {task_id} not found")

def delete_task(storage: TaskStorage, task_id: int) -> None:
    """Delete task.

    Raises:
        TaskNotFoundError: If task not found
    """
    success = storage.delete(task_id)
    if not success:
        raise TaskNotFoundError(f"Task with ID {task_id} not found")
```

**Validation**: `pytest tests/test_operations.py -v`

## Best Practices

### Error Handling
```python
# Use custom exceptions
class NotFoundError(Exception): pass
class ValidationError(Exception): pass

# Return False for not found (storage layer)
def delete(self, task_id: int) -> bool:
    if task_id not in self._tasks:
        return False
    del self._tasks[task_id]
    return True

# Raise exceptions (operations layer)
def delete_task(storage: TaskStorage, task_id: int) -> None:
    success = storage.delete(task_id)
    if not success:
        raise TaskNotFoundError(f"Task {task_id} not found")
```

### ID Management
```python
# Auto-increment IDs
class InMemoryStorage:
    def __init__(self):
        self._next_id = 1

    def add(self, title: str, description: str) -> Task:
        task = Task(id=self._next_id, title=title, description=description)
        self._tasks[self._next_id] = task
        self._next_id += 1
        return task

# Never reuse deleted IDs
# IDs should monotonically increase
```

### Validation Separation
```python
# Storage layer: No validation, assumes clean data
def add(self, title: str, description: str) -> Task:
    # No validation here
    task = Task(id=self._next_id, title=title, description=description)
    self._tasks[self._next_id] = task
    self._next_id += 1
    return task

# Operations layer: Validates before calling storage
def create_task(storage: TaskStorage, title: str, description: str) -> Task:
    validated_title = validate_title(title)  # Validate here
    validated_description = validate_description(description)
    return storage.add(validated_title, validated_description)
```

### Partial Updates
```python
# Use None to indicate "no change"
def update(self, task_id: int, title: str | None = None,
           description: str | None = None) -> bool:
    task = self._tasks.get(task_id)
    if not task:
        return False

    # Only update if not None
    if title is not None:
        task.title = title
    if description is not None:
        task.description = description

    return True
```

## Common Patterns

### Pattern 1: Storage Returns None for Not Found
```python
def get(self, task_id: int) -> Optional[Task]:
    """Return task or None if not found."""
    return self._tasks.get(task_id)
```

### Pattern 2: Storage Returns Bool for Success
```python
def delete(self, task_id: int) -> bool:
    """Return True if deleted, False if not found."""
    if task_id in self._tasks:
        del self._tasks[task_id]
        return True
    return False
```

### Pattern 3: Operations Raises Exceptions
```python
def delete_task(storage: TaskStorage, task_id: int) -> None:
    """Raise TaskNotFoundError if not found."""
    success = storage.delete(task_id)
    if not success:
        raise TaskNotFoundError(f"Task {task_id} not found")
```

### Pattern 4: Query Methods
```python
def find_by_status(self, completed: bool) -> list[Task]:
    """Find tasks by completion status."""
    return [t for t in self._tasks.values() if t.completed == completed]

def count(self) -> int:
    """Count total tasks."""
    return len(self._tasks)
```

## Testing Checklist
- ✅ CREATE with valid data succeeds
- ✅ CREATE assigns unique IDs
- ✅ CREATE never reuses deleted IDs
- ✅ READ existing entity returns correct data
- ✅ READ non-existent entity returns None
- ✅ UPDATE existing entity persists changes
- ✅ UPDATE with None keeps current value
- ✅ UPDATE non-existent entity returns False
- ✅ DELETE existing entity removes from storage
- ✅ DELETE non-existent entity returns False
- ✅ LIST returns all entities sorted by ID
- ✅ LIST excludes deleted entities

## Example: Complete CRUD Test Suite

```python
# tests/test_storage.py
import pytest
from src.todo_app.storage import InMemoryStorage

class TestInMemoryStorage:
    """Test CRUD operations."""

    @pytest.fixture
    def storage(self):
        return InMemoryStorage()

    def test_add_assigns_id_and_increments(self, storage):
        """Test ID assignment and auto-increment."""
        task1 = storage.add("First", "Description 1")
        task2 = storage.add("Second", "Description 2")
        assert task1.id == 1
        assert task2.id == 2

    def test_get_existing_returns_task(self, storage):
        """Test retrieving existing task."""
        created = storage.add("Test", "")
        retrieved = storage.get(created.id)
        assert retrieved is not None
        assert retrieved.title == "Test"

    def test_update_modifies_fields(self, storage):
        """Test updating task fields."""
        task = storage.add("Original", "Original desc")
        success = storage.update(task.id, title="Updated")
        assert success is True
        updated = storage.get(task.id)
        assert updated.title == "Updated"

    def test_delete_removes_task(self, storage):
        """Test deleting task."""
        task = storage.add("To Delete", "")
        success = storage.delete(task.id)
        assert success is True
        assert storage.get(task.id) is None
```
