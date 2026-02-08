# Python TDD Implementation Skill

## Purpose
Implement Python features following strict Test-Driven Development (TDD) methodology with Red-Green-Refactor cycles.

## When to Use
- Implementing new Python functions/classes with test coverage requirements
- Following TDD workflow: write failing tests → implement → refactor
- Projects requiring 80%+ test coverage
- Python 3.13+ projects with pytest

## Prerequisites
- pytest installed (`uv add --dev pytest pytest-cov`)
- Project structure: `src/<module>/` and `tests/`
- Clear specification of function behavior

## Workflow

### 1. RED Phase - Write Failing Tests
```python
# tests/test_<module>.py
import pytest
from src.<module>.<file> import <function>

def test_<function>_<scenario>():
    """Test <function> with <scenario>."""
    # Arrange
    input_data = ...
    expected = ...

    # Act
    result = <function>(input_data)

    # Assert
    assert result == expected
```

**Validation**: Run `uv run pytest tests/test_<module>.py -v` → Tests should FAIL

### 2. GREEN Phase - Implement Minimum Code
```python
# src/<module>/<file>.py
def <function>(<params>) -> <return_type>:
    """Brief description.

    Args:
        param: Description

    Returns:
        Description

    Raises:
        ExceptionType: When condition
    """
    # Minimum implementation to pass tests
    ...
```

**Validation**: Run `uv run pytest tests/test_<module>.py -v` → Tests should PASS

### 3. REFACTOR Phase - Clean Code
- Add comprehensive docstrings
- Improve variable names
- Extract helper functions (if >50 lines)
- Add type hints
- Run `uv run pytest` → Tests must remain GREEN

### 4. Coverage Validation
```bash
uv run pytest --cov=src/<module> --cov-report=term-missing
```
**Target**: ≥80% coverage

## Best Practices

### Test Organization
```
tests/
├── test_models.py      # Data models
├── test_storage.py     # Data persistence
├── test_operations.py  # Business logic
├── test_ui.py          # User interface
└── test_integration.py # End-to-end workflows
```

### Test Naming Convention
- `test_<function>_<scenario>` → Unit tests
- `test_<feature>_<workflow>` → Integration tests
- Use descriptive names: `test_validate_title_rejects_empty_string`

### Assertion Patterns
```python
# Equality
assert result == expected

# Exceptions
with pytest.raises(ValidationError, match="Title cannot be empty"):
    validate_title("")

# Type checks
assert isinstance(result, Task)
assert result.id > 0

# Boolean
assert task.completed is True
```

### Mock External Dependencies
```python
from unittest.mock import Mock, patch

def test_with_storage_mock():
    mock_storage = Mock()
    mock_storage.add.return_value = Task(id=1, title="Test")
    result = create_task(mock_storage, "Test", "")
    assert result.id == 1
```

## Common Patterns

### Testing Validation Functions
```python
@pytest.mark.parametrize("invalid_input,error_msg", [
    ("", "cannot be empty"),
    ("x" * 201, "must be between 1-200 characters"),
    ("   ", "cannot be empty"),
])
def test_validate_title_invalid_inputs(invalid_input, error_msg):
    with pytest.raises(ValidationError, match=error_msg):
        validate_title(invalid_input)
```

### Testing CRUD Operations
```python
def test_storage_add_increments_id():
    storage = InMemoryStorage()
    task1 = storage.add("Task 1", "")
    task2 = storage.add("Task 2", "")
    assert task1.id == 1
    assert task2.id == 2
```

## Troubleshooting

### Tests Not Found
```bash
# Verify test discovery
uv run pytest --collect-only
```

### Import Errors
```python
# Use absolute imports from project root
from src.module.file import function
# NOT: from module.file import function
```

### Coverage Too Low
1. Run with missing lines: `--cov-report=term-missing`
2. Identify uncovered branches
3. Add edge case tests
4. Test error handling paths

## Example: Complete TDD Cycle

```python
# 1. RED: Write failing test
def test_validate_title_rejects_empty():
    with pytest.raises(ValidationError, match="Title cannot be empty"):
        validate_title("")

# Run: pytest → FAILS (function doesn't exist)

# 2. GREEN: Implement minimum code
def validate_title(title: str) -> str:
    if not title or title.strip() == "":
        raise ValidationError("Title cannot be empty")
    return title

# Run: pytest → PASSES

# 3. REFACTOR: Add full validation
def validate_title(title: str) -> str:
    """Validate task title meets requirements.

    Args:
        title: The task title to validate

    Returns:
        The validated title (stripped)

    Raises:
        ValidationError: If title is empty or exceeds 200 chars
    """
    cleaned = title.strip()
    if not cleaned:
        raise ValidationError("Title cannot be empty")
    if len(cleaned) > 200:
        raise ValidationError("Title must be between 1-200 characters")
    return cleaned

# Run: pytest → STILL PASSES
```

## Success Criteria
- ✅ All tests pass (`pytest` exit code 0)
- ✅ Coverage ≥80% (`--cov` report)
- ✅ No linting errors (`ruff check`)
- ✅ Type hints present (`mypy` if configured)
- ✅ Docstrings on all public functions
