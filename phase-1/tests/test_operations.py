"""Tests for business logic operations layer."""

import pytest
from src.todo_app.models import Task
from src.todo_app.storage import InMemoryStorage
from src.todo_app.operations import (
    ValidationError,
    TaskNotFoundError,
    validate_title,
    validate_description,
    create_task,
    list_tasks,
    toggle_task_complete,
    update_task,
)


class TestValidateTitle:
    """Tests for title validation function."""

    def test_validate_title_accepts_valid_input(self):
        """Test that valid titles are accepted and returned stripped."""
        assert validate_title("Buy groceries") == "Buy groceries"
        assert validate_title("  Spaced title  ") == "Spaced title"
        assert validate_title("x" * 200) == "x" * 200  # Boundary: exactly 200 chars

    def test_validate_title_rejects_empty_string(self):
        """Test that empty strings are rejected."""
        with pytest.raises(ValidationError, match="Title cannot be empty"):
            validate_title("")

    def test_validate_title_rejects_whitespace_only(self):
        """Test that whitespace-only strings are rejected (title.strip() == "")."""
        with pytest.raises(ValidationError, match="Title cannot be empty"):
            validate_title("   ")
        with pytest.raises(ValidationError, match="Title cannot be empty"):
            validate_title("\t\n")

    def test_validate_title_rejects_too_long(self):
        """Test that titles over 200 characters are rejected."""
        with pytest.raises(
            ValidationError, match="Title must be between 1-200 characters"
        ):
            validate_title("x" * 201)


class TestValidateDescription:
    """Tests for description validation function."""

    def test_validate_description_accepts_valid_input(self):
        """Test that valid descriptions are accepted."""
        assert validate_description("A task description") == "A task description"
        assert validate_description("") == ""  # Empty is valid
        assert validate_description("x" * 1000) == "x" * 1000  # Boundary: exactly 1000

    def test_validate_description_rejects_too_long(self):
        """Test that descriptions over 1000 characters are rejected."""
        with pytest.raises(
            ValidationError, match="Description cannot exceed 1000 characters"
        ):
            validate_description("x" * 1001)


class TestCreateTask:
    """Tests for create_task business logic function."""

    def test_create_task_with_valid_inputs(self):
        """Test task creation with valid title and description."""
        storage = InMemoryStorage()
        task = create_task(storage, "Buy groceries", "Get milk and bread")

        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description == "Get milk and bread"
        assert task.completed is False
        assert task.created_at is not None

    def test_create_task_with_empty_description(self):
        """Test task creation with no description (default empty string)."""
        storage = InMemoryStorage()
        task = create_task(storage, "Call dentist", "")

        assert task.id == 1
        assert task.title == "Call dentist"
        assert task.description == ""

    def test_create_task_strips_whitespace_from_title(self):
        """Test that title whitespace is stripped during validation."""
        storage = InMemoryStorage()
        task = create_task(storage, "  Spaced title  ", "desc")

        assert task.title == "Spaced title"

    def test_create_task_rejects_invalid_title(self):
        """Test that invalid titles raise ValidationError."""
        storage = InMemoryStorage()

        with pytest.raises(ValidationError, match="Title cannot be empty"):
            create_task(storage, "", "desc")

        with pytest.raises(ValidationError, match="Title cannot be empty"):
            create_task(storage, "   ", "desc")

        with pytest.raises(
            ValidationError, match="Title must be between 1-200 characters"
        ):
            create_task(storage, "x" * 201, "desc")

    def test_create_task_rejects_invalid_description(self):
        """Test that invalid descriptions raise ValidationError."""
        storage = InMemoryStorage()

        with pytest.raises(
            ValidationError, match="Description cannot exceed 1000 characters"
        ):
            create_task(storage, "Valid title", "x" * 1001)

    def test_create_task_increments_ids(self):
        """Test that multiple tasks get sequential IDs."""
        storage = InMemoryStorage()

        task1 = create_task(storage, "Task 1", "")
        task2 = create_task(storage, "Task 2", "")
        task3 = create_task(storage, "Task 3", "")

        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3


class TestInvalidIDFormats:
    """Tests for invalid ID format handling (negative, zero, non-numeric)."""

    def test_negative_id_handling(self):
        """Test that negative IDs are handled as invalid (future operations)."""
        # This will be tested in toggle_task_complete, update_task, delete_task
        # For now, we verify storage doesn't accept negative IDs in get()
        storage = InMemoryStorage()
        storage.add("Task 1", "")

        result = storage.get(-1)
        assert result is None  # Negative ID returns None (not found)

    def test_zero_id_handling(self):
        """Test that ID=0 is handled as invalid."""
        storage = InMemoryStorage()
        storage.add("Task 1", "")

        result = storage.get(0)
        assert result is None  # ID 0 returns None (IDs start at 1)

    def test_non_numeric_id_returns_none(self):
        """Test that non-numeric IDs are handled gracefully (dict.get behavior)."""
        storage = InMemoryStorage()
        storage.add("Task 1", "")

        # Python dicts allow any hashable key, so this returns None (not found)
        # Type hints prevent this at development time with mypy
        result = storage.get("abc")  # type: ignore
        assert result is None  # Non-numeric ID returns None (type mismatch)


class TestListTasks:
    """Tests for list_tasks business logic function."""

    def test_list_tasks_returns_empty_list_when_no_tasks(self):
        """Test that list_tasks returns empty list when storage has no tasks."""
        storage = InMemoryStorage()
        result = list_tasks(storage)

        assert result == []
        assert isinstance(result, list)

    def test_list_tasks_returns_all_tasks_sorted_by_id(self):
        """Test that list_tasks returns all tasks sorted by ID ascending."""
        storage = InMemoryStorage()

        # Create tasks via operations layer
        task1 = create_task(storage, "Task 1", "First")
        task2 = create_task(storage, "Task 2", "Second")
        task3 = create_task(storage, "Task 3", "Third")

        result = list_tasks(storage)

        assert len(result) == 3
        assert result[0].id == task1.id
        assert result[0].title == "Task 1"
        assert result[1].id == task2.id
        assert result[1].title == "Task 2"
        assert result[2].id == task3.id
        assert result[2].title == "Task 3"

    def test_list_tasks_excludes_deleted_tasks(self):
        """Test that list_tasks only returns existing tasks (deleted ones excluded)."""
        storage = InMemoryStorage()

        # Create three tasks
        task1 = create_task(storage, "Task 1", "")
        task2 = create_task(storage, "Task 2", "")
        task3 = create_task(storage, "Task 3", "")

        # Delete middle task
        storage.delete(task2.id)

        result = list_tasks(storage)

        assert len(result) == 2
        assert result[0].id == task1.id
        assert result[1].id == task3.id


class TestToggleTaskComplete:
    """Tests for toggle_task_complete business logic function."""

    def test_toggle_task_complete_from_incomplete_to_complete(self):
        """Test toggling task from incomplete to complete."""
        storage = InMemoryStorage()
        task = create_task(storage, "Task 1", "")

        assert task.completed is False  # Initially incomplete

        toggle_task_complete(storage, task.id)

        # Verify status changed
        updated_task = storage.get(task.id)
        assert updated_task.completed is True

    def test_toggle_task_complete_from_complete_to_incomplete(self):
        """Test toggling task from complete back to incomplete."""
        storage = InMemoryStorage()
        task = create_task(storage, "Task 1", "")

        # First toggle to complete
        toggle_task_complete(storage, task.id)
        assert storage.get(task.id).completed is True

        # Second toggle back to incomplete
        toggle_task_complete(storage, task.id)

        updated_task = storage.get(task.id)
        assert updated_task.completed is False

    def test_toggle_task_complete_nonexistent_id_raises_error(self):
        """Test that toggling non-existent task raises TaskNotFoundError."""
        storage = InMemoryStorage()
        create_task(storage, "Task 1", "")

        with pytest.raises(TaskNotFoundError, match="Task with ID 999 not found"):
            toggle_task_complete(storage, 999)


class TestUpdateTask:
    """Tests for update_task business logic function."""

    def test_update_task_title_only(self):
        """Test updating only the title with validation."""
        storage = InMemoryStorage()
        task = create_task(storage, "Original Title", "Original Description")

        update_task(storage, task.id, title="Updated Title")

        updated_task = storage.get(task.id)
        assert updated_task.title == "Updated Title"
        assert updated_task.description == "Original Description"

    def test_update_task_description_only(self):
        """Test updating only the description."""
        storage = InMemoryStorage()
        task = create_task(storage, "Original Title", "Original Description")

        update_task(storage, task.id, description="Updated Description")

        updated_task = storage.get(task.id)
        assert updated_task.title == "Original Title"
        assert updated_task.description == "Updated Description"

    def test_update_task_both_fields(self):
        """Test updating both title and description."""
        storage = InMemoryStorage()
        task = create_task(storage, "Original Title", "Original Description")

        update_task(storage, task.id, title="New Title", description="New Description")

        updated_task = storage.get(task.id)
        assert updated_task.title == "New Title"
        assert updated_task.description == "New Description"

    def test_update_task_validates_new_title(self):
        """Test that update validates new title (rejects empty/too long)."""
        storage = InMemoryStorage()
        task = create_task(storage, "Original Title", "")

        # Empty title
        with pytest.raises(ValidationError, match="Title cannot be empty"):
            update_task(storage, task.id, title="")

        # Whitespace-only title
        with pytest.raises(ValidationError, match="Title cannot be empty"):
            update_task(storage, task.id, title="   ")

        # Too long title
        with pytest.raises(
            ValidationError, match="Title must be between 1-200 characters"
        ):
            update_task(storage, task.id, title="x" * 201)

    def test_update_task_validates_new_description(self):
        """Test that update validates new description (rejects too long)."""
        storage = InMemoryStorage()
        task = create_task(storage, "Original Title", "")

        with pytest.raises(
            ValidationError, match="Description cannot exceed 1000 characters"
        ):
            update_task(storage, task.id, description="x" * 1001)

    def test_update_task_nonexistent_id_raises_error(self):
        """Test that updating non-existent task raises TaskNotFoundError."""
        storage = InMemoryStorage()
        create_task(storage, "Task 1", "")

        with pytest.raises(TaskNotFoundError, match="Task with ID 999 not found"):
            update_task(storage, 999, title="New Title")
