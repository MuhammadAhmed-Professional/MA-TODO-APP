"""Main application orchestration and workflow handlers.

This module contains handler functions that coordinate between
UI layer, business logic, and storage layer.
"""

from .storage import TaskStorage, InMemoryStorage
from .operations import (
    create_task,
    list_tasks,
    toggle_task_complete,
    update_task,
    delete_task,
    ValidationError,
    TaskNotFoundError,
)
from .ui import (
    get_task_title,
    get_task_description,
    get_task_id,
    get_optional_update,
    get_confirmation,
    display_success,
    display_task_list,
    display_menu,
    get_menu_choice,
    display_error,
)
from .banner import display_banner  # T017


def handle_add_task(storage: TaskStorage) -> None:
    """Handle the 'Add Task' workflow.

    This function orchestrates the complete add task flow:
    1. Get title from user
    2. Get description from user
    3. Create task via operations layer (with validation)
    4. Display success message

    Args:
        storage: The storage instance to use

    Raises:
        ValidationError: If user input fails validation
    """
    # Get inputs from user
    title = get_task_title()
    description = get_task_description()

    # Create task (validates and stores)
    task = create_task(storage, title, description)

    # Display success
    display_success(f"Task #{task.id} '{task.title}' created successfully")


def handle_view_tasks(storage: TaskStorage) -> None:
    """Handle the 'View Tasks' workflow.

    This function orchestrates the view tasks flow:
    1. Retrieve all tasks from storage via operations layer
    2. Display tasks in formatted table (or empty message)

    Args:
        storage: The storage instance to use
    """
    # Get all tasks from storage
    tasks = list_tasks(storage)

    # Display tasks (handles empty list internally)
    display_task_list(tasks)


def handle_mark_complete(storage: TaskStorage) -> None:
    """Handle the 'Mark as Complete' workflow.

    This function orchestrates the mark complete flow:
    1. Get task ID from user
    2. Toggle completion status via operations layer
    3. Display appropriate success message based on new status

    Args:
        storage: The storage instance to use

    Raises:
        TaskNotFoundError: If the task ID does not exist
    """
    # Get task ID from user
    task_id = get_task_id()

    # Get current task to determine new status message
    task = storage.get(task_id)
    if task is None:
        # Will raise TaskNotFoundError in toggle_task_complete
        toggle_task_complete(storage, task_id)
        return

    # Toggle status
    toggle_task_complete(storage, task_id)

    # Display appropriate message based on NEW status
    new_status = "complete" if task.completed else "incomplete"
    display_success(f"Task #{task_id} marked as {new_status}")


def handle_update_task(storage: TaskStorage) -> None:
    """Handle the 'Update Task' workflow.

    This function orchestrates the update task flow:
    1. Get task ID from user
    2. Get current task to show current values
    3. Prompt for new title (optional - press Enter to keep current)
    4. Prompt for new description (optional - press Enter to keep current)
    5. Update task via operations layer (with validation)
    6. Display success message

    Args:
        storage: The storage instance to use

    Raises:
        TaskNotFoundError: If the task ID does not exist
        ValidationError: If new values fail validation
    """
    # Get task ID from user
    task_id = get_task_id()

    # Get current task to show current values
    task = storage.get(task_id)
    if task is None:
        # Will raise TaskNotFoundError in update_task
        update_task(storage, task_id, title="placeholder")
        return

    # Get optional updates (None means keep current)
    new_title = get_optional_update("Enter new title", task.title)
    new_description = get_optional_update("Enter new description", task.description)

    # Update task (validates and stores)
    update_task(storage, task_id, new_title, new_description)

    # Display success
    display_success(f"Task #{task_id} updated successfully")


def handle_delete_task(storage: TaskStorage) -> None:
    """Handle the 'Delete Task' workflow.

    This function orchestrates the delete task flow:
    1. Get task ID from user
    2. Request confirmation
    3. Delete task if confirmed
    4. Display success message

    Args:
        storage: The storage instance to use

    Raises:
        TaskNotFoundError: If the task ID does not exist
    """
    # Get task ID from user
    task_id = get_task_id()

    # Request confirmation
    confirmed = get_confirmation("Are you sure you want to delete this task?")

    if not confirmed:
        display_success("Delete cancelled")
        return

    # Delete task
    delete_task(storage, task_id)

    # Display success
    display_success(f"Task #{task_id} deleted successfully")


def main() -> None:
    """Main application entry point with menu loop and exception handling.

    This function:
    1. Creates storage instance
    2. Displays menu and gets user choice in a loop
    3. Dispatches to appropriate handler based on choice
    4. Handles exceptions globally (ValidationError, TaskNotFoundError, ValueError, KeyboardInterrupt)
    5. Exits gracefully on choice '6' or Ctrl+C
    """
    # Initialize storage
    storage = InMemoryStorage()

    # Display banner (T018)
    display_banner()

    # Blank line separator (T020)
    print()

    print("Welcome to Todo List Application!")
    print("=" * 40)

    # Main menu loop
    while True:
        try:
            # Display menu and get choice
            display_menu()
            choice = get_menu_choice()

            # Dispatch based on choice
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
