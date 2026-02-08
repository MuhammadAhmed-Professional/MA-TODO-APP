"""Tests for UI layer functions."""

import pytest
from io import StringIO
from unittest.mock import patch
from datetime import datetime
from src.todo_app.models import Task
from src.todo_app.ui import (
    get_task_title,
    get_task_description,
    display_success,
    format_timestamp,
    format_status,
    display_task_list,
    get_task_id,
    get_optional_update,
)


class TestUIInputs:
    """Tests for UI input functions."""

    @patch('builtins.input', return_value='Buy groceries')
    def test_get_task_title(self, mock_input):
        """Test getting task title from user."""
        result = get_task_title()

        assert result == 'Buy groceries'
        mock_input.assert_called_once_with("Enter task title: ")

    @patch('builtins.input', return_value='Get milk and bread')
    def test_get_task_description(self, mock_input):
        """Test getting task description from user."""
        result = get_task_description()

        assert result == 'Get milk and bread'
        mock_input.assert_called_once_with("Enter task description (optional): ")

    @patch('builtins.input', return_value='42')
    def test_get_task_id_valid_integer(self, mock_input):
        """Test getting valid task ID from user."""
        result = get_task_id()

        assert result == 42
        mock_input.assert_called_once_with("Enter task ID: ")

    @patch('builtins.input', return_value='1')
    def test_get_task_id_single_digit(self, mock_input):
        """Test getting single-digit task ID."""
        result = get_task_id()

        assert result == 1
        assert isinstance(result, int)

    @patch('builtins.input', return_value='')
    def test_get_optional_update_empty_returns_none(self, mock_input):
        """Test that pressing Enter (empty input) returns None to keep current value."""
        result = get_optional_update("Enter new title", "Current Title")

        assert result is None
        mock_input.assert_called_once_with("Enter new title (current: 'Current Title', press Enter to keep): ")

    @patch('builtins.input', return_value='New Value')
    def test_get_optional_update_with_new_value(self, mock_input):
        """Test that entering new value returns the new value."""
        result = get_optional_update("Enter new title", "Old Title")

        assert result == "New Value"


class TestUIOutputs:
    """Tests for UI output functions."""

    @patch('builtins.input', return_value='')
    @patch('sys.stdout', new_callable=StringIO)
    def test_display_success(self, mock_stdout, mock_input):
        """Test success message display and wait for Enter."""
        display_success("Task #1 'Buy groceries' created successfully")

        output = mock_stdout.getvalue()
        assert "✓ Task #1 'Buy groceries' created successfully" in output
        mock_input.assert_called_once_with("Press Enter to continue...")


class TestFormatting:
    """Tests for formatting functions."""

    def test_format_timestamp_with_sample_datetime(self):
        """Test timestamp formatting as YYYY-MM-DD HH:MM."""
        dt = datetime(2025, 12, 4, 14, 30, 45)  # Includes seconds
        result = format_timestamp(dt)
        assert result == "2025-12-04 14:30"  # No seconds

    def test_format_timestamp_with_single_digit_month_day_time(self):
        """Test timestamp formatting with single-digit values (padding)."""
        dt = datetime(2025, 1, 5, 9, 7, 0)
        result = format_timestamp(dt)
        assert result == "2025-01-05 09:07"  # Zero-padded

    def test_format_status_completed_true(self):
        """Test status formatting for completed tasks."""
        result = format_status(True)
        assert result == "✓"

    def test_format_status_completed_false(self):
        """Test status formatting for incomplete tasks."""
        result = format_status(False)
        assert result == " "  # Single space


class TestDisplayTaskList:
    """Tests for display_task_list function."""

    @patch('builtins.input', return_value='')
    @patch('sys.stdout', new_callable=StringIO)
    def test_display_task_list_empty_shows_message(self, mock_stdout, mock_input):
        """Test that empty task list displays helpful message."""
        display_task_list([])

        output = mock_stdout.getvalue()
        assert "No tasks found. Create your first task to get started!" in output
        mock_input.assert_called_once_with("Press Enter to continue...")

    @patch('builtins.input', return_value='')
    @patch('sys.stdout', new_callable=StringIO)
    def test_display_task_list_with_tasks(self, mock_stdout, mock_input):
        """Test displaying task list as formatted table."""
        tasks = [
            Task(
                id=1,
                title="Buy groceries",
                description="Get milk and bread",
                completed=False,
                created_at=datetime(2025, 12, 4, 14, 30, 0),
            ),
            Task(
                id=2,
                title="Call dentist",
                description="",
                completed=True,
                created_at=datetime(2025, 12, 4, 15, 45, 0),
            ),
        ]

        display_task_list(tasks)

        output = mock_stdout.getvalue()

        # Verify table headers present
        assert "ID" in output
        assert "Status" in output
        assert "Title" in output
        assert "Created" in output

        # Verify task data present
        assert "1" in output
        assert "Buy groceries" in output
        assert "2025-12-04 14:30" in output

        assert "2" in output
        assert "Call dentist" in output
        assert "2025-12-04 15:45" in output
        assert "✓" in output  # Completed status

        mock_input.assert_called_once_with("Press Enter to continue...")
