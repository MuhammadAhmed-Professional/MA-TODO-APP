# Python Pytest Mocking & UI Testing Skill

## Purpose
Test Python UI/CLI functions by mocking `input()` and capturing `print()` output using pytest fixtures and the `unittest.mock` module.

## When to Use
- Testing CLI/console applications
- Testing functions that use `input()` for user input
- Testing functions that use `print()` for output
- Isolating UI layer from business logic during tests

## Key Concepts

### Mocking `input()` for User Input
```python
from unittest.mock import patch

@patch('builtins.input', return_value='user input')
def test_function_with_input(mock_input):
    result = get_user_name()  # Calls input() internally
    assert result == 'user input'
```

### Capturing `print()` Output
```python
@patch('sys.stdout', new_callable=StringIO)
def test_function_with_print(mock_stdout):
    display_message("Hello")  # Calls print() internally
    output = mock_stdout.getvalue()
    assert "Hello" in output
```

### Mocking Multiple `input()` Calls
```python
@patch('builtins.input', side_effect=['first', 'second', 'third'])
def test_multiple_inputs(mock_input):
    result1 = input("Prompt 1:")
    result2 = input("Prompt 2:")
    result3 = input("Prompt 3:")
    assert result1 == 'first'
    assert result2 == 'second'
    assert result3 == 'third'
```

## Common Patterns

### Pattern 1: Test UI Input Function
```python
# src/ui.py
def get_task_title() -> str:
    """Prompt user for task title."""
    return input("Enter task title: ")

# tests/test_ui.py
from unittest.mock import patch
from src.ui import get_task_title

@patch('builtins.input', return_value='Buy groceries')
def test_get_task_title(mock_input):
    """Test getting task title from user."""
    result = get_task_title()

    assert result == 'Buy groceries'
    mock_input.assert_called_once_with("Enter task title: ")
```

### Pattern 2: Test UI Output Function
```python
# src/ui.py
def display_success(message: str) -> None:
    """Display success message and wait for Enter."""
    print(f"✓ {message}")
    input("Press Enter to continue...")

# tests/test_ui.py
from io import StringIO
from unittest.mock import patch
from src.ui import display_success

@patch('builtins.input', return_value='')  # Mock Enter key
@patch('sys.stdout', new_callable=StringIO)
def test_display_success(mock_stdout, mock_input):
    """Test success message display."""
    display_success("Task created")

    output = mock_stdout.getvalue()
    assert "✓ Task created" in output
    mock_input.assert_called_once_with("Press Enter to continue...")
```

### Pattern 3: Test Input Validation Loop
```python
# src/ui.py
def get_valid_number() -> int:
    """Get valid number from user (loops until valid)."""
    while True:
        try:
            return int(input("Enter number: "))
        except ValueError:
            print("Invalid number, try again")

# tests/test_ui.py
@patch('builtins.input', side_effect=['abc', 'def', '42'])
@patch('sys.stdout', new_callable=StringIO)
def test_get_valid_number_retry_logic(mock_stdout, mock_input):
    """Test input validation with invalid then valid input."""
    result = get_valid_number()

    assert result == 42
    output = mock_stdout.getvalue()
    assert output.count("Invalid number") == 2  # Two failed attempts
```

### Pattern 4: Test Integration Workflow
```python
# tests/test_integration.py
@patch('builtins.input', side_effect=['1', 'Buy milk', 'Get 2% milk', ''])
@patch('sys.stdout', new_callable=StringIO)
def test_add_task_workflow(mock_stdout, mock_input):
    """Test full add task workflow from menu to confirmation."""
    storage = InMemoryStorage()
    main_loop_one_iteration(storage)  # Runs menu, gets choice, handles action

    output = mock_stdout.getvalue()
    assert "Task #1 'Buy milk' created successfully" in output

    # Verify storage state
    tasks = storage.get_all()
    assert len(tasks) == 1
    assert tasks[0].title == "Buy milk"
```

## Pytest Fixtures for Reusability

```python
# conftest.py or test file
import pytest
from unittest.mock import patch, MagicMock
from io import StringIO

@pytest.fixture
def mock_input():
    """Fixture for mocking input()."""
    with patch('builtins.input') as mock:
        yield mock

@pytest.fixture
def mock_stdout():
    """Fixture for capturing stdout."""
    with patch('sys.stdout', new_callable=StringIO) as mock:
        yield mock

# Usage
def test_with_fixtures(mock_input, mock_stdout):
    mock_input.return_value = 'test'
    print("Hello")
    assert mock_stdout.getvalue() == "Hello\n"
```

## Advanced Techniques

### Mocking with Context Manager
```python
def test_temporary_mock():
    with patch('builtins.input', return_value='temp'):
        result = input("Prompt:")
        assert result == 'temp'
    # Mock is automatically restored after with block
```

### Verifying Mock Calls
```python
@patch('builtins.input', return_value='test')
def test_verify_calls(mock_input):
    input("First prompt:")
    input("Second prompt:")

    assert mock_input.call_count == 2
    mock_input.assert_any_call("First prompt:")
    mock_input.assert_any_call("Second prompt:")
```

### Mocking Specific Module Functions
```python
# If function is imported: from ui import get_input
# Mock at the call site, not the definition
@patch('main.get_input', return_value='mocked')  # main imports get_input
def test_main_function(mock_get_input):
    result = main.handle_add_task()
    ...
```

## Common Pitfalls

### ❌ Wrong: Mock at definition
```python
@patch('ui.input')  # Won't work if input is from builtins
def test_wrong():
    pass
```

### ✅ Right: Mock builtins.input
```python
@patch('builtins.input')  # Correct
def test_right():
    pass
```

### ❌ Wrong: Forget to handle all inputs
```python
@patch('builtins.input', return_value='only_one')
def test_multiple_calls():
    input("First")
    input("Second")  # Will reuse 'only_one' - might be unintended
```

### ✅ Right: Use side_effect for multiple
```python
@patch('builtins.input', side_effect=['first', 'second'])
def test_multiple_calls():
    assert input("First") == 'first'
    assert input("Second") == 'second'
```

## Testing Checklist
- ✅ Mock all `input()` calls with appropriate values
- ✅ Capture `print()` output if testing display functions
- ✅ Use `side_effect` for multiple input calls
- ✅ Verify mock was called with expected prompts
- ✅ Test both happy path and error handling
- ✅ Ensure mocks are cleaned up (use decorators/fixtures)

## Example: Complete UI Test Suite

```python
"""Tests for UI layer functions."""

import pytest
from io import StringIO
from unittest.mock import patch
from src.ui import get_task_title, get_task_description, display_success

class TestUIInputs:
    """Tests for UI input functions."""

    @patch('builtins.input', return_value='Buy groceries')
    def test_get_task_title_basic(self, mock_input):
        result = get_task_title()
        assert result == 'Buy groceries'
        mock_input.assert_called_once_with("Enter task title: ")

    @patch('builtins.input', return_value='Get milk and bread')
    def test_get_task_description_basic(self, mock_input):
        result = get_task_description()
        assert result == 'Get milk and bread'
        mock_input.assert_called_once_with("Enter task description (optional): ")

class TestUIOutputs:
    """Tests for UI output functions."""

    @patch('builtins.input', return_value='')
    @patch('sys.stdout', new_callable=StringIO)
    def test_display_success(self, mock_stdout, mock_input):
        display_success("Task #1 'Buy groceries' created successfully")

        output = mock_stdout.getvalue()
        assert "Task #1 'Buy groceries' created successfully" in output
        mock_input.assert_called_once()
```
