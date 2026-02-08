# Python Pytest Comprehensive Testing Skill

## Purpose
Write comprehensive pytest test suites covering unit tests, integration tests, fixtures, parametrization, and advanced patterns for Python projects.

## When to Use
- Building complete test coverage for Python modules
- Creating reusable pytest fixtures for shared test setup
- Testing complex workflows with multiple dependencies
- Parameterized testing for edge cases and input variations
- Mocking external dependencies and side effects

## Prerequisites
- pytest installed (`uv add --dev pytest pytest-cov pytest-mock`)
- Project structure: `src/<module>/` and `tests/`
- Understanding of pytest discovery and assertion rewriting
- Familiarity with unittest.mock for mocking

## Project Structure

```
tests/
├── conftest.py              # Shared fixtures and plugins
├── test_models.py           # Data model tests
├── test_storage.py          # Persistence layer tests
├── test_operations.py       # Business logic tests
├── test_ui.py               # User interface tests
└── test_integration.py      # End-to-end workflow tests
```

## Workflow

### Phase 1: Setup and Configuration

```python
# conftest.py - Root test configuration
import pytest
from pathlib import Path

# Register custom markers
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )

# Project root path
PROJECT_ROOT = Path(__file__).parent.parent
```

**Validation**: Run `pytest --collect-only -m unit` to verify markers work.

### Phase 2: Create Shared Fixtures

```python
# tests/conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def project_root():
    """Return project root directory."""
    return Path(__file__).parent.parent

@pytest.fixture
def temp_data_file(tmp_path):
    """Create temporary data file for testing."""
    data_file = tmp_path / "test_data.json"
    data_file.write_text('{"test": "data"}')
    return data_file

@pytest.fixture
def sample_task():
    """Create sample task for testing."""
    from src.todo_app.models import Task
    from datetime import datetime
    return Task(id=1, title="Test Task", description="Test", completed=False, created_at=datetime.now())

@pytest.fixture
def storage():
    """Create fresh storage for each test."""
    from src.todo_app.storage import InMemoryStorage
    return InMemoryStorage()
```

**Validation**: Run `pytest --fixtures` to see registered fixtures.

### Phase 3: Unit Tests with Parametrization

```python
# tests/test_operations.py
import pytest
from src.todo_app.operations import validate_title, ValidationError

class TestValidation:
    """Test input validation functions."""

    @pytest.mark.parametrize("invalid_title,expected_error", [
        ("", "cannot be empty"),
        ("   ", "cannot be empty"),
        ("x" * 201, "must be between 1-200 characters"),
    ])
    def test_validate_title_invalid(self, invalid_title, expected_error):
        """Test title validation with various invalid inputs."""
        with pytest.raises(ValidationError, match=expected_error):
            validate_title(invalid_title)

    @pytest.mark.parametrize("valid_title", [
        "Valid Task",
        "Task with numbers 123",
        "x" * 200,  # Maximum length
    ])
    def test_validate_title_valid(self, valid_title):
        """Test title validation with valid inputs."""
        result = validate_title(valid_title)
        assert result == valid_title.strip()
```

**Validation**: Run `pytest tests/test_operations.py -v` to verify parametrized tests.

### Phase 4: Integration Tests

```python
# tests/test_integration.py
import pytest
from src.todo_app.storage import InMemoryStorage
from src.todo_app.operations import create_task, list_tasks

@pytest.mark.integration
class TestCreateTaskWorkflow:
    """Test complete create task workflow."""

    @pytest.fixture
    def storage(self):
        """Create fresh storage for each test."""
        return InMemoryStorage()

    def test_create_and_retrieve_task(self, storage):
        """Test creating and retrieving a task."""
        # Arrange
        title = "Buy groceries"
        description = "Get milk and bread"

        # Act
        created = create_task(storage, title, description)
        all_tasks = list_tasks(storage)

        # Assert
        assert created.title == title
        assert created.description == description
        assert len(all_tasks) == 1
        assert all_tasks[0].id == created.id
```

**Validation**: Run `pytest -m integration -v` to run integration tests.

### Phase 5: Advanced Mocking Patterns

```python
# tests/test_ui.py
import pytest
from unittest.mock import patch
from io import StringIO

@patch('builtins.input', return_value='Test Task')
def test_get_task_title(mock_input):
    """Test getting task title from user."""
    from src.todo_app.ui import get_task_title
    result = get_task_title()
    assert result == 'Test Task'
    mock_input.assert_called_once_with("Enter task title: ")

@patch('sys.stdout', new_callable=StringIO)
def test_display_success(mock_stdout):
    """Test success message display."""
    from src.todo_app.ui import display_success
    with patch('builtins.input'):  # Mock the "Press Enter"
        display_success("Task created")
    output = mock_stdout.getvalue()
    assert "✓ Task created" in output
```

**Validation**: Run `pytest tests/test_ui.py -v` to verify mocking works.

## Best Practices

### Test Organization
- **Unit tests**: Fast, isolated, single responsibility
- **Integration tests**: Test interactions between components
- **Mark tests**: Use `@pytest.mark.unit`, `@pytest.mark.integration`
- **Separate fixtures**: Move shared fixtures to `conftest.py`

### Assertion Patterns
```python
# Equality
assert result == expected

# Type checking
assert isinstance(result, Task)

# Exceptions
with pytest.raises(ValidationError, match="specific message"):
    function_that_raises()

# Collections
assert task in task_list
assert len(tasks) == 3

# Boolean conditions
assert task.completed
assert not task.archived
```

### Fixture Scope
```python
@pytest.fixture(scope="function")  # New instance per test (default)
def fresh_storage():
    return InMemoryStorage()

@pytest.fixture(scope="class")  # Shared across class tests
def expensive_setup():
    return ExpensiveObject()

@pytest.fixture(scope="session")  # Shared across all tests
def database_connection():
    return Database()
```

## Common Patterns

### Pattern 1: Fixture with Setup and Teardown
```python
@pytest.fixture
def database_session():
    """Setup database, yield for test, teardown."""
    db = Database()
    db.connect()
    yield db
    db.close()
```

### Pattern 2: Parametrized Fixtures
```python
@pytest.fixture(params=["json", "csv", "xml"])
def data_format(request):
    """Test with multiple data formats."""
    return request.param

def test_export_formats(data_format):
    """Test exporting in various formats."""
    exporter = DataExporter(format=data_format)
    result = exporter.export([])
    assert result is not None
```

### Pattern 3: Factory Fixture
```python
@pytest.fixture
def task_factory():
    """Create tasks with customizable parameters."""
    def _create(title="Default", completed=False, **kwargs):
        from src.todo_app.models import Task
        return Task(id=0, title=title, completed=completed, **kwargs)
    return _create

def test_multiple_tasks(task_factory):
    tasks = [
        task_factory(title="Task 1"),
        task_factory(title="Task 2", completed=True),
    ]
    assert len(tasks) == 2
```

## Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_models.py

# Specific test class
pytest tests/test_models.py::TestTaskModel

# By marker
pytest -m unit               # Only unit tests
pytest -m integration        # Only integration tests

# With coverage
pytest --cov=src --cov-report=html

# Verbose output
pytest -v

# Show print statements
pytest -s

# Stop on first failure
pytest -x
```

## Testing Checklist
- ✅ Unit tests for all public functions
- ✅ Integration tests for workflows
- ✅ Edge cases and boundary conditions tested
- ✅ Error paths and exceptions tested
- ✅ Fixtures for common setup/teardown
- ✅ Parametrized tests for input variations
- ✅ Mocks for external dependencies only
- ✅ Coverage ≥80%
- ✅ Tests run in any order (no dependencies)
