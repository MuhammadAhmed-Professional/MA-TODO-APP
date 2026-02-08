"""User interface functions for console interaction.

This module contains all input/output functions for the CLI application.
"""

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Task


def get_task_title() -> str:
    """Prompt user for task title.

    Returns:
        The task title entered by the user
    """
    return input("Enter task title: ")


def get_task_description() -> str:
    """Prompt user for task description (optional).

    Returns:
        The task description entered by the user (can be empty)
    """
    return input("Enter task description (optional): ")


def get_task_id() -> int:
    """Prompt user for task ID and return as integer.

    Returns:
        The task ID entered by the user as an integer
    """
    return int(input("Enter task ID: "))


def get_optional_update(prompt: str, current_value: str) -> str | None:
    """Prompt user for optional update, allowing them to keep current value.

    Args:
        prompt: The prompt message (e.g., "Enter new title")
        current_value: The current value to display

    Returns:
        New value if user entered text, None if user pressed Enter (keep current)
    """
    user_input = input(f"{prompt} (current: '{current_value}', press Enter to keep): ")
    return user_input if user_input else None


def get_confirmation(prompt: str) -> bool:
    """Prompt user for yes/no confirmation.

    Args:
        prompt: The confirmation message

    Returns:
        True if user entered 'y' or 'yes' (case-insensitive), False otherwise
    """
    response = input(f"{prompt} (y/n): ").strip().lower()
    return response in ('y', 'yes')


def display_success(message: str) -> None:
    """Display success message and wait for user acknowledgment.

    Args:
        message: The success message to display
    """
    print(f"✓ {message}")
    input("Press Enter to continue...")


def format_timestamp(dt: datetime) -> str:
    """Format datetime as YYYY-MM-DD HH:MM (minute-level precision).

    Args:
        dt: The datetime object to format

    Returns:
        Formatted timestamp string without seconds
    """
    return dt.strftime("%Y-%m-%d %H:%M")


def format_status(completed: bool) -> str:
    """Format task completion status as checkmark or space.

    Args:
        completed: True if task is completed, False if incomplete

    Returns:
        "✓" for completed tasks, " " (single space) for incomplete
    """
    return "✓" if completed else " "


def display_task_list(tasks: list["Task"]) -> None:
    """Display a formatted table of tasks or empty list message.

    Args:
        tasks: List of Task objects to display (can be empty)
    """
    if not tasks:
        print("No tasks found. Create your first task to get started!")
        input("Press Enter to continue...")
        return

    # Display table header
    print(f"{'ID':<5} {'Status':<8} {'Title':<30} {'Created':<20}")
    print("-" * 63)

    # Display each task
    for task in tasks:
        status = format_status(task.completed)
        timestamp = format_timestamp(task.created_at)
        # Truncate title if too long
        title = task.title[:27] + "..." if len(task.title) > 30 else task.title
        print(f"{task.id:<5} {status:<8} {title:<30} {timestamp:<20}")

    input("Press Enter to continue...")


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
    """Get menu choice from user (raw input, no validation).

    Returns:
        The menu choice entered by the user as a string
    """
    return input("\nEnter your choice: ").strip()


def display_error(message: str) -> None:
    """Display formatted error message.

    Args:
        message: The error message to display
    """
    print(f"\n❌ Error: {message}")
    input("Press Enter to continue...")


def wait_for_enter() -> None:
    """Pause and wait for user to press Enter."""
    input("Press Enter to continue...")
