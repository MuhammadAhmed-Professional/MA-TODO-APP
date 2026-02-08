# Quickstart: TDD Implementation Guide

**Feature**: Phase 1 Console Todo Application
**Date**: 2025-12-05
**Purpose**: Step-by-step TDD implementation sequence with code examples

## Prerequisites

Before starting implementation:
1. ✅ Read [spec.md](./spec.md) - Feature requirements
2. ✅ Read [plan.md](./plan.md) - Architecture design
3. ✅ Read [data-model.md](./data-model.md) - Entity definitions
4. ✅ Read [contracts/cli-interface.md](./contracts/cli-interface.md) - CLI specifications

## Project Setup (5 minutes)

```bash
# Navigate to project root
cd /mnt/e/Hackathons-Panaversity/Hackathon-ii/MA-TODO

# Initialize UV project (if not already done)
uv init

# Create directory structure
mkdir -p src/todo_app tests

# Create __init__.py files
touch src/todo_app/__init__.py tests/__init__.py

# Create Python version file
echo "3.13" > .python-version

# Install pytest and coverage
uv add --dev pytest pytest-cov

# Verify setup
uv run pytest --version
```

## TDD Implementation Sequence

### Phase 1: Models Layer (30 minutes)

**Step 1.1: Write Failing Tests** (RED)

Create `tests/test_models.py`:
```python
from datetime import datetime
from src.todo_app.models import Task

def test_task_creation_with_all_fields():
    """Test Task dataclass with all fields specified."""
    created = datetime(2025, 12, 5, 14, 30)
    task = Task(
        id=1,
        title="Buy groceries",
        description="Milk, eggs, bread",
        completed=False,
        created_at=created
    )
    assert task.id == 1
    assert task.title == "Buy groceries"
    assert task.description == "Milk, eggs, bread"
    assert task.completed is False
    assert task.created_at == created

def test_task_creation_with_defaults():
    """Test Task dataclass with default values."""
    task = Task(id=1, title="Test Task")
    assert task.description == ""
    assert task.completed is False
    assert isinstance(task.created_at, datetime)

def test_task_equality():
    """Test Task equality comparison."""
    task1 = Task(id=1, title="Task 1")
    task2 = Task(id=1, title="Task 1")
    # Note: created_at will differ, so tasks won't be equal
    # This tests dataclass default equality
    assert task1.id == task2.id
    assert task1.title == task2.title
```

**Run tests (should FAIL)**:
```bash
uv run pytest tests/test_models.py -v
# Expected: ModuleNotFoundError: No module named 'src.todo_app.models'
```

**Step 1.2: Implement Minimum Code** (GREEN)

Create `src/todo_app/models.py`:
```python
"""Task entity definition."""
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
```

**Run tests (should PASS)**:
```bash
uv run pytest tests/test_models.py -v
# Expected: All tests pass ✅
```

**Step 1.3: Refactor** (REFACTOR)
- Models.py is already clean
- Add docstrings if needed
- Tests remain green

### Phase 2: Storage Layer (60 minutes)

**Step 2.1: Write Failing Tests** (RED)

Create `tests/test_storage.py`:
```python
import pytest
from src.todo_app.models import Task
from src.todo_app.storage import InMemoryStorage

@pytest.fixture
def storage():
    """Provide clean storage instance for each test."""
    return InMemoryStorage()

def test_add_task_assigns_id_starting_at_1(storage):
    """Test add() assigns ID 1 to first task."""
    task = storage.add("First task", "Description")
    assert task.id == 1

def test_add_increments_id(storage):
    """Test IDs increment sequentially."""
    task1 = storage.add("Task 1")
    task2 = storage.add("Task 2")
    task3 = storage.add("Task 3")
    assert task1.id == 1
    assert task2.id == 2
    assert task3.id == 3

def test_id_never_reused_after_deletion(storage):
    """Test IDs not reused after deletion (spec requirement)."""
    task1 = storage.add("Task 1")
    task2 = storage.add("Task 2")
    task3 = storage.add("Task 3")
    # Delete task 2
    storage.delete(task2.id)
    # Add new task - should get ID 4, not 2
    task4 = storage.add("Task 4")
    assert task4.id == 4

def test_get_existing_task(storage):
    """Test get() returns task if exists."""
    task = storage.add("Test task")
    retrieved = storage.get(task.id)
    assert retrieved is not None
    assert retrieved.id == task.id
    assert retrieved.title == "Test task"

def test_get_nonexistent_task_returns_none(storage):
    """Test get() returns None if not found."""
    assert storage.get(999) is None

def test_get_all_returns_sorted_by_id(storage):
    """Test get_all() returns tasks in ID order."""
    task1 = storage.add("Task 1")
    task2 = storage.add("Task 2")
    task3 = storage.add("Task 3")
    all_tasks = storage.get_all()
    assert len(all_tasks) == 3
    assert all_tasks[0].id == 1
    assert all_tasks[1].id == 2
    assert all_tasks[2].id == 3

def test_get_all_empty_storage(storage):
    """Test get_all() returns [] for empty storage."""
    assert storage.get_all() == []

def test_update_existing_task(storage):
    """Test update() modifies task fields."""
    task = storage.add("Original title", "Original description")
    result = storage.update(task.id, title="Updated title", description=None)
    assert result is True
    updated = storage.get(task.id)
    assert updated.title == "Updated title"
    assert updated.description == "Original description"  # Unchanged

def test_update_nonexistent_task_returns_false(storage):
    """Test update() returns False if not found."""
    assert storage.update(999, title="New title") is False

def test_delete_existing_task(storage):
    """Test delete() removes task."""
    task = storage.add("Test task")
    result = storage.delete(task.id)
    assert result is True
    assert storage.get(task.id) is None

def test_delete_nonexistent_task_returns_false(storage):
    """Test delete() returns False if not found."""
    assert storage.delete(999) is False

def test_toggle_complete_incomplete_to_complete(storage):
    """Test toggle changes False → True."""
    task = storage.add("Test task")
    assert task.completed is False
    result = storage.toggle_complete(task.id)
    assert result is True
    updated = storage.get(task.id)
    assert updated.completed is True

def test_toggle_complete_complete_to_incomplete(storage):
    """Test toggle changes True → False."""
    task = storage.add("Test task")
    storage.toggle_complete(task.id)  # Make complete
    result = storage.toggle_complete(task.id)  # Toggle back
    assert result is True
    updated = storage.get(task.id)
    assert updated.completed is False

def test_toggle_nonexistent_returns_false(storage):
    """Test toggle returns False if not found."""
    assert storage.toggle_complete(999) is False
```

**Run tests (should FAIL)**:
```bash
uv run pytest tests/test_storage.py -v
# Expected: ModuleNotFoundError or ImportError
```

**Step 2.2: Implement Minimum Code** (GREEN)

Create `src/todo_app/storage.py`:
```python
"""Storage abstraction layer for task persistence."""
from abc import ABC, abstractmethod
from datetime import datetime
from src.todo_app.models import Task

class TaskStorage(ABC):
    """Abstract base class for task storage operations."""

    @abstractmethod
    def add(self, title: str, description: str = "") -> Task:
        """Create and store a new task."""
        pass

    @abstractmethod
    def get(self, task_id: int) -> Task | None:
        """Retrieve a task by ID."""
        pass

    @abstractmethod
    def get_all(self) -> list[Task]:
        """Retrieve all tasks, ordered by ID ascending."""
        pass

    @abstractmethod
    def update(self, task_id: int, title: str | None = None,
               description: str | None = None) -> bool:
        """Update task title and/or description."""
        pass

    @abstractmethod
    def delete(self, task_id: int) -> bool:
        """Permanently delete a task."""
        pass

    @abstractmethod
    def toggle_complete(self, task_id: int) -> bool:
        """Toggle task completion status."""
        pass


class InMemoryStorage(TaskStorage):
    """In-memory storage implementation using dict."""

    def __init__(self) -> None:
        """Initialize empty storage with ID counter."""
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def add(self, title: str, description: str = "") -> Task:
        """Create task with auto-generated ID."""
        task_id = self._next_id
        self._next_id += 1

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

**Run tests (should PASS)**:
```bash
uv run pytest tests/test_storage.py -v
# Expected: All 17 tests pass ✅
```

**Step 2.3: Refactor** (REFACTOR)
- Extract common task creation logic if needed
- Add type hints to all methods (already done)
- Tests remain green

### Phase 3: Business Logic Layer (90 minutes)

**Step 3.1: Write Failing Tests** (RED)

Create `tests/test_operations.py`:
```python
import pytest
from src.todo_app.storage import InMemoryStorage
from src.todo_app.operations import (
    ValidationError,
    TaskNotFoundError,
    validate_title,
    validate_description,
    create_task,
    list_tasks,
    get_task,
    update_task,
    delete_task,
    toggle_task_complete,
)

@pytest.fixture
def storage():
    """Provide clean storage instance."""
    return InMemoryStorage()

# Validation tests
def test_validate_title_valid():
    """Test valid titles pass validation."""
    validate_title("Valid title")  # Should not raise

def test_validate_title_empty_raises_error():
    """Test empty title raises ValidationError."""
    with pytest.raises(ValidationError, match="Title cannot be empty"):
        validate_title("")

def test_validate_title_whitespace_only_raises_error():
    """Test whitespace-only title raises ValidationError."""
    with pytest.raises(ValidationError, match="Title cannot be empty"):
        validate_title("   ")

def test_validate_title_too_long_raises_error():
    """Test title >200 chars raises ValidationError."""
    with pytest.raises(ValidationError, match="Title must be between 1-200 characters"):
        validate_title("x" * 201)

@pytest.mark.parametrize("length", [1, 100, 200])
def test_validate_title_boundary_conditions(length):
    """Test titles at boundary lengths (1, 100, 200 chars)."""
    validate_title("x" * length)  # Should not raise

def test_validate_description_valid():
    """Test valid descriptions pass validation."""
    validate_description("Valid description")  # Should not raise
    validate_description("")  # Empty is valid

def test_validate_description_too_long_raises_error():
    """Test description >1000 chars raises ValidationError."""
    with pytest.raises(ValidationError, match="Description cannot exceed 1000 characters"):
        validate_description("x" * 1001)

@pytest.mark.parametrize("length", [0, 500, 1000])
def test_validate_description_boundary_conditions(length):
    """Test descriptions at boundary lengths."""
    validate_description("x" * length)  # Should not raise

# create_task tests
def test_create_task_success(storage):
    """Test successful task creation."""
    task = create_task(storage, "Buy groceries", "Milk, eggs")
    assert task.id == 1
    assert task.title == "Buy groceries"
    assert task.description == "Milk, eggs"
    assert task.completed is False

def test_create_task_empty_title_raises_validation_error(storage):
    """Test empty title raises ValidationError."""
    with pytest.raises(ValidationError):
        create_task(storage, "", "Description")

# list_tasks tests
def test_list_tasks_returns_sorted(storage):
    """Test list_tasks returns tasks in ID order."""
    create_task(storage, "Task 1")
    create_task(storage, "Task 2")
    tasks = list_tasks(storage)
    assert len(tasks) == 2
    assert tasks[0].id == 1
    assert tasks[1].id == 2

def test_list_tasks_empty_storage(storage):
    """Test list_tasks returns [] for empty storage."""
    assert list_tasks(storage) == []

# get_task tests
def test_get_task_existing(storage):
    """Test get_task retrieves existing task."""
    task = create_task(storage, "Test task")
    retrieved = get_task(storage, task.id)
    assert retrieved.id == task.id

def test_get_task_nonexistent_raises_not_found_error(storage):
    """Test get_task raises TaskNotFoundError if not found."""
    with pytest.raises(TaskNotFoundError, match="Task #999 not found"):
        get_task(storage, 999)

# update_task tests
def test_update_task_title_only(storage):
    """Test updating title only."""
    task = create_task(storage, "Old title", "Old description")
    updated = update_task(storage, task.id, title="New title", description=None)
    assert updated.title == "New title"
    assert updated.description == "Old description"

def test_update_task_description_only(storage):
    """Test updating description only."""
    task = create_task(storage, "Title", "Old description")
    updated = update_task(storage, task.id, title=None, description="New description")
    assert updated.title == "Title"
    assert updated.description == "New description"

def test_update_task_both_fields(storage):
    """Test updating both title and description."""
    task = create_task(storage, "Old title", "Old desc")
    updated = update_task(storage, task.id, "New title", "New desc")
    assert updated.title == "New title"
    assert updated.description == "New desc"

def test_update_task_nonexistent_raises_not_found_error(storage):
    """Test updating nonexistent task raises TaskNotFoundError."""
    with pytest.raises(TaskNotFoundError):
        update_task(storage, 999, title="New title")

# delete_task tests
def test_delete_task_success(storage):
    """Test successful task deletion."""
    task = create_task(storage, "Test task")
    delete_task(storage, task.id)
    with pytest.raises(TaskNotFoundError):
        get_task(storage, task.id)

def test_delete_task_nonexistent_raises_not_found_error(storage):
    """Test deleting nonexistent task raises TaskNotFoundError."""
    with pytest.raises(TaskNotFoundError):
        delete_task(storage, 999)

# toggle_complete tests
def test_toggle_task_complete(storage):
    """Test toggling task to complete."""
    task = create_task(storage, "Test task")
    toggled = toggle_task_complete(storage, task.id)
    assert toggled.completed is True

def test_toggle_task_incomplete(storage):
    """Test toggling task back to incomplete."""
    task = create_task(storage, "Test task")
    toggle_task_complete(storage, task.id)  # Make complete
    toggled = toggle_task_complete(storage, task.id)  # Toggle back
    assert toggled.completed is False

def test_toggle_nonexistent_raises_not_found_error(storage):
    """Test toggling nonexistent task raises TaskNotFoundError."""
    with pytest.raises(TaskNotFoundError):
        toggle_task_complete(storage, 999)
```

**Run tests (should FAIL)**:
```bash
uv run pytest tests/test_operations.py -v
# Expected: ImportError or failures
```

**Step 3.2: Implement Minimum Code** (GREEN)

Create `src/todo_app/operations.py`:
```python
"""Business logic operations for task management."""
from src.todo_app.models import Task
from src.todo_app.storage import TaskStorage

class ValidationError(Exception):
    """Raised when input violates validation rules."""
    pass

class TaskNotFoundError(Exception):
    """Raised when operation references non-existent task ID."""
    pass

def validate_title(title: str) -> None:
    """Validate task title, raise ValidationError if invalid."""
    if not title or not title.strip():
        raise ValidationError("Title cannot be empty")
    if len(title) > 200:
        raise ValidationError("Title must be between 1-200 characters")

def validate_description(description: str) -> None:
    """Validate task description, raise ValidationError if invalid."""
    if len(description) > 1000:
        raise ValidationError("Description cannot exceed 1000 characters")

def create_task(storage: TaskStorage, title: str, description: str = "") -> Task:
    """Validate inputs and create task in storage."""
    validate_title(title)
    validate_description(description)
    return storage.add(title, description)

def list_tasks(storage: TaskStorage) -> list[Task]:
    """Retrieve all tasks sorted by ID."""
    return storage.get_all()

def get_task(storage: TaskStorage, task_id: int) -> Task:
    """Get task by ID, raise TaskNotFoundError if not found."""
    task = storage.get(task_id)
    if task is None:
        raise TaskNotFoundError(f"Task #{task_id} not found")
    return task

def update_task(storage: TaskStorage, task_id: int,
                title: str | None = None, description: str | None = None) -> Task:
    """Update task fields, raise TaskNotFoundError/ValidationError."""
    if title is not None:
        validate_title(title)
    if description is not None:
        validate_description(description)

    result = storage.update(task_id, title, description)
    if not result:
        raise TaskNotFoundError(f"Task #{task_id} not found")

    return get_task(storage, task_id)

def delete_task(storage: TaskStorage, task_id: int) -> None:
    """Delete task, raise TaskNotFoundError if not found."""
    result = storage.delete(task_id)
    if not result:
        raise TaskNotFoundError(f"Task #{task_id} not found")

def toggle_task_complete(storage: TaskStorage, task_id: int) -> Task:
    """Toggle completion, raise TaskNotFoundError if not found."""
    result = storage.toggle_complete(task_id)
    if not result:
        raise TaskNotFoundError(f"Task #{task_id} not found")
    return get_task(storage, task_id)
```

**Run tests (should PASS)**:
```bash
uv run pytest tests/test_operations.py -v
# Expected: All 25+ tests pass ✅
```

**Step 3.3: Refactor** (REFACTOR)
- Operations.py is clean and under 150 lines
- Tests remain green

## Continue Implementation

**Remaining Phases**:
- Phase 4: UI Layer (`ui.py` + `test_ui.py`)
- Phase 5: Main Entry Point (`main.py` + `test_integration.py`)

**Follow same TDD pattern**:
1. Write failing tests (RED)
2. Implement minimum code (GREEN)
3. Refactor (REFACTOR)

## Running Tests

**Run all tests**:
```bash
uv run pytest -v
```

**Run with coverage**:
```bash
uv run pytest --cov=src/todo_app --cov-report=term-missing
```

**Run specific test file**:
```bash
uv run pytest tests/test_models.py -v
```

**Run tests matching pattern**:
```bash
uv run pytest -k "test_validate" -v
```

## Coverage Target

**Minimum**: 80% (constitution requirement)

**Check coverage**:
```bash
uv run pytest --cov=src/todo_app --cov-report=html
# Open htmlcov/index.html in browser
```

## Next Steps

After completing all modules:
1. Manual testing (run application)
2. Fix bugs found during manual testing
3. Refactor to achieve 80%+ coverage
4. Update README.md
5. Record demo video (<90 seconds)
6. Submit via form

## Quick Reference

**Test Fixtures**:
```python
@pytest.fixture
def storage():
    return InMemoryStorage()
```

**Parametrized Tests**:
```python
@pytest.mark.parametrize("length", [1, 100, 200])
def test_boundary(length):
    # Test code using 'length' variable
```

**Exception Testing**:
```python
with pytest.raises(ValidationError, match="error message"):
    some_function()
```

**Mock Input** (for UI tests):
```python
def test_get_input(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: "user input")
    result = get_user_input()
    assert result == "user input"
```

**Mock Stdout** (for UI tests):
```python
def test_display(capsys):
    display_message("Hello")
    captured = capsys.readouterr()
    assert "Hello" in captured.out
```

## Troubleshooting

**Import errors**:
- Ensure `__init__.py` exists in `src/todo_app/` and `tests/`
- Run tests with `uv run pytest` (not plain `pytest`)

**Coverage not 80%**:
- Run `pytest --cov-report=html` and open `htmlcov/index.html`
- Identify untested lines
- Add tests for uncovered branches

**Tests fail after refactor**:
- Review changes carefully
- Run `pytest -v` to see which tests fail
- Fix implementation or tests as needed

---

**Status**: Ready for implementation
**Estimated Time**: 4-5 days following TDD approach
**Next Command**: `/sp.tasks` to generate detailed implementation tasks
