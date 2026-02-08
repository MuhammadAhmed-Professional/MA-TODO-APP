"""
Unit Tests for Task Service (T061)

Tests task CRUD operations in the TaskService layer with mocked database.
Tests business logic, ownership validation, edge cases, and error handling.
"""

import uuid
from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException

from src.models.task import Task, TaskCreate, TaskUpdate
from src.services.task_service import TaskService


@pytest.fixture
def mock_session():
    """
    Mock database session for isolated unit tests.

    Returns:
        Mock object simulating SQLModel Session
    """
    return Mock()


@pytest.fixture
def task_service(mock_session):
    """
    TaskService instance with mocked database session.

    Args:
        mock_session: Mocked database session

    Returns:
        TaskService instance for testing
    """
    return TaskService(session=mock_session)


@pytest.fixture
def sample_user_id():
    """Sample user ID for testing"""
    return uuid.uuid4()


@pytest.fixture
def sample_task_data():
    """Sample task creation data"""
    return TaskCreate(
        title="Complete project documentation",
        description="Write comprehensive README and API docs"
    )


@pytest.fixture
def sample_task(sample_user_id):
    """Sample Task object for testing"""
    return Task(
        id=uuid.uuid4(),
        title="Complete project documentation",
        description="Write comprehensive README and API docs",
        is_complete=False,
        user_id=sample_user_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


class TestCreateTask:
    """Test TaskService.create_task method"""

    @pytest.mark.asyncio
    async def test_create_task_success(
        self,
        task_service,
        mock_session,
        sample_task_data,
        sample_user_id
    ):
        """
        Test successful task creation with valid data.

        Verifies:
        - Task is created with correct attributes
        - Title and description are trimmed
        - Timestamps are set
        - Task is added to session and committed
        """
        # Act
        task = await task_service.create_task(sample_task_data, sample_user_id)

        # Assert
        assert task.title == "Complete project documentation"
        assert task.description == "Write comprehensive README and API docs"
        assert task.is_complete is False
        assert task.user_id == sample_user_id
        assert isinstance(task.id, uuid.UUID)
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)

        # Verify database operations
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_task_trims_whitespace(
        self,
        task_service,
        sample_user_id
    ):
        """
        Test that task creation trims leading/trailing whitespace.

        Verifies title and description are cleaned before saving.
        """
        # Arrange
        task_data = TaskCreate(
            title="  Task with spaces  ",
            description="  Description with spaces  "
        )

        # Act
        task = await task_service.create_task(task_data, sample_user_id)

        # Assert
        assert task.title == "Task with spaces"
        assert task.description == "Description with spaces"

    @pytest.mark.asyncio
    async def test_create_task_with_none_description(
        self,
        task_service,
        sample_user_id
    ):
        """
        Test task creation with no description (optional field).
        """
        # Arrange
        task_data = TaskCreate(title="Task without description", description=None)

        # Act
        task = await task_service.create_task(task_data, sample_user_id)

        # Assert
        assert task.title == "Task without description"
        assert task.description is None

    @pytest.mark.asyncio
    async def test_create_task_with_empty_description(
        self,
        task_service,
        sample_user_id
    ):
        """
        Test task creation with empty string description.

        Empty description should be converted to None.
        """
        # Arrange
        task_data = TaskCreate(title="Task", description="   ")

        # Act
        task = await task_service.create_task(task_data, sample_user_id)

        # Assert
        assert task.description is None

    @pytest.mark.asyncio
    async def test_create_task_raises_error_for_empty_title(
        self,
        task_service,
        sample_user_id
    ):
        """
        Test that task creation fails for empty title after trimming.

        Verifies ValueError is raised for whitespace-only titles.
        """
        # Arrange
        task_data = TaskCreate(title="   ", description="Valid description")

        # Act & Assert
        with pytest.raises(ValueError, match="Title cannot be empty or whitespace"):
            await task_service.create_task(task_data, sample_user_id)


class TestGetUserTasks:
    """Test TaskService.get_user_tasks method"""

    @pytest.mark.asyncio
    async def test_get_user_tasks_returns_only_owned_tasks(
        self,
        task_service,
        mock_session,
        sample_user_id
    ):
        """
        Test that get_user_tasks returns only tasks owned by the user.

        Verifies ownership filtering in database query.
        """
        # Arrange
        user1_id = sample_user_id
        user2_id = uuid.uuid4()

        user1_tasks = [
            Task(id=uuid.uuid4(), title="Task 1", user_id=user1_id, is_complete=False,
                 created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
            Task(id=uuid.uuid4(), title="Task 2", user_id=user1_id, is_complete=False,
                 created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
        ]

        # Mock query execution
        mock_query = Mock()
        mock_query.where.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.order_by.return_value = mock_query

        mock_result = Mock()
        mock_result.all.return_value = user1_tasks

        mock_session.exec.return_value = mock_result

        # Act
        with patch('src.services.task_service.select', return_value=mock_query):
            tasks = await task_service.get_user_tasks(user1_id)

        # Assert
        assert len(tasks) == 2
        assert all(task.user_id == user1_id for task in tasks)

    @pytest.mark.asyncio
    async def test_get_user_tasks_empty_list(
        self,
        task_service,
        mock_session,
        sample_user_id
    ):
        """
        Test that get_user_tasks returns empty list when no tasks exist.
        """
        # Arrange
        mock_query = Mock()
        mock_query.where.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.order_by.return_value = mock_query

        mock_result = Mock()
        mock_result.all.return_value = []

        mock_session.exec.return_value = mock_result

        # Act
        with patch('src.services.task_service.select', return_value=mock_query):
            tasks = await task_service.get_user_tasks(sample_user_id)

        # Assert
        assert tasks == []

    @pytest.mark.asyncio
    async def test_get_user_tasks_filters_by_completion_status(
        self,
        task_service,
        mock_session,
        sample_user_id
    ):
        """
        Test filtering tasks by completion status.

        Verifies is_complete filter is applied correctly.
        """
        # Arrange
        incomplete_tasks = [
            Task(id=uuid.uuid4(), title="Task 1", user_id=sample_user_id, is_complete=False,
                 created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
        ]

        mock_query = Mock()
        mock_query.where.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.order_by.return_value = mock_query

        mock_result = Mock()
        mock_result.all.return_value = incomplete_tasks

        mock_session.exec.return_value = mock_result

        # Act
        with patch('src.services.task_service.select', return_value=mock_query):
            tasks = await task_service.get_user_tasks(sample_user_id, is_complete=False)

        # Assert
        assert len(tasks) == 1
        assert tasks[0].is_complete is False

    @pytest.mark.asyncio
    async def test_get_user_tasks_respects_pagination(
        self,
        task_service,
        mock_session,
        sample_user_id
    ):
        """
        Test that pagination parameters (limit, offset) are applied.
        """
        # Arrange
        mock_query = Mock()
        mock_query.where.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.order_by.return_value = mock_query

        mock_result = Mock()
        mock_result.all.return_value = []

        mock_session.exec.return_value = mock_result

        # Act
        with patch('src.services.task_service.select', return_value=mock_query):
            await task_service.get_user_tasks(sample_user_id, limit=10, offset=20)

        # Assert
        mock_query.limit.assert_called_with(10)
        mock_query.offset.assert_called_with(20)


class TestGetTask:
    """Test TaskService.get_task method"""

    @pytest.mark.asyncio
    async def test_get_task_success(
        self,
        task_service,
        mock_session,
        sample_task,
        sample_user_id
    ):
        """
        Test successful retrieval of task with ownership verification.
        """
        # Arrange
        mock_session.get.return_value = sample_task

        # Act
        task = await task_service.get_task(sample_task.id, sample_user_id)

        # Assert
        assert task.id == sample_task.id
        assert task.user_id == sample_user_id
        mock_session.get.assert_called_once_with(Task, sample_task.id)

    @pytest.mark.asyncio
    async def test_get_task_not_found(
        self,
        task_service,
        mock_session,
        sample_user_id
    ):
        """
        Test get_task raises 404 HTTPException when task not found.
        """
        # Arrange
        task_id = uuid.uuid4()
        mock_session.get.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await task_service.get_task(task_id, sample_user_id)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Task not found"

    @pytest.mark.asyncio
    async def test_get_task_ownership_validation_fails(
        self,
        task_service,
        mock_session,
        sample_task
    ):
        """
        Test get_task raises 403 HTTPException when user doesn't own task.

        Verifies ownership check prevents accessing other users' tasks.
        """
        # Arrange
        different_user_id = uuid.uuid4()  # Different from sample_task.user_id
        mock_session.get.return_value = sample_task

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await task_service.get_task(sample_task.id, different_user_id)

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Not authorized to access this task"


class TestUpdateTask:
    """Test TaskService.update_task method"""

    @pytest.mark.asyncio
    async def test_update_task_success(
        self,
        task_service,
        mock_session,
        sample_task,
        sample_user_id
    ):
        """
        Test successful task update with valid data.

        Verifies:
        - Title and description are updated
        - Timestamps are updated
        - Changes are committed
        """
        # Arrange
        mock_session.get.return_value = sample_task
        update_data = TaskUpdate(
            title="Updated title",
            description="Updated description"
        )

        # Act
        updated_task = await task_service.update_task(
            sample_task.id,
            update_data,
            sample_user_id
        )

        # Assert
        assert updated_task.title == "Updated title"
        assert updated_task.description == "Updated description"
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_task_partial_update(
        self,
        task_service,
        mock_session,
        sample_task,
        sample_user_id
    ):
        """
        Test partial update (only title or only description).

        Verifies that None fields are not updated.
        """
        # Arrange
        original_title = sample_task.title
        original_description = sample_task.description
        mock_session.get.return_value = sample_task

        # Update only description
        update_data = TaskUpdate(title=None, description="New description only")

        # Act
        updated_task = await task_service.update_task(
            sample_task.id,
            update_data,
            sample_user_id
        )

        # Assert
        assert updated_task.title == original_title  # Title unchanged
        assert updated_task.description == "New description only"

    @pytest.mark.asyncio
    async def test_update_task_ownership_validation(
        self,
        task_service,
        mock_session,
        sample_task
    ):
        """
        Test that update fails when user doesn't own the task.

        Verifies ownership check before update.
        """
        # Arrange
        different_user_id = uuid.uuid4()
        mock_session.get.return_value = sample_task
        update_data = TaskUpdate(title="Hacked title")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await task_service.update_task(
                sample_task.id,
                update_data,
                different_user_id
            )

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_update_task_not_found(
        self,
        task_service,
        mock_session,
        sample_user_id
    ):
        """
        Test update_task raises 404 when task doesn't exist.
        """
        # Arrange
        task_id = uuid.uuid4()
        mock_session.get.return_value = None
        update_data = TaskUpdate(title="New title")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await task_service.update_task(task_id, update_data, sample_user_id)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_update_task_raises_error_for_empty_title(
        self,
        task_service,
        mock_session,
        sample_task,
        sample_user_id
    ):
        """
        Test that update fails when title is empty after trimming.
        """
        # Arrange
        mock_session.get.return_value = sample_task
        update_data = TaskUpdate(title="   ")  # Whitespace only

        # Act & Assert
        with pytest.raises(ValueError, match="Title cannot be empty"):
            await task_service.update_task(
                sample_task.id,
                update_data,
                sample_user_id
            )

    @pytest.mark.asyncio
    async def test_update_task_trims_whitespace(
        self,
        task_service,
        mock_session,
        sample_task,
        sample_user_id
    ):
        """
        Test that update trims whitespace from title and description.
        """
        # Arrange
        mock_session.get.return_value = sample_task
        update_data = TaskUpdate(
            title="  Trimmed title  ",
            description="  Trimmed description  "
        )

        # Act
        updated_task = await task_service.update_task(
            sample_task.id,
            update_data,
            sample_user_id
        )

        # Assert
        assert updated_task.title == "Trimmed title"
        assert updated_task.description == "Trimmed description"


class TestToggleComplete:
    """Test TaskService.toggle_complete method"""

    @pytest.mark.asyncio
    async def test_toggle_complete_updates_status(
        self,
        task_service,
        mock_session,
        sample_task,
        sample_user_id
    ):
        """
        Test toggling completion status from False to True.
        """
        # Arrange
        sample_task.is_complete = False
        mock_session.get.return_value = sample_task

        # Act
        updated_task = await task_service.toggle_complete(
            sample_task.id,
            True,
            sample_user_id
        )

        # Assert
        assert updated_task.is_complete is True
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_toggle_complete_idempotent(
        self,
        task_service,
        mock_session,
        sample_task,
        sample_user_id
    ):
        """
        Test multiple toggles work correctly (idempotent operation).

        Verifies toggling True -> False -> True works as expected.
        """
        # Arrange
        mock_session.get.return_value = sample_task

        # Act - Toggle to True
        task1 = await task_service.toggle_complete(sample_task.id, True, sample_user_id)
        assert task1.is_complete is True

        # Act - Toggle back to False
        task2 = await task_service.toggle_complete(sample_task.id, False, sample_user_id)
        assert task2.is_complete is False

        # Act - Toggle to True again
        task3 = await task_service.toggle_complete(sample_task.id, True, sample_user_id)
        assert task3.is_complete is True

    @pytest.mark.asyncio
    async def test_toggle_complete_ownership_check(
        self,
        task_service,
        mock_session,
        sample_task
    ):
        """
        Test that toggle fails when user doesn't own the task.
        """
        # Arrange
        different_user_id = uuid.uuid4()
        mock_session.get.return_value = sample_task

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await task_service.toggle_complete(
                sample_task.id,
                True,
                different_user_id
            )

        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_toggle_complete_not_found(
        self,
        task_service,
        mock_session,
        sample_user_id
    ):
        """
        Test toggle raises 404 when task doesn't exist.
        """
        # Arrange
        task_id = uuid.uuid4()
        mock_session.get.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await task_service.toggle_complete(task_id, True, sample_user_id)

        assert exc_info.value.status_code == 404


class TestDeleteTask:
    """Test TaskService.delete_task method"""

    @pytest.mark.asyncio
    async def test_delete_task_removes_from_db(
        self,
        task_service,
        mock_session,
        sample_task,
        sample_user_id
    ):
        """
        Test successful task deletion from database.

        Verifies:
        - Task is retrieved with ownership check
        - Task is deleted from session
        - Changes are committed
        """
        # Arrange
        mock_session.get.return_value = sample_task

        # Act
        await task_service.delete_task(sample_task.id, sample_user_id)

        # Assert
        mock_session.delete.assert_called_once_with(sample_task)
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_task_ownership_check(
        self,
        task_service,
        mock_session,
        sample_task
    ):
        """
        Test that delete fails when user doesn't own the task.

        Verifies ownership validation prevents deleting others' tasks.
        """
        # Arrange
        different_user_id = uuid.uuid4()
        mock_session.get.return_value = sample_task

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await task_service.delete_task(sample_task.id, different_user_id)

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Not authorized to access this task"

        # Verify delete was NOT called
        mock_session.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_delete_task_not_found(
        self,
        task_service,
        mock_session,
        sample_user_id
    ):
        """
        Test delete raises 404 when task doesn't exist.
        """
        # Arrange
        task_id = uuid.uuid4()
        mock_session.get.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await task_service.delete_task(task_id, sample_user_id)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Task not found"

        # Verify delete was NOT called
        mock_session.delete.assert_not_called()


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    @pytest.mark.asyncio
    async def test_create_task_with_max_length_title(
        self,
        task_service,
        sample_user_id
    ):
        """
        Test task creation with maximum allowed title length (200 chars).
        """
        # Arrange
        max_title = "a" * 200
        task_data = TaskCreate(title=max_title, description=None)

        # Act
        task = await task_service.create_task(task_data, sample_user_id)

        # Assert
        assert len(task.title) == 200

    @pytest.mark.asyncio
    async def test_create_task_with_max_length_description(
        self,
        task_service,
        sample_user_id
    ):
        """
        Test task creation with maximum allowed description length (2000 chars).
        """
        # Arrange
        max_description = "b" * 2000
        task_data = TaskCreate(title="Task", description=max_description)

        # Act
        task = await task_service.create_task(task_data, sample_user_id)

        # Assert
        assert len(task.description) == 2000

    @pytest.mark.asyncio
    async def test_get_user_tasks_with_zero_limit(
        self,
        task_service,
        mock_session,
        sample_user_id
    ):
        """
        Test pagination with zero limit (edge case).
        """
        # Arrange
        mock_query = Mock()
        mock_query.where.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.order_by.return_value = mock_query

        mock_result = Mock()
        mock_result.all.return_value = []

        mock_session.exec.return_value = mock_result

        # Act
        with patch('src.services.task_service.select', return_value=mock_query):
            tasks = await task_service.get_user_tasks(sample_user_id, limit=0)

        # Assert
        mock_query.limit.assert_called_with(0)

    @pytest.mark.asyncio
    async def test_update_task_with_empty_string_description(
        self,
        task_service,
        mock_session,
        sample_task,
        sample_user_id
    ):
        """
        Test updating description to empty string converts to None.
        """
        # Arrange
        mock_session.get.return_value = sample_task
        update_data = TaskUpdate(description="")

        # Act
        updated_task = await task_service.update_task(
            sample_task.id,
            update_data,
            sample_user_id
        )

        # Assert
        assert updated_task.description is None
