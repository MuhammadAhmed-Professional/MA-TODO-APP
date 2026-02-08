# CLI Interface Contract: Phase 1 Console Todo Application

**Date**: 2025-12-05
**Feature**: 001-console-todo-app
**Purpose**: Define the command-line interface contracts, menu system, input/output specifications

## Main Menu Interface

**Display Format**:
```
=== Todo Application ===

1. Add Task
2. View Task List
3. Update Task
4. Delete Task
5. Mark as Complete
6. Exit

Enter your choice (1-6):
```

**Input Contract**:
- **Valid Inputs**: "1", "2", "3", "4", "5", "6" (string representations)
- **Invalid Inputs**: Any other input (numbers outside range, non-numeric, empty)
- **Error Handling**:
  - Invalid input → Display: "Invalid choice. Please enter a number between 1 and 6"
  - Re-display menu immediately after error
  - No exit on invalid input (loop continues)

**Exit Contract**:
- Choice "6" → Display: "Goodbye!" → Program terminates cleanly (exit code 0)
- Ctrl+C (KeyboardInterrupt) → Display: "Operation cancelled" → Program terminates (exit code 0)

---

## Operation 1: Add Task

**Flow**:
1. Display: "Enter task title:"
2. Accept user input (string, up to 200 chars)
3. Display: "Enter task description (optional, press Enter to skip):"
4. Accept user input (string, up to 1000 chars, empty allowed)
5. Create task → Display confirmation → Return to menu

**Input Contracts**:

**Title Input**:
- **Valid**: Non-empty string, 1-200 characters after strip
- **Invalid Cases**:
  - Empty or whitespace-only → "Title cannot be empty" → Re-prompt for title
  - >200 characters → "Title must be between 1-200 characters" → Re-prompt for title
- **Special Characters**: Accepts all Unicode (emojis, non-Latin scripts)

**Description Input**:
- **Valid**: Any string 0-1000 characters (empty is valid)
- **Invalid Cases**:
  - >1000 characters → "Description cannot exceed 1000 characters" → Re-prompt for description
- **Optional**: Pressing Enter without input → description = "" (valid)

**Success Output**:
```
Task #1 'Buy groceries' created successfully

Press Enter to continue...
```

**Error Output Format**:
```
Error: Title cannot be empty
Please enter a title between 1-200 characters

Enter task title:
```

---

## Operation 2: View Task List

**Flow**:
1. Retrieve all tasks (sorted by ID ascending)
2. Display formatted table
3. Press Enter to return to menu

**Output Contract (Tasks Exist)**:
```
=== Task List ===

ID | Title                | Status | Created
---+---------------------+--------+------------------
1  | Buy groceries        | [ ]    | 2025-12-04 14:30
2  | Call dentist         | [✓]    | 2025-12-04 14:35
3  | Write documentation  | [ ]    | 2025-12-04 14:40

Press Enter to continue...
```

**Output Contract (No Tasks)**:
```
No tasks found. Create your first task to get started!

Press Enter to continue...
```

**Formatting Rules**:
- **Status**: `[✓]` for completed (`completed=True`), `[ ]` for incomplete (`completed=False`)
- **Timestamp**: `YYYY-MM-DD HH:MM` format (minute precision, no seconds)
- **Ordering**: Ascending by ID (creation order, completed and incomplete intermixed)
- **Column Alignment**: Left-aligned text, fixed-width columns

---

## Operation 3: Update Task

**Flow**:
1. Display: "Enter task ID to update:"
2. Accept task ID (integer)
3. If task not found → Error → Return to menu
4. Display: "Enter new title (or press Enter to keep current '{current_title}'):"
5. Accept title input (empty = keep current)
6. Display: "Enter new description (or press Enter to keep current):"
7. Accept description input (empty = keep current)
8. Update task → Display confirmation → Return to menu

**Input Contracts**:

**Task ID Input**:
- **Valid**: Positive integer corresponding to existing task
- **Invalid Cases**:
  - Non-numeric → "Error: Invalid task ID. Please enter a valid number" → Return to menu
  - Non-existent ID → "Error: Task #99 not found" → Return to menu
  - Negative/zero → "Error: Invalid task ID. Please enter a valid number" → Return to menu

**Title Update Input**:
- **Press Enter**: Keep current title (no change)
- **New Value**: 1-200 characters after strip
- **Invalid**:
  - Empty after stripping non-Enter input → "Title cannot be empty" → Re-prompt for title
  - >200 characters → "Title must be between 1-200 characters" → Re-prompt for title

**Description Update Input**:
- **Press Enter**: Keep current description (no change)
- **New Value**: Max 1000 characters
- **Invalid**:
  - >1000 characters → "Description cannot exceed 1000 characters" → Re-prompt for description

**Success Output**:
```
Task #2 updated successfully

Press Enter to continue...
```

---

## Operation 4: Delete Task

**Flow**:
1. Display: "Enter task ID to delete:"
2. Accept task ID (integer)
3. If task not found → Error → Return to menu
4. Display: "Are you sure you want to delete task #2 'Call dentist'? (y/n):"
5. Accept confirmation (y/n)
6. If 'y' → Delete task → Display confirmation → Return to menu
7. If 'n' → Display "Deletion cancelled" → Return to menu

**Input Contracts**:

**Task ID Input**: Same as Update Task

**Confirmation Input**:
- **Valid**: "y" (yes) or "n" (no) - case-insensitive
- **Invalid**:
  - Any other input → "Please enter 'y' for yes or 'n' for no" → Re-prompt for confirmation

**Success Output (Deleted)**:
```
Task #2 deleted successfully

Press Enter to continue...
```

**Cancelled Output**:
```
Deletion cancelled

Press Enter to continue...
```

---

## Operation 5: Mark as Complete

**Flow**:
1. Display: "Enter task ID to mark as complete/incomplete:"
2. Accept task ID (integer)
3. If task not found → Error → Return to menu
4. Toggle completion status
5. Display confirmation → Return to menu

**Input Contracts**:

**Task ID Input**: Same as Update Task

**Success Output (Marked Complete)**:
```
Task #3 marked as complete

Press Enter to continue...
```

**Success Output (Marked Incomplete)**:
```
Task #3 marked as incomplete

Press Enter to continue...
```

**Toggle Behavior**:
- If `completed=False` → Set to `True`, display "marked as complete"
- If `completed=True` → Set to `False`, display "marked as incomplete"

---

## Error Message Standards

**Format Requirements** (per spec SC-003, SC-007):
1. State what went wrong in plain language
2. State valid input requirements
3. No technical jargon (no "ValueError", "Exception", stack traces, variable names)
4. Allow immediate retry (return to input prompt for validation errors, menu for not-found errors)

**Standard Error Messages**:
```
"Title cannot be empty"
"Title must be between 1-200 characters"
"Description cannot exceed 1000 characters"
"Error: Task #99 not found"
"Error: Invalid task ID. Please enter a valid number"
"Invalid choice. Please enter a number between 1 and 6"
"Please enter 'y' for yes or 'n' for no"
```

**Error Recovery**:
- **Validation Errors**: Re-prompt for same input field (don't return to menu)
- **Not Found Errors**: Display error, return to main menu
- **Invalid Menu Choice**: Display error, re-display menu

---

## Input/Output Functions (ui.py contracts)

### Input Functions

```python
def get_menu_choice() -> str:
    """
    Display main menu and get user choice.

    Returns:
        str: User's menu choice ("1"-"6" or invalid input)
    """

def get_task_title(prompt: str = "Enter task title:") -> str:
    """
    Prompt for task title with validation loop.

    Args:
        prompt: Custom prompt message

    Returns:
        str: Valid task title (1-200 chars, non-empty after strip)

    Note: Loops until valid input received; handles validation errors internally
    """

def get_task_description(prompt: str = "Enter task description (optional):") -> str:
    """
    Prompt for task description with validation loop.

    Args:
        prompt: Custom prompt message

    Returns:
        str: Valid task description (0-1000 chars), empty string if skipped

    Note: Loops until valid input received; handles validation errors internally
    """

def get_task_id(prompt: str = "Enter task ID:") -> int | None:
    """
    Prompt for task ID with validation.

    Args:
        prompt: Custom prompt message

    Returns:
        int: Valid positive integer task ID
        None: If invalid input (non-numeric, negative, zero)

    Note: Returns None on first invalid input; caller handles error message
    """

def get_confirmation(prompt: str) -> bool:
    """
    Prompt for yes/no confirmation.

    Args:
        prompt: Question to ask user

    Returns:
        bool: True if 'y', False if 'n'

    Note: Loops until valid 'y' or 'n' received (case-insensitive)
    """

def get_optional_update(field_name: str, current_value: str) -> str | None:
    """
    Prompt for field update with option to keep current value.

    Args:
        field_name: Name of field being updated
        current_value: Current field value

    Returns:
        str: New value if entered
        None: If Enter pressed (keep current)
    """
```

### Output Functions

```python
def display_menu() -> None:
    """Display main menu with all options."""

def display_task_list(tasks: list[Task]) -> None:
    """
    Display formatted task list table.

    Args:
        tasks: List of tasks to display (pre-sorted by ID)

    Note: Handles empty list case with "No tasks found" message
    """

def display_success(message: str) -> None:
    """
    Display success message and wait for Enter.

    Args:
        message: Success message to display
    """

def display_error(message: str) -> None:
    """
    Display error message (formatted for visibility).

    Args:
        message: Error message to display

    Note: Does NOT wait for Enter (caller handles flow control)
    """

def wait_for_enter(prompt: str = "Press Enter to continue...") -> None:
    """Pause execution until user presses Enter."""

def clear_screen() -> None:
    """Clear terminal screen (optional, for better UX)."""
```

---

## Terminal Compatibility

**Assumptions**:
- Terminal width: Minimum 80 characters
- Character encoding: UTF-8 support
- Special characters: `✓`, `[ ]`, table borders display correctly
- Input method: Keyboard text input (no mouse/touch)
- Display: Monospace font for table alignment

**Cross-Platform Support**:
- Works on Linux, macOS, Windows terminals
- No ANSI color codes (optional for Phase 1)
- No cursor manipulation (optional for Phase 1)
- Basic text formatting only (spaces, dashes, brackets)

---

## Summary

**Total Operations**: 6 (5 CRUD + Exit)
**Input Validations**: 7 distinct validation rules
**Error Messages**: 7 standard error messages
**User Prompts**: 10+ distinct prompts
**Output Formats**: 2 (table view + success/error messages)

**Testability**: All I/O functions isolated in ui.py, enabling:
- Unit tests for formatting logic (snapshot testing)
- Mocking input/output for integration tests
- Business logic tests without I/O dependencies
