# Research: Phase 1 Console Todo Application

**Date**: 2025-12-05
**Feature**: 001-console-todo-app
**Purpose**: Document technology choices, patterns, and best practices for Phase 1 implementation

## Technology Decisions

### Decision 1: Python Dataclasses for Task Entity
**Decision**: Use Python `@dataclass` decorator for Task model
**Rationale**:
- Built-in to Python 3.13+ (no external dependencies)
- Automatic `__init__`, `__repr__`, `__eq__` generation reduces boilerplate
- Native support for type hints and field defaults
- Immutable option with `frozen=True` if needed
- Simpler than Pydantic for Phase 1 (no validation DSL needed)

**Alternatives Considered**:
- **Pydantic**: More powerful validation, but adds external dependency and complexity for simple use case
- **NamedTuple**: Immutable and lightweight, but lacks flexibility for future fields
- **Regular class**: More boilerplate, manual implementation of dunder methods

**Phase 2 Impact**: Dataclass fields map directly to database columns; easy migration to SQLAlchemy or similar ORM

### Decision 2: Storage Abstraction Layer Pattern
**Decision**: Implement `TaskStorage` abstract base class with `InMemoryStorage` concrete implementation

**Rationale**:
- Enables Phase 2 database migration without changing business logic
- Follows Dependency Inversion Principle (depend on abstractions)
- Facilitates testing with mock storage implementations
- Isolates ID generation logic in one place

**Pattern**:
```python
class TaskStorage(ABC):
    @abstractmethod
    def add(self, task: Task) -> int: ...
    @abstractmethod
    def get(self, task_id: int) -> Task | None: ...
    @abstractmethod
    def get_all(self) -> list[Task]: ...
    @abstractmethod
    def update(self, task_id: int, updates: dict) -> bool: ...
    @abstractmethod
    def delete(self, task_id: int) -> bool: ...
    @abstractmethod
    def toggle_complete(self, task_id: int) -> bool: ...
```

**Alternatives Considered**:
- **Direct dict manipulation**: Simpler short-term, but couples business logic to storage; hard to migrate
- **Repository pattern**: More enterprise-y, adds unnecessary complexity for 5 operations
- **DAO pattern**: Similar to chosen approach but heavier; abstraction layer is lighter and sufficient

**Phase 2 Impact**: Create `DatabaseStorage(TaskStorage)` class; swap in main.py; zero changes to operations.py

### Decision 3: Separation of UI and Business Logic
**Decision**: Split into `ui.py` (I/O functions) and `operations.py` (business logic)

**Rationale**:
- `ui.py` handles all `input()` and `print()` calls, formatting, prompts
- `operations.py` contains pure functions: take inputs, return results (no I/O)
- Enables unit testing of business logic without mocking input/output
- `main.py` orchestrates: calls ui functions, passes to operations, handles operation results

**Pattern**:
```python
# ui.py
def get_task_title() -> str | None:
    """Prompt user for task title, validate, return or None on cancel."""

def display_task_list(tasks: list[Task]) -> None:
    """Format and print task list table."""

# operations.py
def create_task(storage: TaskStorage, title: str, description: str) -> Task:
    """Business logic: validate, create task, save to storage."""

def list_tasks(storage: TaskStorage) -> list[Task]:
    """Business logic: retrieve and sort tasks."""
```

**Alternatives Considered**:
- **MVC pattern**: Overkill for CLI; no "View" rendering beyond print statements
- **Single module**: Violates SRP; makes testing harder; exceeds 300-line limit
- **CLI framework (click, typer)**: Adds dependency; spec requires simple numbered menu, not sophisticated CLI

**Phase 2 Impact**: Replace `ui.py` with web forms (Flask/FastAPI), keep operations.py unchanged

### Decision 4: Match/Case for Menu Dispatcher
**Decision**: Use Python 3.10+ `match/case` statement for menu selection routing

**Rationale**:
- Modern Python idiom (constitution principle VI)
- More readable than long if/elif chains
- Exhaustiveness checking potential with type checkers
- Pattern matching capabilities for future expansion

**Pattern**:
```python
match choice:
    case "1":
        # Add task flow
    case "2":
        # View tasks flow
    case "3":
        # Update task flow
    case "4":
        # Delete task flow
    case "5":
        # Mark complete flow
    case "6":
        # Exit
    case _:
        # Invalid choice error
```

**Alternatives Considered**:
- **if/elif chain**: Works but less Pythonic, harder to extend
- **Dictionary dispatch**: More dynamic but less readable; overkill for 6 fixed options
- **Command pattern**: Too heavyweight for simple menu; adds unnecessary abstraction

### Decision 5: ID Generation Strategy
**Decision**: Track `_next_id` counter in storage layer; increment on add; never reuse deleted IDs

**Rationale**:
- Spec requirement from `/sp.clarify`: "IDs never reused after deletion"
- Matches database auto-increment behavior for Phase 2 compatibility
- Simple implementation: `_next_id += 1` on each add
- Prevents user confusion when referencing tasks by ID

**Implementation**:
```python
class InMemoryStorage(TaskStorage):
    def __init__(self):
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1  # Always increments, never resets

    def add(self, task: Task) -> int:
        task_id = self._next_id
        self._next_id += 1  # Increment even if later deletion occurs
        self._tasks[task_id] = task
        return task_id
```

**Alternatives Considered**:
- **Reuse deleted IDs**: Simpler (fill gaps) but violates spec clarification; confuses users
- **UUID**: Overkill for Phase 1; harder to reference (can't say "task 3"); breaks Phase 2 migration assumptions
- **Timestamp-based**: Not guaranteed unique; harder to test; non-sequential display

### Decision 6: Timestamp Format
**Decision**: Store as `datetime.datetime`, display as `YYYY-MM-DD HH:MM` (minute precision)

**Rationale**:
- Spec requirement from `/sp.clarify`: minute-level precision
- Store full datetime for flexibility (Phase 2 might need seconds)
- Format on display using `strftime("%Y-%m-%d %H:%M")`
- Uses `datetime.now()` at creation time

**Implementation**:
```python
from datetime import datetime

@dataclass
class Task:
    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)
```

**Alternatives Considered**:
- **String storage**: Harder to query/sort in Phase 2; loses timezone info
- **Second precision**: Spec specifies minute-level; simpler display
- **Unix timestamp**: Less readable; requires conversion on display

### Decision 7: Validation Strategy
**Decision**: Validate at operation layer before storage; raise custom exceptions; handle in main loop

**Rationale**:
- Operations layer validates business rules (title 1-200 chars, description ≤1000 chars)
- Storage layer assumes valid input (no duplicate validation)
- Custom exceptions: `ValidationError`, `TaskNotFoundError`
- Main loop catches exceptions, uses ui functions to display errors, re-prompts

**Pattern**:
```python
# operations.py
class ValidationError(Exception): pass
class TaskNotFoundError(Exception): pass

def validate_title(title: str) -> None:
    if not title or not title.strip():
        raise ValidationError("Title cannot be empty")
    if len(title) > 200:
        raise ValidationError("Title must be between 1-200 characters")

# main.py
try:
    task = create_task(storage, title, description)
    ui.display_success(f"Task #{task.id} created successfully")
except ValidationError as e:
    ui.display_error(str(e))
    # Re-prompt or return to menu
```

**Alternatives Considered**:
- **Validation in ui.py**: Duplicates logic; harder to test; business rules leak into presentation
- **Validation in models.py**: Dataclass validators (Pydantic-style) add complexity; not needed for 5 fields
- **No exceptions**: Return Result type (Ok/Err); more functional but less Pythonic; verbose for simple cases

### Decision 8: Testing Strategy
**Decision**: Pytest with fixtures for storage, test-per-acceptance-scenario structure

**Rationale**:
- Pytest is constitution requirement
- Fixtures provide clean storage instances for each test (isolation)
- Each spec acceptance scenario becomes one or more test functions
- Parametrized tests for boundary conditions (200 chars, 1000 chars, etc.)
- Coverage target: 80% minimum (constitution requirement)

**Test Organization**:
- `test_models.py`: Task creation, field validation, equality
- `test_storage.py`: CRUD operations, ID generation, ID non-reuse after deletion
- `test_operations.py`: Business logic, validation errors, edge cases
- `test_ui.py`: Formatting functions, table display (snapshot testing)
- `test_integration.py`: Full workflows (add→view→update→delete)

**TDD Workflow**:
1. **Red**: Write test for acceptance scenario (failing)
2. **Green**: Implement minimum code to pass test
3. **Refactor**: Clean up, extract helpers, maintain tests green

**Fixtures Example**:
```python
@pytest.fixture
def storage():
    return InMemoryStorage()

@pytest.fixture
def sample_task():
    return Task(id=1, title="Test Task", description="Test Desc")
```

## Best Practices Research

### Python 3.13 CLI Application Patterns
- **Entry Point**: `if __name__ == "__main__":` in main.py with `main()` function
- **Type Hints**: Use modern union syntax `str | None` (not `Optional[str]`)
- **Dataclasses**: Use `field(default_factory=...)` for mutable defaults
- **Error Handling**: Catch `KeyboardInterrupt` for Ctrl+C graceful exit
- **UTF-8**: Ensure `sys.stdout.reconfigure(encoding='utf-8')` for unicode support

### Clean Architecture for CLI
- **Dependency Flow**: main.py → operations.py → storage.py → models.py
- **No Circular Dependencies**: Each layer depends only on layers below
- **Testability**: Pure functions in operations.py; I/O isolated in ui.py
- **Single Responsibility**: Each module has one clear purpose

### Phase 2 Migration Patterns
- **Storage Abstraction**: Abstract base class enables drop-in database implementation
- **Data Model Compatibility**: Dataclass fields → SQLAlchemy columns (1:1 mapping)
- **Zero Business Logic Changes**: operations.py stays the same; only storage implementation swaps
- **Configuration**: Pass storage instance to operations (dependency injection)

## Open Questions (None)

All technical decisions are clear based on specification and constitution. No unknowns remain.

## References

- Python Dataclasses: https://docs.python.org/3/library/dataclasses.html
- Python match/case: https://peps.python.org/pep-0636/
- Pytest fixtures: https://docs.pytest.org/en/stable/fixture.html
- Clean Architecture: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
- PEP 8 Style Guide: https://peps.python.org/pep-0008/
