# Implementation Plan: In-Memory Python Console Todo Application (Phase 1)

**Branch**: `001-console-todo-app` | **Date**: 2025-12-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-console-todo-app/spec.md`

## Summary

Build a command-line todo application in Python 3.13+ that provides 5 core CRUD operations (Add, View, Update, Delete, Mark Complete) with in-memory task storage. The application follows Test-Driven Development (TDD), uses clean architecture with layer separation, and is designed to facilitate Phase 2 database migration. All tasks include ID, title, description, completion status, and creation timestamp, displayed in a formatted CLI interface with robust validation and error handling.

**Technical Approach**: Implement a three-layer architecture (Presentation/CLI, Business Logic, Data) using Python dataclasses for task entities, a storage abstraction layer for future database migration, and pytest for TDD with 80%+ coverage target.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: pytest (testing only), standard library for core functionality
**Storage**: In-memory using Python dict/list (designed for future database abstraction)
**Testing**: pytest with 80% minimum coverage target, following TDD Red-Green-Refactor cycle
**Target Platform**: Cross-platform CLI (Linux, macOS, Windows terminals with UTF-8 support)
**Project Type**: Single project (CLI application)
**Performance Goals**: Task creation <10s, task viewing <3s, no operation >5s with 100 tasks
**Constraints**: No external dependencies for core features, max 50 lines/function, PEP 8 compliance, type hints required
**Scale/Scope**: 5 CRUD operations, 15 functional requirements, designed to handle 100+ tasks in memory

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Spec-Driven Development ✅
- **Status**: PASS
- **Evidence**: Complete specification at `specs/001-console-todo-app/spec.md` with 5 user stories, 31 acceptance scenarios, 15 functional requirements, 10 success criteria
- **Action**: Design must trace every module/function back to spec requirements

### Principle II: Clean Code & Pythonic Standards ✅
- **Status**: PASS (design enforces)
- **Requirements**: PEP 8, type hints, max 50 lines/function, max 300 lines/file, docstrings
- **Action**: Architecture must support these constraints through proper module decomposition

### Principle III: Test-First Development (TDD) ✅
- **Status**: PASS (architecture designed for testability)
- **Requirements**: Red-Green-Refactor cycle, 80% coverage, pytest execution
- **Action**: All modules must have clear interfaces enabling unit testing before implementation

### Principle IV: Simple In-Memory Storage ✅
- **Status**: PASS
- **Approach**: Python dict for task storage, abstraction layer for future database migration
- **Action**: Storage interface must be designed to swap implementations in Phase 2 without business logic changes

### Principle V: CLI Interface Excellence ✅
- **Status**: PASS (detailed in spec FR-001 through FR-015)
- **Features**: Numbered menu, input validation, error messages, formatted output, confirmations
- **Action**: CLI layer must be cleanly separated from business logic for testability

### Principle VI: Python 3.13+ Modern Practices ✅
- **Status**: PASS
- **Tools**: UV for dependencies, dataclasses for models, modern type hints (|), match/case for menu
- **Action**: Use dataclasses for Task entity, match/case for menu dispatcher

**Overall**: ✅ ALL GATES PASS - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/001-console-todo-app/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (technology decisions)
├── data-model.md        # Phase 1 output (entity design)
├── quickstart.md        # Phase 1 output (TDD implementation sequence)
├── contracts/           # Phase 1 output (CLI interface contracts)
│   └── cli-interface.md # Menu and I/O specifications
├── checklists/
│   └── requirements.md  # Spec quality checklist (complete)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT YET CREATED)
```

### Source Code (repository root)

```text
src/todo_app/
├── __init__.py          # Package marker
├── main.py              # Entry point, CLI loop, menu dispatcher
├── models.py            # Task dataclass, validation logic
├── storage.py           # TaskStorage interface + InMemoryStorage implementation
├── operations.py        # Business logic for CRUD operations
└── ui.py                # User I/O functions, formatting, prompts

tests/
├── __init__.py
├── test_models.py       # Task entity tests, validation tests
├── test_storage.py      # Storage layer tests (ID generation, CRUD)
├── test_operations.py   # Business logic tests (end-to-end operation flows)
├── test_ui.py           # UI layer tests (input/output formatting)
└── test_integration.py  # Full workflow tests (menu → operation → storage)

# Project root files
├── .specify/            # Spec-Kit Plus configuration
├── specs/               # Feature specifications
├── src/                 # Application source
├── tests/               # Test suite
├── README.md            # Setup and usage
├── CLAUDE.md            # Claude Code instructions
├── pyproject.toml       # UV project configuration
└── .python-version      # Python version (3.13+)
```

**Structure Decision**: Selected **Single Project** structure (Option 1) because this is a CLI application without frontend/backend separation. The src/todo_app/ package contains 5 focused modules (main, models, storage, operations, ui) each under 300 lines, promoting testability and adherence to SRP (Single Responsibility Principle).

## Complexity Tracking

> **No violations** - All constitution principles satisfied without complexity trade-offs.

## Architecture Overview

### Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────┐  │
│  │ main.py  │  │  ui.py   │  │ CLI Loop & I/O Functions │  │
│  │ - Entry  │  │ - Input  │  │ - Menu display           │  │
│  │ - Menu   │  │ - Output │  │ - Prompts & validation   │  │
│  │   loop   │  │ - Format │  │ - Table formatting       │  │
│  └─────┬────┘  └──────────┘  └──────────────────────────┘  │
└────────┼───────────────────────────────────────────────────┘
         │ Calls operations with user input
         ▼
┌─────────────────────────────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ operations.py                                          │ │
│  │ - create_task()      : Validate & store new task      │ │
│  │ - list_tasks()       : Retrieve & sort tasks          │ │
│  │ - update_task()      : Validate & update fields       │ │
│  │ - delete_task()      : Delete with confirmation logic │ │
│  │ - toggle_complete()  : Toggle completion status       │ │
│  └─────────────────────┬──────────────────────────────────┘ │
└────────────────────────┼───────────────────────────────────┘
                         │ Uses storage abstraction
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                       DATA LAYER                             │
│  ┌──────────────┐  ┌────────────────────────────────────┐  │
│  │  models.py   │  │        storage.py                  │  │
│  │              │  │                                    │  │
│  │ Task         │  │ TaskStorage (ABC)                  │  │
│  │  - id        │  │  - add()                           │  │
│  │  - title     │  │  - get()                           │  │
│  │  - desc      │  │  - get_all()                       │  │
│  │  - completed │  │  - update()                        │  │
│  │  - created   │  │  - delete()                        │  │
│  │              │  │  - toggle_complete()               │  │
│  │              │  │                                    │  │
│  │              │  │ InMemoryStorage(TaskStorage)       │  │
│  │              │  │  - _tasks: dict[int, Task]         │  │
│  │              │  │  - _next_id: int                   │  │
│  └──────────────┘  └────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Dependency Flow

```
main.py  ───────┐
                ├──> operations.py ───> storage.py ───> models.py
ui.py   ────────┘

Direction: High-level → Low-level (no circular dependencies)
```

### Phase 2 Migration Strategy

```
Phase 1:                        Phase 2:
┌────────────┐                 ┌────────────┐
│ operations │                 │ operations │ (unchanged)
└──────┬─────┘                 └──────┬─────┘
       │                              │
       ▼                              ▼
┌────────────────┐             ┌────────────────┐
│ InMemoryStorage│             │ DatabaseStorage│ (new)
└────────────────┘             └───────┬────────┘
                                       │
                                       ▼
                                 ┌──────────┐
                                 │ Database │
                                 └──────────┘
```

## Module Design

### Module 1: models.py (Data Layer)

**Purpose**: Define Task entity with validation logic

**Exports**:
```python
@dataclass
class Task:
    """Represents a todo task with metadata."""
    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
```

**Responsibilities**:
- Task entity definition with type hints
- Field defaults (description="", completed=False, created_at=now())
- Mutable dataclass (default behavior; not frozen) to allow field updates via storage layer

**Dependencies**: `datetime` (stdlib)

**Testing Strategy**:
- Test task creation with all fields
- Test field defaults
- Test equality comparison
- Estimated lines: ~30

### Module 2: storage.py (Data Layer)

**Purpose**: Abstract storage interface + in-memory implementation

**Exports**:
```python
class TaskStorage(ABC):
    """Abstract base class for task storage operations."""
    @abstractmethod
    def add(self, title: str, description: str = "") -> Task:
        """Create and store a new task with auto-generated ID.

        Callers do not provide task IDs; the storage layer creates
        the Task object internally with an auto-incremented ID.
        Returns the newly created Task with assigned ID.
        """
        ...
    @abstractmethod
    def get(self, task_id: int) -> Task | None: ...
    @abstractmethod
    def get_all(self) -> list[Task]: ...
    @abstractmethod
    def update(self, task_id: int, title: str | None,
               description: str | None) -> bool: ...
    @abstractmethod
    def delete(self, task_id: int) -> bool: ...
    @abstractmethod
    def toggle_complete(self, task_id: int) -> bool: ...

class InMemoryStorage(TaskStorage):
    """In-memory implementation using dict."""
    def __init__(self):
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1
```

**Responsibilities**:
- ID generation (auto-increment, never reuse)
- CRUD operations on task collection
- Sorting (get_all returns tasks sorted by ID)
- Task existence checking

**Dependencies**: `models.Task`, `abc.ABC`, `typing`

**Testing Strategy**:
- Test ID auto-increment (1, 2, 3...)
- Test ID never reused after deletion (spec requirement)
- Test add, get, get_all, update, delete, toggle_complete
- Test operations on non-existent IDs (return False/None)
- Test get_all returns sorted by ID
- Estimated lines: ~80

### Module 3: operations.py (Business Logic Layer)

**Purpose**: Pure business logic functions for CRUD operations

**Exports**:
```python
class ValidationError(Exception): ...
class TaskNotFoundError(Exception): ...

def validate_title(title: str) -> None:
    """Raise ValidationError if title invalid."""

def validate_description(description: str) -> None:
    """Raise ValidationError if description invalid."""

def create_task(storage: TaskStorage, title: str,
                description: str = "") -> Task:
    """Validate inputs and create task in storage."""

def list_tasks(storage: TaskStorage) -> list[Task]:
    """Retrieve all tasks sorted by ID."""

def get_task(storage: TaskStorage, task_id: int) -> Task:
    """Get task by ID, raise TaskNotFoundError if not found."""

def update_task(storage: TaskStorage, task_id: int,
                title: str | None, description: str | None) -> Task:
    """Update task fields, raise TaskNotFoundError/ValidationError."""

def delete_task(storage: TaskStorage, task_id: int) -> None:
    """Delete task, raise TaskNotFoundError if not found."""

def toggle_task_complete(storage: TaskStorage, task_id: int) -> Task:
    """Toggle completion, raise TaskNotFoundError if not found."""
```

**Responsibilities**:
- Input validation (title 1-200 chars, description ≤1000 chars)
- Business rule enforcement
- Error handling (raise exceptions for invalid operations)
- NO I/O operations (pure functions)

**Dependencies**: `storage.TaskStorage`, `models.Task`

**Testing Strategy**:
- Test each operation with valid inputs (happy path)
- Test validation errors (empty title, >200 chars, >1000 chars desc)
- Test TaskNotFoundError for non-existent IDs
- Test boundary conditions (200 char title, 1000 char desc)
- Parametrized tests for validation rules
- Estimated lines: ~150

### Module 4: ui.py (Presentation Layer)

**Purpose**: All user input/output, formatting, prompts

**Exports**:
```python
def display_menu() -> None:
    """Display main menu with 6 options."""

def get_menu_choice() -> str:
    """Get and return user's menu choice (no validation)."""

def get_task_title(prompt: str = "Enter task title:") -> str:
    """Prompt for title with validation loop, return valid title."""

def get_task_description(prompt: str = "Enter description:") -> str:
    """Prompt for description with validation loop, return valid desc."""

def get_task_id(prompt: str = "Enter task ID:") -> int | None:
    """Prompt for task ID, return int or None if invalid."""

def get_confirmation(prompt: str) -> bool:
    """Prompt for y/n confirmation, loop until valid."""

def get_optional_update(field_name: str, current: str) -> str | None:
    """Prompt for field update, None if Enter pressed (keep current)."""

def display_task_list(tasks: list[Task]) -> None:
    """Display formatted task table or 'No tasks found' message."""

def display_success(message: str) -> None:
    """Display success message and wait for Enter."""

def display_error(message: str) -> None:
    """Display error message (formatted for visibility)."""

def format_timestamp(dt: datetime) -> str:
    """Format datetime as YYYY-MM-DD HH:MM."""

def format_status(completed: bool) -> str:
    """Return '[✓]' if completed else '[ ]'."""

def wait_for_enter(prompt: str = "Press Enter...") -> None:
    """Pause until Enter pressed."""

def clear_screen() -> None:
    """Clear terminal screen (optional)."""
```

**Responsibilities**:
- All `input()` and `print()` calls
- Input validation loops (re-prompt on error)
- Table formatting for task list
- Timestamp and status indicator formatting
- Error message display

**Dependencies**: `models.Task`, `datetime`

**Testing Strategy**:
- Test formatting functions (format_timestamp, format_status)
- Test display functions with mock stdout (snapshot testing)
- Mock input() for get_* function tests
- Test validation loops (mocking multiple invalid→valid inputs)
- Estimated lines: ~200

### Module 5: main.py (Presentation Layer - Orchestration)

**Purpose**: Entry point, menu loop, orchestrate UI + operations

**Exports**:
```python
def handle_add_task(storage: TaskStorage) -> None:
    """Orchestrate add task flow: UI → operations → UI."""

def handle_view_tasks(storage: TaskStorage) -> None:
    """Orchestrate view tasks flow."""

def handle_update_task(storage: TaskStorage) -> None:
    """Orchestrate update task flow."""

def handle_delete_task(storage: TaskStorage) -> None:
    """Orchestrate delete task flow."""

def handle_mark_complete(storage: TaskStorage) -> None:
    """Orchestrate mark complete flow."""

def main() -> None:
    """Main entry point: initialize storage, run menu loop."""

if __name__ == "__main__":
    main()
```

**Responsibilities**:
- Initialize InMemoryStorage
- Menu loop (display menu, get choice, dispatch)
- Route menu choices using match/case
- Orchestrate UI and operations (call ui functions, pass to operations, display results)
- Exception handling (catch ValidationError, TaskNotFoundError)
- Graceful exit (Ctrl+C handling)

**Dependencies**: `storage.InMemoryStorage`, `operations.*`, `ui.*`

**Testing Strategy**:
- Integration tests for full workflows
- Mock storage and test each handler function
- Test menu loop dispatch (mock get_menu_choice)
- Test exception handling (ValidationError → display_error)
- Estimated lines: ~150

## Data Flow Example: Add Task Operation

```
1. User sees menu, enters "1"
   ├─> main.py: get_menu_choice() returns "1"
   └─> main.py: match case "1" → handle_add_task(storage)

2. main.py calls ui functions to get input
   ├─> ui.get_task_title()
   │   ├─> Prompt: "Enter task title:"
   │   ├─> User types: "Buy groceries"
   │   └─> Returns: "Buy groceries"
   │
   └─> ui.get_task_description()
       ├─> Prompt: "Enter description (optional):"
       ├─> User types: "Milk, eggs, bread"
       └─> Returns: "Milk, eggs, bread"

3. main.py passes inputs to business logic
   └─> operations.create_task(storage, "Buy groceries", "Milk, eggs, bread")
       ├─> operations.validate_title("Buy groceries") ✓
       ├─> operations.validate_description("Milk, eggs, bread") ✓
       └─> storage.add("Buy groceries", "Milk, eggs, bread")
           ├─> ID = _next_id (1)
           ├─> _next_id += 1 (now 2)
           ├─> task = Task(id=1, title=..., desc=..., completed=False, created_at=now())
           ├─> _tasks[1] = task
           └─> return task

4. main.py receives result, displays confirmation
   └─> ui.display_success("Task #1 'Buy groceries' created successfully")
       ├─> Print message
       ├─> ui.wait_for_enter()
       └─> Return to menu

5. Menu loop continues
   └─> Display menu again
```

## Design Decisions & Rationale

### Decision 1: Storage Abstraction Layer
**Decision**: Implement `TaskStorage` ABC with `InMemoryStorage` concrete class
**Rationale**:
- Enables Phase 2 database migration with zero business logic changes
- Follows Dependency Inversion Principle (high-level modules depend on abstractions)
- Facilitates testing (can mock storage for operations tests)
- Isolates ID generation strategy in one place

**Trade-offs**:
- Adds ~20 lines of abstraction code
- Benefit: Saves hundreds of lines of refactoring in Phase 2

**ADR Significance Test**:
- ✅ **Impact**: Long-term (affects Phase 2 migration ease)
- ✅ **Alternatives**: Direct dict vs abstraction layer vs repository pattern
- ✅ **Scope**: Cross-cutting (all CRUD operations depend on this)
**Result**: ⚠️ **Borderline ADR** - Consider documenting if team unfamiliar with abstraction patterns

### Decision 2: Separate UI from Business Logic
**Decision**: Split into `ui.py` (I/O) and `operations.py` (business logic)
**Rationale**:
- Enables unit testing of business logic without mocking I/O
- Follows Single Responsibility Principle
- Facilitates Phase 2 web UI (replace ui.py, keep operations.py)
- Makes code more maintainable (clear separation of concerns)

**Trade-offs**:
- 2 modules instead of 1 (~30 lines overhead)
- Benefit: Testability, flexibility, maintainability

**ADR Significance**: ❌ Not significant (standard best practice)

### Decision 3: Match/Case for Menu Dispatcher
**Decision**: Use Python 3.10+ `match/case` for menu routing
**Rationale**:
- Modern Python idiom (constitution principle VI)
- More readable than if/elif chains
- Demonstrates Python 3.13 features
- Easier to extend (add new menu options)

**Trade-offs**:
- Requires Python 3.10+ (already required)
- No downside vs if/elif for this use case

**ADR Significance**: ❌ Not significant (implementation detail)

### Decision 4: Raise Exceptions for Errors
**Decision**: operations.py raises `ValidationError`, `TaskNotFoundError`; main.py catches
**Rationale**:
- Pythonic error handling pattern
- Separates error detection (operations) from error presentation (main/ui)
- Simplifies testing (test that exceptions are raised)
- Clear error propagation path

**Trade-offs**:
- Requires try/except blocks in main.py
- Benefit: Clean error handling, testable

**ADR Significance**: ❌ Not significant (standard Python practice)

### Decision 5: ID Never Reused After Deletion
**Decision**: `_next_id` always increments, never resets or reuses deleted IDs
**Rationale**:
- Spec requirement from `/sp.clarify` session
- Matches database auto-increment behavior
- Prevents user confusion ("I deleted task 5" remains clear)

**Trade-offs**:
- IDs may have gaps (1, 2, 4, 5 if 3 deleted)
- Benefit: User clarity, Phase 2 compatibility

**ADR Significance**: ❌ Not significant (spec requirement, not architectural choice)

## Testing Approach

### TDD Workflow (Constitution Requirement)

**Red-Green-Refactor Cycle**:
1. **Red**: Write failing test for acceptance scenario
2. **Green**: Implement minimum code to pass test
3. **Refactor**: Clean up, extract helpers, keep tests green

**Implementation Order** (following test dependencies):
1. models.py → test_models.py (Task entity)
2. storage.py → test_storage.py (storage layer)
3. operations.py → test_operations.py (business logic)
4. ui.py → test_ui.py (formatting functions)
5. main.py → test_integration.py (full workflows)

### Test Structure

**test_models.py** (~50 lines):
```python
def test_task_creation_with_defaults():
    """Test Task dataclass with default values."""

def test_task_creation_with_all_fields():
    """Test Task with explicit field values."""

def test_task_equality():
    """Test Task equality comparison."""
```

**test_storage.py** (~150 lines):
```python
def test_add_task_assigns_id():
    """Test add() assigns ID starting at 1."""

def test_add_increments_id():
    """Test IDs increment (1, 2, 3...)."""

def test_id_never_reused_after_deletion():
    """Test ID 2 not reused after deletion (spec requirement)."""

def test_get_existing_task():
    """Test get() returns task if exists."""

def test_get_nonexistent_task_returns_none():
    """Test get() returns None if not found."""

def test_get_all_returns_sorted_by_id():
    """Test get_all() returns tasks in ID order."""

def test_get_all_empty_storage():
    """Test get_all() returns [] for empty storage."""

def test_update_existing_task():
    """Test update() modifies task fields."""

def test_update_nonexistent_task_returns_false():
    """Test update() returns False if not found."""

def test_delete_existing_task():
    """Test delete() removes task."""

def test_delete_nonexistent_task_returns_false():
    """Test delete() returns False if not found."""

def test_toggle_complete_incomplete_to_complete():
    """Test toggle changes False → True."""

def test_toggle_complete_complete_to_incomplete():
    """Test toggle changes True → False."""
```

**test_operations.py** (~200 lines):
```python
# Validation tests
def test_validate_title_valid():
def test_validate_title_empty_raises_error():
def test_validate_title_too_long_raises_error():
def test_validate_title_whitespace_only_raises_error():
def test_validate_description_valid():
def test_validate_description_too_long_raises_error():

# create_task tests
def test_create_task_success():
def test_create_task_empty_title_raises_validation_error():
def test_create_task_title_too_long_raises_validation_error():

# list_tasks tests
def test_list_tasks_returns_sorted():
def test_list_tasks_empty_storage():

# get_task tests
def test_get_task_existing():
def test_get_task_nonexistent_raises_not_found_error():

# update_task tests
def test_update_task_title_only():
def test_update_task_description_only():
def test_update_task_both_fields():
def test_update_task_nonexistent_raises_not_found_error():

# delete_task tests
def test_delete_task_success():
def test_delete_task_nonexistent_raises_not_found_error():

# toggle_complete tests
def test_toggle_task_complete():
def test_toggle_task_incomplete():
def test_toggle_nonexistent_raises_not_found_error():

# Boundary condition tests (parametrized)
@pytest.mark.parametrize("length", [1, 100, 200])
def test_title_boundary_conditions(length):
    """Test title with 1, 100, 200 chars (all valid)."""

@pytest.mark.parametrize("length", [201, 250, 500])
def test_title_exceeds_limit(length):
    """Test title with >200 chars raises ValidationError."""
```

**test_ui.py** (~100 lines):
```python
def test_format_timestamp():
    """Test timestamp formatted as YYYY-MM-DD HH:MM."""

def test_format_status_completed():
    """Test completed=True returns '[✓]'."""

def test_format_status_incomplete():
    """Test completed=False returns '[ ]'."""

def test_display_task_list_with_tasks(capsys):
    """Test table display with tasks (snapshot test)."""

def test_display_task_list_empty(capsys):
    """Test 'No tasks found' message."""

def test_display_success(capsys):
    """Test success message format."""

def test_display_error(capsys):
    """Test error message format."""

# Input function tests (mock input)
def test_get_menu_choice(monkeypatch):
    """Test menu choice input."""

def test_get_task_title_valid(monkeypatch):
    """Test valid title input."""

def test_get_task_id_valid(monkeypatch):
    """Test valid ID input."""

def test_get_task_id_invalid(monkeypatch):
    """Test invalid ID returns None."""
```

**test_integration.py** (~150 lines):
```python
def test_full_add_task_workflow():
    """Test complete add task flow."""

def test_full_view_tasks_workflow():
    """Test complete view tasks flow."""

def test_full_update_task_workflow():
    """Test complete update task flow."""

def test_full_delete_task_workflow():
    """Test complete delete task flow."""

def test_full_mark_complete_workflow():
    """Test complete mark complete flow."""

def test_add_delete_add_id_not_reused():
    """Test spec requirement: IDs not reused."""
```

### Coverage Target

**Minimum**: 80% (constitution requirement)
**Expected**: 85-90% with comprehensive tests

**Coverage Gaps (Acceptable)**:
- Some error handling branches (KeyboardInterrupt)
- Some UI formatting edge cases
- Clear screen / terminal-specific code

### Pytest Configuration

**pyproject.toml**:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--verbose",
    "--cov=src/todo_app",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-fail-under=80"
]
```

## Implementation Sequence (TDD Order)

**Phase 1: Foundation** (Day 1)
1. ✅ Project setup (UV init, pyproject.toml, directory structure)
2. ✅ Write test_models.py (3-5 tests for Task dataclass)
3. ✅ Implement models.py (pass tests)
4. ✅ Write test_storage.py (ID generation, CRUD operations)
5. ✅ Implement storage.py (pass tests)

**Phase 2: Business Logic** (Day 2)
6. ✅ Write test_operations.py (validation, create_task)
7. ✅ Implement validation functions in operations.py
8. ✅ Implement create_task in operations.py
9. ✅ Write tests for list_tasks, get_task, update_task, delete_task, toggle_complete
10. ✅ Implement remaining operations.py functions

**Phase 3: UI Layer** (Day 3)
11. ✅ Write test_ui.py (formatting functions)
12. ✅ Implement ui.py (display functions, formatting)
13. ✅ Write tests for input functions (mock input)
14. ✅ Implement ui.py input functions

**Phase 4: Integration** (Day 4)
15. ✅ Write test_integration.py (full workflows)
16. ✅ Implement main.py (menu loop, handlers)
17. ✅ Manual testing (run app, verify all scenarios)
18. ✅ Fix bugs, refactor, achieve 80%+ coverage

**Phase 5: Documentation & Submission** (Day 5)
19. ✅ Update README.md (setup, usage, features)
20. ✅ Record demo video (<90 seconds)
21. ✅ Final testing, commit, push
22. ✅ Submit via form

## Risk Analysis

### Risk 1: Test Coverage Below 80%
**Probability**: Low
**Impact**: High (constitution violation)
**Mitigation**:
- Run `pytest --cov` frequently during development
- Write tests before code (TDD enforces this)
- Use coverage report to identify untested branches
- Fail CI build if coverage <80% (`--cov-fail-under=80`)

**Contingency**: If coverage falls short, add parametrized tests for edge cases

### Risk 2: Functions Exceed 50 Lines
**Probability**: Medium
**Impact**: Medium (constitution violation)
**Mitigation**:
- Review function length during refactor phase
- Extract helper functions proactively
- Use linting rules to flag long functions
- Operations.py handlers likely need helpers (validation, error handling)

**Contingency**: Refactor long functions into smaller helpers during Refactor phase

### Risk 3: Unicode/Terminal Compatibility Issues
**Probability**: Medium
**Impact**: Low (affects display only)
**Mitigation**:
- Test on Windows, Linux, macOS terminals
- Use basic ASCII alternatives (`[X]` instead of `[✓]` if needed)
- Configure UTF-8 encoding: `sys.stdout.reconfigure(encoding='utf-8')`
- Document terminal requirements in README

**Contingency**: Provide fallback ASCII display mode if Unicode fails

## Success Criteria Mapping

**How architecture supports each spec success criterion (SC-001 to SC-010)**:

| Criterion | Architecture Support |
|-----------|---------------------|
| **SC-001**: Task creation <10s | UI layer handles prompts efficiently; no network I/O; minimal processing |
| **SC-002**: Task viewing <3s | In-memory dict lookup is O(1); sorting 100 tasks is trivial |
| **SC-003**: Error messages <1s | Validation in operations.py is immediate; no external calls |
| **SC-004**: No crashes, 80% coverage | TDD approach + comprehensive test suite ensures robustness |
| **SC-005**: All validations work | Dedicated validation functions with parametrized tests |
| **SC-006**: Performance with 100 tasks | Dict storage is O(1) lookup; sorting 100 items is <1ms |
| **SC-007**: Clear error messages | Spec defines exact error message format; ui.py implements |
| **SC-008**: 90% first-attempt success | UI prompts are clear; error messages guide user |
| **SC-009**: Data accuracy | Immutable dataclass pattern; comprehensive storage tests |
| **SC-010**: Boundary conditions handled | Parametrized tests for 200/201 chars, 1000/1001 chars, edge IDs |

**All SC requirements are architecturally supported** ✅

## Next Steps

**After `/sp.plan` completes**:
1. ✅ Review plan.md, research.md, data-model.md, contracts/
2. ✅ Run `/sp.tasks` to generate implementation tasks from this plan
3. ✅ Begin Phase 1 implementation following TDD sequence
4. ✅ Track progress via tasks.md

**Documentation Complete**:
- ✅ plan.md (this file)
- ✅ research.md (technology decisions)
- ✅ data-model.md (entity design)
- ✅ contracts/cli-interface.md (CLI specifications)
- ⏳ tasks.md (pending `/sp.tasks` command)

---

**Plan Status**: ✅ COMPLETE
**Constitution Compliance**: ✅ ALL PRINCIPLES SATISFIED
**Ready for**: `/sp.tasks` command to generate implementation tasks
**Estimated Implementation Time**: 4-5 days with TDD approach

