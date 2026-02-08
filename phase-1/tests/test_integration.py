"""Integration tests for complete workflows."""

import pytest
from io import StringIO
from unittest.mock import patch
from src.todo_app.storage import InMemoryStorage
from src.todo_app.main import (
    handle_add_task,
    handle_view_tasks,
    handle_mark_complete,
    handle_update_task,
)
from src.todo_app.operations import ValidationError, create_task, TaskNotFoundError


class TestAddTaskWorkflow:
    """Integration tests for the 'Add Task' workflow (US1)."""

    @patch('builtins.input', side_effect=['Buy groceries', 'Get milk and bread', ''])
    @patch('sys.stdout', new_callable=StringIO)
    def test_add_task_complete_workflow(self, mock_stdout, mock_input):
        """Test full add task workflow from input to confirmation."""
        storage = InMemoryStorage()

        handle_add_task(storage)

        # Verify success message displayed
        output = mock_stdout.getvalue()
        assert "✓ Task #1 'Buy groceries' created successfully" in output

        # Verify task was stored correctly
        tasks = storage.get_all()
        assert len(tasks) == 1
        assert tasks[0].id == 1
        assert tasks[0].title == "Buy groceries"
        assert tasks[0].description == "Get milk and bread"
        assert tasks[0].completed is False

    @patch('builtins.input', side_effect=['Call dentist', '', ''])
    @patch('sys.stdout', new_callable=StringIO)
    def test_add_task_without_description(self, mock_stdout, mock_input):
        """Test add task with empty description."""
        storage = InMemoryStorage()

        handle_add_task(storage)

        # Verify task was created with empty description
        tasks = storage.get_all()
        assert len(tasks) == 1
        assert tasks[0].title == "Call dentist"
        assert tasks[0].description == ""

    @patch('builtins.input', side_effect=['  Spaced title  ', 'desc', ''])
    @patch('sys.stdout', new_callable=StringIO)
    def test_add_task_strips_whitespace(self, mock_stdout, mock_input):
        """Test that title whitespace is stripped during creation."""
        storage = InMemoryStorage()

        handle_add_task(storage)

        tasks = storage.get_all()
        assert tasks[0].title == "Spaced title"  # Whitespace stripped

    @patch('builtins.input', side_effect=['', 'desc'])
    def test_add_task_with_empty_title_raises_error(self, mock_input):
        """Test that empty title raises ValidationError."""
        storage = InMemoryStorage()

        with pytest.raises(ValidationError, match="Title cannot be empty"):
            handle_add_task(storage)

    @patch('builtins.input', side_effect=['x' * 201, 'desc'])
    def test_add_task_with_too_long_title_raises_error(self, mock_input):
        """Test that title over 200 chars raises ValidationError."""
        storage = InMemoryStorage()

        with pytest.raises(
            ValidationError, match="Title must be between 1-200 characters"
        ):
            handle_add_task(storage)


class TestViewTasksWorkflow:
    """Integration tests for the 'View Tasks' workflow (US2)."""

    @patch('builtins.input', return_value='')
    @patch('sys.stdout', new_callable=StringIO)
    def test_view_tasks_empty_list(self, mock_stdout, mock_input):
        """Test viewing empty task list displays helpful message."""
        storage = InMemoryStorage()

        handle_view_tasks(storage)

        output = mock_stdout.getvalue()
        assert "No tasks found. Create your first task to get started!" in output
        mock_input.assert_called_once_with("Press Enter to continue...")

    @patch('builtins.input', return_value='')
    @patch('sys.stdout', new_callable=StringIO)
    def test_view_tasks_with_tasks(self, mock_stdout, mock_input):
        """Test viewing task list displays formatted table."""
        storage = InMemoryStorage()

        # Create some tasks
        task1 = create_task(storage, "Buy groceries", "Get milk and bread")
        task2 = create_task(storage, "Call dentist", "")

        handle_view_tasks(storage)

        output = mock_stdout.getvalue()

        # Verify table headers
        assert "ID" in output
        assert "Status" in output
        assert "Title" in output
        assert "Created" in output

        # Verify task data
        assert "Buy groceries" in output
        assert "Call dentist" in output

        mock_input.assert_called_once_with("Press Enter to continue...")


class TestMarkCompleteWorkflow:
    """Integration tests for the 'Mark as Complete' workflow (US3)."""

    @patch('builtins.input', side_effect=['1', ''])
    @patch('sys.stdout', new_callable=StringIO)
    def test_mark_complete_workflow(self, mock_stdout, mock_input):
        """Test marking a task as complete from incomplete status."""
        storage = InMemoryStorage()

        # Create a task
        task = create_task(storage, "Buy groceries", "Get milk")
        assert task.completed is False

        handle_mark_complete(storage)

        # Verify success message
        output = mock_stdout.getvalue()
        assert "Task #1 marked as complete" in output

        # Verify task status changed
        updated_task = storage.get(task.id)
        assert updated_task.completed is True

    @patch('builtins.input', side_effect=['1', ''])
    @patch('sys.stdout', new_callable=StringIO)
    def test_mark_complete_toggle_back_to_incomplete(self, mock_stdout, mock_input):
        """Test toggling already-complete task back to incomplete."""
        storage = InMemoryStorage()

        # Create and complete a task
        task = create_task(storage, "Buy groceries", "")
        storage.toggle_complete(task.id)
        assert task.completed is True

        handle_mark_complete(storage)

        # Verify success message
        output = mock_stdout.getvalue()
        assert "Task #1 marked as incomplete" in output

        # Verify task toggled back
        updated_task = storage.get(task.id)
        assert updated_task.completed is False

    @patch('builtins.input', return_value='999')
    def test_mark_complete_nonexistent_task(self, mock_input):
        """Test marking non-existent task raises TaskNotFoundError."""
        storage = InMemoryStorage()
        create_task(storage, "Task 1", "")

        with pytest.raises(TaskNotFoundError, match="Task with ID 999 not found"):
            handle_mark_complete(storage)


class TestUpdateTaskWorkflow:
    """Integration tests for the 'Update Task' workflow (US4)."""

    @patch('builtins.input', side_effect=['1', 'Updated Title', '', ''])
    @patch('sys.stdout', new_callable=StringIO)
    def test_update_task_title_only(self, mock_stdout, mock_input):
        """Test updating only the title of a task."""
        storage = InMemoryStorage()

        # Create a task
        task = create_task(storage, "Original Title", "Original Description")

        handle_update_task(storage)

        # Verify success message
        output = mock_stdout.getvalue()
        assert "Task #1 updated successfully" in output

        # Verify only title changed
        updated_task = storage.get(task.id)
        assert updated_task.title == "Updated Title"
        assert updated_task.description == "Original Description"

    @patch('builtins.input', side_effect=['1', '', 'Updated Description', ''])
    @patch('sys.stdout', new_callable=StringIO)
    def test_update_task_description_only(self, mock_stdout, mock_input):
        """Test updating only the description of a task."""
        storage = InMemoryStorage()

        # Create a task
        task = create_task(storage, "Original Title", "Original Description")

        handle_update_task(storage)

        # Verify success message
        output = mock_stdout.getvalue()
        assert "Task #1 updated successfully" in output

        # Verify only description changed
        updated_task = storage.get(task.id)
        assert updated_task.title == "Original Title"
        assert updated_task.description == "Updated Description"

    @patch('builtins.input', side_effect=['1', 'New Title', 'New Description', ''])
    @patch('sys.stdout', new_callable=StringIO)
    def test_update_task_both_fields(self, mock_stdout, mock_input):
        """Test updating both title and description."""
        storage = InMemoryStorage()

        # Create a task
        task = create_task(storage, "Original Title", "Original Description")

        handle_update_task(storage)

        # Verify both fields updated
        updated_task = storage.get(task.id)
        assert updated_task.title == "New Title"
        assert updated_task.description == "New Description"

    @patch('builtins.input', return_value='999')
    def test_update_nonexistent_task(self, mock_input):
        """Test updating non-existent task raises TaskNotFoundError."""
        storage = InMemoryStorage()
        create_task(storage, "Task 1", "")

        with pytest.raises(TaskNotFoundError, match="Task with ID 999 not found"):
            handle_update_task(storage)
