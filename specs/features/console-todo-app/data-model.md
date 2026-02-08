# Data Model: Phase 1 Console Todo Application

**Date**: 2025-12-05
**Feature**: 001-console-todo-app
**Purpose**: Define entities, fields, validation rules, and storage interfaces

## Entity: Task

**Purpose**: Represents a single todo item with title, description, completion status, and metadata.

### Fields

| Field | Type | Required | Constraints | Default | Description |
|-------|------|----------|-------------|---------|-------------|
| `id` | `int` | Yes | Positive integer, unique, never reused | Assigned by storage | Unique identifier for the task |
| `title` | `str` | Yes | 1-200 characters, non-empty after strip | None | Brief description of the task |
| `description` | `str` | No | Max 1000 characters | Empty string `""` | Detailed information about the task |
| `completed` | `bool` | Yes | True or False | `False` | Whether the task is complete |
| `created_at` | `datetime` | Yes | Valid datetime | Current timestamp | When the task was created |

### Dataclass Implementation

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Task:
    """Represents a todo task with metadata."""

    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate field constraints after initialization."""
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")
        if len(self.title) > 200:
            raise ValueError("Title must be between 1-200 characters")
        if len(self.description) > 1000:
            raise ValueError("Description cannot exceed 1000 characters")
```

### Validation Rules

**Title Validation** (enforced in operations layer):
- `validate_title(title: str) -> None`
- Must not be empty or whitespace-only: `if not title.strip()`
- Must be 1-200 characters: `1 <= len(title) <= 200`
- Accepts all valid Unicode characters (emojis, non-Latin scripts)
- Error messages:
  - Empty: "Title cannot be empty"
  - Too long: "Title must be between 1-200 characters"

**Description Validation** (enforced in operations layer):
- `validate_description(description: str) -> None`
- Optional field (empty string is valid)
- Must not exceed 1000 characters: `len(description) <= 1000`
- Accepts all valid Unicode characters
- Error message:
  - Too long: "Description cannot exceed 1000 characters"

**ID Validation** (enforced in operations layer):
- Task IDs must be positive integers: `id > 0`
- Non-numeric input rejected: "Error: Invalid task ID. Please enter a valid number"
- Non-existent IDs rejected: "Error: Task #{id} not found"
- Negative or zero IDs rejected: "Error: Invalid task ID. Please enter a valid number"

### State Transitions

**Completion Status**:
```
[ ] (incomplete) ←→ [✓] (complete)
```
- Default state: `completed=False` ([ ])
- Toggle operation: `task.completed = not task.completed`
- No restrictions on toggling (can complete/uncomplete any number of times)

**Lifecycle**:
```
Created → [Exists] → Deleted
         ↓
      Updated (title/description)
         ↓
      Toggled (completed status)
```
- Tasks cannot be "archived" or "soft deleted" in Phase 1
- Deletion is permanent (task removed from storage)
- Updates do not change `id` or `created_at`
- Completion toggle does not change `id`, `title`, `description`, or `created_at`

## Storage Interface: TaskStorage

**Purpose**: Abstract base class defining storage operations, enabling Phase 2 database migration without business logic changes.

### Interface Definition

```python
from abc import ABC, abstractmethod
from typing import Optional

class TaskStorage(ABC):
    """Abstract base class for task storage operations."""

    @abstractmethod
    def add(self, title: str, description: str = "") -> Task:
        """
        Create and store a new task.

        Args:
            title: Task title (1-200 chars, validated by caller)
            description: Optional task description (max 1000 chars)

        Returns:
            Task: Created task with assigned ID

        Raises:
            ValidationError: If title/description violate constraints
        """
        pass

    @abstractmethod
    def get(self, task_id: int) -> Task | None:
        """
        Retrieve a task by ID.

        Args:
            task_id: Unique task identifier

        Returns:
            Task if found, None otherwise
        """
        pass

    @abstractmethod
    def get_all(self) -> list[Task]:
        """
        Retrieve all tasks, ordered by ID ascending.

        Returns:
            List of tasks sorted by ID (creation order)
        """
        pass

    @abstractmethod
    def update(self, task_id: int, title: str | None = None,
               description: str | None = None) -> bool:
        """
        Update task title and/or description.

        Args:
            task_id: Task to update
            title: New title (None = keep current)
            description: New description (None = keep current)

        Returns:
            True if updated, False if task not found

        Raises:
            ValidationError: If new title/description violate constraints
        """
        pass

    @abstractmethod
    def delete(self, task_id: int) -> bool:
        """
        Permanently delete a task.

        Args:
            task_id: Task to delete

        Returns:
            True if deleted, False if task not found
        """
        pass

    @abstractmethod
    def toggle_complete(self, task_id: int) -> bool:
        """
        Toggle task completion status (incomplete ↔ complete).

        Args:
            task_id: Task to toggle

        Returns:
            True if toggled, False if task not found
        """
        pass
```

### Implementation: InMemoryStorage

**Purpose**: Concrete implementation using Python dict for Phase 1.

```python
class InMemoryStorage(TaskStorage):
    """In-memory storage implementation using dict."""

    def __init__(self) -> None:
        """Initialize empty storage with ID counter."""
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1  # Never reused, always increments

    def add(self, title: str, description: str = "") -> Task:
        """Create task with auto-generated ID."""
        task_id = self._next_id
        self._next_id += 1  # Increment even if task later deleted

        task = Task(
            id=task_id,
            title=title,
            description=description,
            completed=False,
            created_at=datetime.now()
        )
        self._tasks[task_id] = task
        return task

    def get(self, task_id: int) -> Task | None:
        """Retrieve task by ID, None if not found."""
        return self._tasks.get(task_id)

    def get_all(self) -> list[Task]:
        """Return all tasks sorted by ID (ascending)."""
        return sorted(self._tasks.values(), key=lambda t: t.id)

    def update(self, task_id: int, title: str | None = None,
               description: str | None = None) -> bool:
        """Update task fields, return False if not found."""
        task = self._tasks.get(task_id)
        if task is None:
            return False

        # Create new task with updated fields (dataclass immutability pattern)
        updated_task = Task(
            id=task.id,
            title=title if title is not None else task.title,
            description=description if description is not None else task.description,
            completed=task.completed,
            created_at=task.created_at
        )
        self._tasks[task_id] = updated_task
        return True

    def delete(self, task_id: int) -> bool:
        """Delete task, return False if not found."""
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def toggle_complete(self, task_id: int) -> bool:
        """Toggle completion status, return False if not found."""
        task = self._tasks.get(task_id)
        if task is None:
            return False

        # Create new task with toggled completion
        updated_task = Task(
            id=task.id,
            title=task.title,
            description=task.description,
            completed=not task.completed,
            created_at=task.created_at
        )
        self._tasks[task_id] = updated_task
        return True
```

### ID Generation Strategy

**Requirements** (from `/sp.clarify`):
- IDs start at 1 and auto-increment
- IDs are never reused after deletion
- IDs always increase, even after deletions

**Implementation**:
- `_next_id` counter starts at 1
- Increments on every `add()` call: `self._next_id += 1`
- Never decrements or resets
- Deletion does not affect `_next_id`

**Example Scenario**:
```
1. Add task → ID 1 (next_id = 2)
2. Add task → ID 2 (next_id = 3)
3. Add task → ID 3 (next_id = 4)
4. Delete task ID 2
5. Add task → ID 4 (NOT ID 2) (next_id = 5)
```

**Rationale**: Matches database auto-increment behavior; prevents user confusion when referencing tasks by ID in conversation.

## Display Format

**Task List Table**:
```
ID | Title                | Status | Created
---+---------------------+--------+------------------
1  | Buy groceries        | [ ]    | 2025-12-04 14:30
2  | Call dentist         | [✓]    | 2025-12-04 14:35
3  | Write documentation  | [ ]    | 2025-12-04 14:40
```

**Formatting Rules**:
- Status: `[✓]` for completed, `[ ]` for incomplete
- Timestamp: `YYYY-MM-DD HH:MM` format (minute precision)
- Ordering: Ascending by ID (creation order)
- Empty list: "No tasks found. Create your first task to get started!"

## Phase 2 Migration Path

**Database Schema Mapping**:
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Maps to Task.id
    title VARCHAR(200) NOT NULL,           -- Maps to Task.title
    description VARCHAR(1000) DEFAULT '',  -- Maps to Task.description
    completed BOOLEAN DEFAULT FALSE,       -- Maps to Task.completed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Maps to Task.created_at
);
```

**SQLAlchemy Model** (future):
```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime

class TaskModel(DeclarativeBase):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(String(1000), default="")
    completed: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
```

**Storage Implementation** (future):
```python
class DatabaseStorage(TaskStorage):
    def __init__(self, session: Session):
        self._session = session

    def add(self, title: str, description: str = "") -> Task:
        model = TaskModel(title=title, description=description)
        self._session.add(model)
        self._session.commit()
        return Task(
            id=model.id,
            title=model.title,
            description=model.description,
            completed=model.completed,
            created_at=model.created_at
        )

    # Implement other methods similarly
```

**Migration Impact**:
- ✅ Zero changes to operations.py (business logic)
- ✅ Zero changes to ui.py (presentation layer)
- ✅ Only change: Pass `DatabaseStorage(session)` instead of `InMemoryStorage()` in main.py
- ✅ All tests remain valid (use in-memory storage for unit tests)

## Validation Error Types

**Custom Exceptions**:
```python
class ValidationError(Exception):
    """Raised when input violates validation rules."""
    pass

class TaskNotFoundError(Exception):
    """Raised when operation references non-existent task ID."""
    pass
```

**Error Message Format** (per spec SC-003, SC-007):
- State what went wrong: "Title is too long"
- State valid input requirements: "Title must be 1-200 characters"
- No technical jargon: No "ValueError", "Exception", stack traces
- Allow immediate retry: Return to input prompt, not menu

**Example Error Messages**:
- "Title cannot be empty"
- "Title must be between 1-200 characters"
- "Description cannot exceed 1000 characters"
- "Error: Task #99 not found"
- "Error: Invalid task ID. Please enter a valid number"
- "Invalid choice. Please enter a number between 1 and 6"

## Summary

**Entities**: 1 (Task)
**Storage Interfaces**: 1 abstract (TaskStorage), 1 concrete (InMemoryStorage)
**Total Fields**: 5 (id, title, description, completed, created_at)
**Validation Rules**: 3 (title, description, id)
**State Transitions**: 1 (completion toggle)
**Phase 2 Ready**: ✅ Storage abstraction enables drop-in database implementation
