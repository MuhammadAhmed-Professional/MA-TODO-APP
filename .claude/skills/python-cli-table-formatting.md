# Python CLI Table Formatting Skill

## Purpose
Format and display data as tables in command-line interfaces using Python's built-in string formatting. Includes patterns for headers, rows, alignment, truncation, and empty state handling.

## When to Use
- Displaying lists of records (tasks, users, products, etc.)
- Creating formatted reports in CLI applications
- Showing structured data with multiple columns
- Implementing "view all" or "list" features

## Key Concepts

### Column Alignment with f-strings
Python's f-string formatting supports alignment operators:
- `{value:<width}` - Left-align
- `{value:>width}` - Right-align
- `{value:^width}` - Center-align

```python
# Left-aligned columns (common for text)
print(f"{'ID':<5} {'Name':<20} {'Status':<10}")
print(f"{1:<5} {'Alice':<20} {'Active':<10}")

# Right-aligned (common for numbers)
print(f"{'Amount':>10}")
print(f"{1234.56:>10}")
```

### Table Structure Pattern
1. Display header row with column labels
2. Display separator line (dashes)
3. Iterate and display each data row
4. Handle empty state with helpful message

## Common Patterns

### Pattern 1: Basic Table Display

```python
def display_users(users: list[User]) -> None:
    """Display users as a formatted table."""
    if not users:
        print("No users found.")
        input("Press Enter to continue...")
        return

    # Header
    print(f"{'ID':<5} {'Name':<20} {'Email':<30} {'Status':<10}")
    print("-" * 65)

    # Rows
    for user in users:
        print(f"{user.id:<5} {user.name:<20} {user.email:<30} {user.status:<10}")

    input("Press Enter to continue...")
```

### Pattern 2: Text Truncation for Long Values

```python
def display_tasks(tasks: list[Task]) -> None:
    """Display tasks with title truncation."""
    if not tasks:
        print("No tasks found. Create your first task to get started!")
        input("Press Enter to continue...")
        return

    print(f"{'ID':<5} {'Title':<30} {'Created':<20}")
    print("-" * 55)

    for task in tasks:
        # Truncate title if too long
        title = task.title[:27] + "..." if len(task.title) > 30 else task.title
        timestamp = format_timestamp(task.created_at)
        print(f"{task.id:<5} {title:<30} {timestamp:<20}")

    input("Press Enter to continue...")
```

### Pattern 3: Boolean/Status Formatting

```python
def format_status(completed: bool) -> str:
    """Format boolean status as symbol."""
    return "✓" if completed else " "

def display_task_list(tasks: list[Task]) -> None:
    """Display tasks with completion status."""
    if not tasks:
        print("No tasks found.")
        input("Press Enter to continue...")
        return

    print(f"{'ID':<5} {'Status':<8} {'Title':<30}")
    print("-" * 43)

    for task in tasks:
        status = format_status(task.completed)
        print(f"{task.id:<5} {status:<8} {task.title:<30}")

    input("Press Enter to continue...")
```

### Pattern 4: Datetime Formatting

```python
from datetime import datetime

def format_timestamp(dt: datetime) -> str:
    """Format datetime as YYYY-MM-DD HH:MM (no seconds)."""
    return dt.strftime("%Y-%m-%d %H:%M")

def display_events(events: list[Event]) -> None:
    """Display events with formatted timestamps."""
    print(f"{'ID':<5} {'Event':<25} {'Date':<17}")
    print("-" * 47)

    for event in events:
        timestamp = format_timestamp(event.created_at)
        print(f"{event.id:<5} {event.name:<25} {timestamp:<17}")
```

### Pattern 5: Multi-Value Display (Combining Multiple Fields)

```python
def display_products(products: list[Product]) -> None:
    """Display products with price and stock."""
    if not products:
        print("No products available.")
        input("Press Enter to continue...")
        return

    print(f"{'ID':<5} {'Name':<30} {'Price':>10} {'Stock':>8}")
    print("-" * 53)

    for product in products:
        # Format currency
        price_str = f"${product.price:.2f}"
        print(f"{product.id:<5} {product.name:<30} {price_str:>10} {product.stock:>8}")

    input("Press Enter to continue...")
```

### Pattern 6: Conditional Formatting

```python
def display_orders(orders: list[Order]) -> None:
    """Display orders with status-based symbols."""
    print(f"{'ID':<5} {'Status':<10} {'Customer':<20} {'Amount':>10}")
    print("-" * 45)

    for order in orders:
        # Choose symbol based on status
        if order.status == "completed":
            symbol = "✓"
        elif order.status == "pending":
            symbol = "⏳"
        else:
            symbol = "✗"

        status_display = f"{symbol} {order.status}"
        amount_str = f"${order.amount:.2f}"
        print(f"{order.id:<5} {status_display:<10} {order.customer:<20} {amount_str:>10}")
```

## Advanced Techniques

### Dynamic Column Width Calculation

```python
def display_dynamic_table(items: list[dict]) -> None:
    """Display table with columns sized to content."""
    if not items:
        print("No items.")
        return

    # Calculate max width for each column
    keys = items[0].keys()
    widths = {key: max(len(str(key)), max(len(str(item[key])) for item in items))
              for key in keys}

    # Header
    header = " ".join(f"{key:<{widths[key]}}" for key in keys)
    print(header)
    print("-" * len(header))

    # Rows
    for item in items:
        row = " ".join(f"{str(item[key]):<{widths[key]}}" for key in keys)
        print(row)
```

### Testing Table Output with Mocks

```python
# test_ui.py
from io import StringIO
from unittest.mock import patch
from datetime import datetime
from models import Task
from ui import display_task_list

@patch('builtins.input', return_value='')
@patch('sys.stdout', new_callable=StringIO)
def test_display_task_list_with_tasks(mock_stdout, mock_input):
    """Test displaying task list as formatted table."""
    tasks = [
        Task(id=1, title="Buy groceries", completed=False,
             created_at=datetime(2025, 12, 4, 14, 30, 0)),
        Task(id=2, title="Call dentist", completed=True,
             created_at=datetime(2025, 12, 4, 15, 45, 0)),
    ]

    display_task_list(tasks)

    output = mock_stdout.getvalue()

    # Verify headers
    assert "ID" in output
    assert "Status" in output
    assert "Title" in output

    # Verify data
    assert "Buy groceries" in output
    assert "Call dentist" in output
    assert "2025-12-04 14:30" in output
    assert "✓" in output  # Completed status

    mock_input.assert_called_once_with("Press Enter to continue...")
```

### Empty State Pattern

```python
def display_with_empty_message(items: list, empty_msg: str) -> None:
    """Generic display with custom empty message."""
    if not items:
        print(empty_msg)
        input("Press Enter to continue...")
        return

    # Display logic here...

# Usage
display_with_empty_message(
    tasks,
    "No tasks found. Create your first task to get started!"
)
```

## Common Pitfalls

### ❌ Wrong: Hardcoded Width Not Matching Data

```python
# Column width 10 but data is 15 chars - breaks alignment
print(f"{'LongColumnName':<10}")
```

### ✅ Right: Width Matches Longest Expected Value

```python
# Column width accounts for longest value
print(f"{'LongColumnName':<20}")
```

### ❌ Wrong: Forgetting Empty State Handling

```python
def display_items(items):
    print("ID | Name")
    for item in items:  # Crashes if items is empty? No, but looks bad
        print(f"{item.id} | {item.name}")
```

### ✅ Right: Always Handle Empty State

```python
def display_items(items):
    if not items:
        print("No items found.")
        input("Press Enter to continue...")
        return

    print("ID | Name")
    for item in items:
        print(f"{item.id} | {item.name}")

    input("Press Enter to continue...")
```

### ❌ Wrong: Not Truncating Long Text

```python
# Title could be 200 chars - breaks table layout
print(f"{task.title:<30}")
```

### ✅ Right: Truncate with Ellipsis

```python
title = task.title[:27] + "..." if len(task.title) > 30 else task.title
print(f"{title:<30}")
```

## Testing Checklist
- ✅ Test with empty list (verify empty message)
- ✅ Test with single item
- ✅ Test with multiple items
- ✅ Test with long text values (verify truncation)
- ✅ Test alignment (visual inspection or string assertions)
- ✅ Test special characters (✓, ✗, emojis)
- ✅ Mock stdout to capture and verify output

## Example: Complete Implementation

```python
"""UI functions for displaying tasks."""

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Task


def format_timestamp(dt: datetime) -> str:
    """Format datetime as YYYY-MM-DD HH:MM."""
    return dt.strftime("%Y-%m-%d %H:%M")


def format_status(completed: bool) -> str:
    """Format completion status as checkmark or space."""
    return "✓" if completed else " "


def display_task_list(tasks: list["Task"]) -> None:
    """Display formatted table of tasks or empty message."""
    if not tasks:
        print("No tasks found. Create your first task to get started!")
        input("Press Enter to continue...")
        return

    # Header
    print(f"{'ID':<5} {'Status':<8} {'Title':<30} {'Created':<20}")
    print("-" * 63)

    # Rows
    for task in tasks:
        status = format_status(task.completed)
        timestamp = format_timestamp(task.created_at)
        title = task.title[:27] + "..." if len(task.title) > 30 else task.title
        print(f"{task.id:<5} {status:<8} {title:<30} {timestamp:<20}")

    input("Press Enter to continue...")
```

## Summary

Key principles for CLI table formatting:
1. **Consistent alignment**: Left for text, right for numbers
2. **Fixed widths**: Calculate based on longest expected value
3. **Truncation**: Handle long text with ellipsis
4. **Empty state**: Always provide helpful message
5. **Separation**: Use dashes or equals for visual clarity
6. **Formatting helpers**: Extract datetime/status formatting to functions
7. **User acknowledgment**: Wait for Enter before returning to menu
