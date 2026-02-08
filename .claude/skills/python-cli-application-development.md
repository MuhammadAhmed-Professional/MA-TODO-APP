# Python CLI Application Development Skill

## Purpose
Build production-ready command-line interface applications with menu systems, user input handling, state management, and clean architecture.

## When to Use
- Creating interactive console applications
- Building CLI tools with menu-driven interfaces
- Implementing multi-step user workflows
- Console applications requiring persistent state
- Applications with complex input validation

## Prerequisites
- Python 3.13+ with type hints
- Project structure: `src/`, `tests/`, with modules for models, storage, operations, ui
- Understanding of MVC-style separation of concerns
- Familiarity with file I/O and error handling

## Architecture

### Separation of Concerns
```
CLI Application
├── UI Layer (ui.py)
│   ├── Display functions (print output)
│   ├── Input functions (get user input)
│   └── Menu rendering
├── Operations Layer (operations.py)
│   ├── Business logic (create, update, delete)
│   ├── Validation (input constraints)
│   └── Workflow coordination
├── Models Layer (models.py)
│   ├── Data structures
│   └── Type definitions
├── Storage Layer (storage.py)
│   ├── Data persistence
│   ├── CRUD operations
│   └── State management
└── Main Layer (main.py)
    ├── Application entry point
    ├── Menu loop
    └── Global exception handling
```

## Workflow

### Phase 1: Define Data Models

```python
# src/todo_app/models.py
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Task:
    """Task data model."""
    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate model on creation."""
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")
```

**Validation**: `python -c "from src.todo_app.models import Task; t = Task(1, 'Test'); print(t)"`

### Phase 2: Implement Storage Layer

```python
# src/todo_app/storage.py
from abc import ABC, abstractmethod
from typing import Optional
from .models import Task

class TaskStorage(ABC):
    """Abstract storage interface."""

    @abstractmethod
    def add(self, title: str, description: str = "") -> Task:
        """Add task to storage."""
        pass

    @abstractmethod
    def get(self, task_id: int) -> Optional[Task]:
        """Retrieve task by ID."""
        pass

    @abstractmethod
    def get_all(self) -> list[Task]:
        """Get all tasks."""
        pass

class InMemoryStorage(TaskStorage):
    """In-memory task storage."""

    def __init__(self):
        self._tasks: dict[int, Task] = {}
        self._next_id = 1

    def add(self, title: str, description: str = "") -> Task:
        """Add task with auto-incremented ID."""
        task = Task(id=self._next_id, title=title, description=description)
        self._tasks[self._next_id] = task
        self._next_id += 1
        return task

    def get(self, task_id: int) -> Optional[Task]:
        """Retrieve task or None."""
        return self._tasks.get(task_id)

    def get_all(self) -> list[Task]:
        """Return all tasks sorted by ID."""
        return sorted(self._tasks.values(), key=lambda t: t.id)
```

**Validation**: `pytest tests/test_storage.py -v`

### Phase 3: Implement Operations/Business Logic

```python
# src/todo_app/operations.py
from .storage import TaskStorage
from .models import Task

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

def validate_title(title: str) -> str:
    """Validate task title."""
    cleaned = title.strip()
    if not cleaned:
        raise ValidationError("Title cannot be empty")
    if len(cleaned) > 200:
        raise ValidationError("Title must be between 1-200 characters")
    return cleaned

def create_task(storage: TaskStorage, title: str, description: str = "") -> Task:
    """Create a new task with validation."""
    validated_title = validate_title(title)
    validated_description = validate_description(description)
    task = storage.add(validated_title, validated_description)
    return task
```

**Validation**: `pytest tests/test_operations.py -v`

### Phase 4: Implement UI Layer

```python
# src/todo_app/ui.py
from typing import TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .models import Task

def display_menu() -> None:
    """Display the main menu options."""
    print("\n=== Todo List Application ===")
    print("1. Add Task")
    print("2. View All Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Mark Task as Complete")
    print("6. Exit")

def get_menu_choice() -> str:
    """Get menu choice from user."""
    return input("\nEnter your choice: ").strip()

def get_task_title() -> str:
    """Prompt user for task title."""
    return input("Enter task title: ")

def display_success(message: str) -> None:
    """Display success message."""
    print(f"✓ {message}")
    input("Press Enter to continue...")

def display_error(message: str) -> None:
    """Display error message."""
    print(f"\n❌ Error: {message}")
    input("Press Enter to continue...")

def display_task_list(tasks: list["Task"]) -> None:
    """Display a formatted table of tasks."""
    if not tasks:
        print("No tasks found. Create your first task to get started!")
        input("Press Enter to continue...")
        return

    print(f"{'ID':<5} {'Status':<8} {'Title':<30} {'Created':<20}")
    print("-" * 63)

    for task in tasks:
        status = "✓" if task.completed else " "
        timestamp = task.created_at.strftime("%Y-%m-%d %H:%M")
        title = task.title[:27] + "..." if len(task.title) > 30 else task.title
        print(f"{task.id:<5} {status:<8} {title:<30} {timestamp:<20}")

    input("Press Enter to continue...")
```

**Validation**: `pytest tests/test_ui.py -v`

### Phase 5: Implement Main Application Loop

```python
# src/todo_app/main.py
from .storage import InMemoryStorage
from .operations import ValidationError, TaskNotFoundError
from .ui import display_menu, get_menu_choice, display_error

def main() -> None:
    """Main application entry point with menu loop."""
    storage = InMemoryStorage()

    print("Welcome to Todo List Application!")
    print("=" * 40)

    while True:
        try:
            display_menu()
            choice = get_menu_choice()

            match choice:
                case "1":
                    handle_add_task(storage)
                case "2":
                    handle_view_tasks(storage)
                case "3":
                    handle_update_task(storage)
                case "4":
                    handle_delete_task(storage)
                case "5":
                    handle_mark_complete(storage)
                case "6":
                    print("\nGoodbye! Your tasks have been saved.")
                    break
                case _:
                    display_error(f"Invalid choice: '{choice}'. Please enter 1-6.")

        except ValidationError as e:
            display_error(f"Validation error: {e}")
        except TaskNotFoundError as e:
            display_error(str(e))
        except ValueError as e:
            display_error(f"Invalid input: {e}")
        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Goodbye!")
            break
        except Exception as e:
            display_error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
```

**Validation**: `python -m src.todo_app.main` and test workflows.

## Best Practices

### Input Validation
- Always strip whitespace: `input().strip()`
- Validate before creating models
- Provide clear error messages
- Use retry loops for invalid input
- Never let invalid data into storage

### State Management
- Keep storage interface abstract
- Inject dependencies (dependency injection)
- Don't store application state globally
- Use dataclasses for data models
- Update timestamps on modifications

### User Experience
- Clear, consistent prompts
- Helpful error messages
- Visual separation (headers, lines)
- Empty state handling
- Confirmation for destructive actions
- "Press Enter to continue" after each operation

## Common Patterns

### Pattern 1: Menu-Driven Loop
```python
def main():
    """Main loop with menu."""
    while True:
        choice = show_menu()
        match choice:
            case "1":
                handle_option_1()
            case "q":
                break
            case _:
                print("Invalid choice")
```

### Pattern 2: Validated Input
```python
def get_task_id() -> int:
    """Get task ID with validation."""
    return int(input("Enter task ID: "))
```

### Pattern 3: Workflow Handler
```python
def handle_add_task(storage: TaskStorage) -> None:
    """Handle add task workflow."""
    title = get_task_title()
    description = get_task_description()
    task = create_task(storage, title, description)
    display_success(f"Task #{task.id} created successfully")
```

### Pattern 4: Global Exception Handling
```python
try:
    # Application logic
    pass
except ValidationError as e:
    display_error(f"Validation error: {e}")
except KeyboardInterrupt:
    print("\n\nGoodbye!")
except Exception as e:
    display_error(f"Unexpected error: {e}")
```

## Testing Checklist
- ✅ Models can be created and validated
- ✅ Storage layer CRUD operations work
- ✅ Business logic produces correct results
- ✅ UI input functions accept valid input
- ✅ UI output functions format data correctly
- ✅ Menu navigation works end-to-end
- ✅ Error handling prevents invalid state
- ✅ Integration tests verify full workflows

## Running the Application

```bash
# Run application
python -m src.todo_app.main

# Run tests
pytest tests/ -v

# Run with coverage
pytest --cov=src --cov-report=html
```
