"""Tests for storage layer (TaskStorage and InMemoryStorage)."""

import pytest
from src.todo_app.models import Task
from src.todo_app.storage import TaskStorage, InMemoryStorage
from src.todo_app.operations import TaskNotFoundError


class TestInMemoryStorage:
    """Tests for InMemoryStorage.add method - ID assignment and increment."""

    def test_add_assigns_id_and_increments(self):
        """Test that storage assigns sequential IDs starting from 1."""
        storage = InMemoryStorage()

        # Add first task - should get ID 1
        task1 = storage.add(title="First Task", description="First description")
        assert task1.id == 1
        assert task1.title == "First Task"
        assert task1.description == "First description"
        assert task1.completed is False

        # Add second task - should get ID 2
        task2 = storage.add(title="Second Task")
        assert task2.id == 2
        assert task2.title == "Second Task"
        assert task2.description == ""  # Default empty description

    def test_add_non_reuse_of_deleted_ids(self):
        """Test that deleted IDs are never reused."""
        storage = InMemoryStorage()

        # Add and delete first task (ID 1)
        task1 = storage.add(title="Task to delete")
        assert task1.id == 1
        storage.delete(task1.id)

        # Add second task - should get ID 2, not reuse ID 1
        task2 = storage.add(title="New Task after deletion")
        assert task2.id == 2  # Should not reuse deleted ID 1


class TestInMemoryStorageGetAll:
    """Tests for InMemoryStorage.get_all method - retrieving all tasks."""

    def test_get_all_returns_empty_list_when_no_tasks(self):
        """Test that get_all returns empty list for new storage."""
        storage = InMemoryStorage()
        result = storage.get_all()
        assert result == []
        assert isinstance(result, list)

    def test_get_all_returns_all_tasks_sorted_by_id(self):
        """Test that get_all returns all tasks sorted by ID ascending."""
        storage = InMemoryStorage()

        # Add tasks in order
        task1 = storage.add(title="Task 1", description="First")
        task2 = storage.add(title="Task 2", description="Second")
        task3 = storage.add(title="Task 3", description="Third")

        result = storage.get_all()

        assert len(result) == 3
        assert result[0].id == 1
        assert result[0].title == "Task 1"
        assert result[1].id == 2
        assert result[1].title == "Task 2"
        assert result[2].id == 3
        assert result[2].title == "Task 3"

    def test_get_all_excludes_deleted_tasks(self):
        """Test that get_all does not return deleted tasks."""
        storage = InMemoryStorage()

        # Add three tasks
        task1 = storage.add(title="Task 1")
        task2 = storage.add(title="Task 2")
        task3 = storage.add(title="Task 3")

        # Delete middle task
        storage.delete(task2.id)

        result = storage.get_all()

        assert len(result) == 2
        assert result[0].id == 1
        assert result[1].id == 3  # Task 2 should be excluded


class TestInMemoryStorageToggleComplete:
    """Tests for InMemoryStorage.toggle_complete method - changing completion status."""

    def test_toggle_complete_from_incomplete_to_complete(self):
        """Test toggling task from incomplete (False) to complete (True)."""
        storage = InMemoryStorage()
        task = storage.add(title="Task 1")

        assert task.completed is False  # Initially incomplete

        result = storage.toggle_complete(task.id)

        assert result is True  # Operation succeeded
        assert task.completed is True  # Task is now complete

    def test_toggle_complete_from_complete_to_incomplete(self):
        """Test toggling task from complete (True) back to incomplete (False)."""
        storage = InMemoryStorage()
        task = storage.add(title="Task 1")

        # First toggle to complete
        storage.toggle_complete(task.id)
        assert task.completed is True

        # Second toggle back to incomplete
        result = storage.toggle_complete(task.id)

        assert result is True  # Operation succeeded
        assert task.completed is False  # Task is incomplete again

    def test_toggle_complete_nonexistent_id_returns_false(self):
        """Test that toggling non-existent task ID returns False."""
        storage = InMemoryStorage()
        storage.add(title="Task 1")

        result = storage.toggle_complete(999)  # ID that doesn't exist

        assert result is False  # Operation failed


class TestInMemoryStorageUpdate:
    """Tests for InMemoryStorage.update method - modifying task details."""

    def test_update_title_only(self):
        """Test updating only the title of a task."""
        storage = InMemoryStorage()
        task = storage.add(title="Original Title", description="Original Description")

        result = storage.update(task.id, title="Updated Title")

        assert result is True
        updated_task = storage.get(task.id)
        assert updated_task.title == "Updated Title"
        assert updated_task.description == "Original Description"  # Unchanged

    def test_update_description_only(self):
        """Test updating only the description of a task."""
        storage = InMemoryStorage()
        task = storage.add(title="Original Title", description="Original Description")

        result = storage.update(task.id, description="Updated Description")

        assert result is True
        updated_task = storage.get(task.id)
        assert updated_task.title == "Original Title"  # Unchanged
        assert updated_task.description == "Updated Description"

    def test_update_both_title_and_description(self):
        """Test updating both title and description simultaneously."""
        storage = InMemoryStorage()
        task = storage.add(title="Original Title", description="Original Description")

        result = storage.update(task.id, title="New Title", description="New Description")

        assert result is True
        updated_task = storage.get(task.id)
        assert updated_task.title == "New Title"
        assert updated_task.description == "New Description"

    def test_update_nonexistent_id_returns_false(self):
        """Test that updating non-existent task ID returns False."""
        storage = InMemoryStorage()
        storage.add(title="Task 1")

        result = storage.update(999, title="New Title")

        assert result is False


class TestInMemoryStorageDelete:
    """Tests for InMemoryStorage.delete method - removing tasks."""

    def test_delete_existing_task(self):
        """Test deleting an existing task."""
        storage = InMemoryStorage()
        task = storage.add(title="Task to delete")

        result = storage.delete(task.id)

        assert result is True
        assert storage.get(task.id) is None  # Task no longer exists

    def test_delete_nonexistent_id_returns_false(self):
        """Test that deleting non-existent task ID returns False."""
        storage = InMemoryStorage()
        storage.add(title="Task 1")

        result = storage.delete(999)

        assert result is False

    def test_delete_removes_from_get_all(self):
        """Test that deleted tasks don't appear in get_all()."""
        storage = InMemoryStorage()
        task1 = storage.add(title="Task 1")
        task2 = storage.add(title="Task 2")
        task3 = storage.add(title="Task 3")

        storage.delete(task2.id)

        all_tasks = storage.get_all()
        assert len(all_tasks) == 2
        assert task1 in all_tasks
        assert task3 in all_tasks
        assert task2 not in all_tasks
