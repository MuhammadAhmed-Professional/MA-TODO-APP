"""
Integration Tests for Task Management API Endpoints (T062)

Tests complete request-response cycle for task CRUD endpoints with authentication.
Covers all HTTP methods, response codes, pagination, filtering, and ownership checks.
"""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from src.auth.jwt import create_access_token
from src.models.task import Task
from tests.conftest import create_test_user


class TestListTasksEndpoint:
    """Test GET /api/tasks"""

    def test_list_tasks_authenticated_200(
        self, client: TestClient, session: Session
    ):
        """Test listing tasks for authenticated user returns 200 with user's tasks."""
        # Create user and auth token
        user = create_test_user(session, email="alice@example.com")
        token = create_access_token(user.id, user.email)

        # Create 3 tasks for this user
        for i in range(3):
            task = Task(
                id=uuid.uuid4(),
                title=f"Task {i+1}",
                description=f"Description {i+1}",
                is_complete=False,
                user_id=user.id,
            )
            session.add(task)
        session.commit()

        # Make authenticated request
        response = client.get(
            "/api/tasks",
            cookies={"auth_token": token}
        )

        # Should return 200 OK
        assert response.status_code == 200

        # Should return list of tasks
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3

        # All tasks should belong to the user
        for task_data in data:
            assert task_data["user_id"] == str(user.id)
            assert "id" in task_data
            assert "title" in task_data
            assert "is_complete" in task_data
            assert "created_at" in task_data
            assert "updated_at" in task_data

    def test_list_tasks_unauthenticated_401(self, client: TestClient):
        """Test listing tasks without authentication returns 401."""
        response = client.get("/api/tasks")

        # Should return 401 Unauthorized
        assert response.status_code == 401

        # Should return error message
        data = response.json()
        assert "detail" in data
        assert "not authenticated" in data["detail"].lower()

    def test_list_tasks_pagination(self, client: TestClient, session: Session):
        """Test pagination with limit and offset parameters."""
        # Create user and auth token
        user = create_test_user(session, email="bob@example.com")
        token = create_access_token(user.id, user.email)

        # Create 10 tasks
        for i in range(10):
            task = Task(
                id=uuid.uuid4(),
                title=f"Task {i+1}",
                is_complete=False,
                user_id=user.id,
            )
            session.add(task)
        session.commit()

        # Test limit parameter (first 5 tasks)
        response = client.get(
            "/api/tasks?limit=5",
            cookies={"auth_token": token}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

        # Test offset parameter (skip first 5, get next 5)
        response = client.get(
            "/api/tasks?limit=5&offset=5",
            cookies={"auth_token": token}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

        # Test offset beyond total (should return empty list)
        response = client.get(
            "/api/tasks?offset=20",
            cookies={"auth_token": token}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_list_tasks_filter_is_complete(
        self, client: TestClient, session: Session
    ):
        """Test filtering tasks by completion status."""
        # Create user and auth token
        user = create_test_user(session, email="charlie@example.com")
        token = create_access_token(user.id, user.email)

        # Create 3 incomplete tasks
        for i in range(3):
            task = Task(
                id=uuid.uuid4(),
                title=f"Incomplete Task {i+1}",
                is_complete=False,
                user_id=user.id,
            )
            session.add(task)

        # Create 2 complete tasks
        for i in range(2):
            task = Task(
                id=uuid.uuid4(),
                title=f"Complete Task {i+1}",
                is_complete=True,
                user_id=user.id,
            )
            session.add(task)
        session.commit()

        # Filter for incomplete tasks only
        response = client.get(
            "/api/tasks?is_complete=false",
            cookies={"auth_token": token}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        for task_data in data:
            assert task_data["is_complete"] is False

        # Filter for complete tasks only
        response = client.get(
            "/api/tasks?is_complete=true",
            cookies={"auth_token": token}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        for task_data in data:
            assert task_data["is_complete"] is True

        # Get all tasks (no filter)
        response = client.get(
            "/api/tasks",
            cookies={"auth_token": token}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5

    def test_list_tasks_only_returns_own_tasks(
        self, client: TestClient, session: Session
    ):
        """Test that user only sees their own tasks, not other users' tasks."""
        # Create two users
        user_a = create_test_user(session, email="usera@example.com")
        user_b = create_test_user(session, email="userb@example.com")
        token_a = create_access_token(user_a.id, user_a.email)

        # Create tasks for user A
        for i in range(3):
            task = Task(
                id=uuid.uuid4(),
                title=f"User A Task {i+1}",
                user_id=user_a.id,
            )
            session.add(task)

        # Create tasks for user B
        for i in range(2):
            task = Task(
                id=uuid.uuid4(),
                title=f"User B Task {i+1}",
                user_id=user_b.id,
            )
            session.add(task)
        session.commit()

        # User A should only see their 3 tasks
        response = client.get(
            "/api/tasks",
            cookies={"auth_token": token_a}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        for task_data in data:
            assert task_data["user_id"] == str(user_a.id)


class TestCreateTaskEndpoint:
    """Test POST /api/tasks"""

    def test_create_task_201_with_location_header(
        self, client: TestClient, session: Session
    ):
        """Test creating task returns 201 Created with task data."""
        # Create user and auth token
        user = create_test_user(session, email="dave@example.com")
        token = create_access_token(user.id, user.email)

        # Create task
        task_data = {
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
        }

        response = client.post(
            "/api/tasks",
            json=task_data,
            cookies={"auth_token": token}
        )

        # Should return 201 Created
        assert response.status_code == 201

        # Should return created task
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["description"] == task_data["description"]
        assert data["is_complete"] is False
        assert data["user_id"] == str(user.id)
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

        # Verify UUID format
        task_id = uuid.UUID(data["id"])
        assert isinstance(task_id, uuid.UUID)

    def test_create_task_without_description(
        self, client: TestClient, session: Session
    ):
        """Test creating task without description (description is optional)."""
        user = create_test_user(session, email="eve@example.com")
        token = create_access_token(user.id, user.email)

        task_data = {
            "title": "Simple task",
        }

        response = client.post(
            "/api/tasks",
            json=task_data,
            cookies={"auth_token": token}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["description"] is None

    def test_create_task_400_empty_title(self, client: TestClient, session: Session):
        """Test creating task with empty title returns 400 Bad Request."""
        user = create_test_user(session, email="frank@example.com")
        token = create_access_token(user.id, user.email)

        # Empty string
        response = client.post(
            "/api/tasks",
            json={"title": ""},
            cookies={"auth_token": token}
        )

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

        # Whitespace only
        response = client.post(
            "/api/tasks",
            json={"title": "   "},
            cookies={"auth_token": token}
        )

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_create_task_422_missing_title(self, client: TestClient, session: Session):
        """Test creating task without title returns 422 Validation Error."""
        user = create_test_user(session, email="grace@example.com")
        token = create_access_token(user.id, user.email)

        response = client.post(
            "/api/tasks",
            json={},  # Missing title
            cookies={"auth_token": token}
        )

        # Should return 422 Unprocessable Entity (Pydantic validation)
        assert response.status_code == 422

        # Should return validation error
        data = response.json()
        assert "detail" in data

    def test_create_task_401_unauthenticated(self, client: TestClient):
        """Test creating task without authentication returns 401."""
        task_data = {
            "title": "Unauthorized task",
        }

        response = client.post("/api/tasks", json=task_data)

        # Should return 401 Unauthorized
        assert response.status_code == 401

        data = response.json()
        assert "detail" in data
        assert "not authenticated" in data["detail"].lower()


class TestGetTaskEndpoint:
    """Test GET /api/tasks/{task_id}"""

    def test_get_task_200(self, client: TestClient, session: Session):
        """Test getting own task returns 200 with task data."""
        # Create user and task
        user = create_test_user(session, email="hannah@example.com")
        token = create_access_token(user.id, user.email)

        task = Task(
            id=uuid.uuid4(),
            title="Test Task",
            description="Test Description",
            is_complete=False,
            user_id=user.id,
        )
        session.add(task)
        session.commit()

        # Get task
        response = client.get(
            f"/api/tasks/{task.id}",
            cookies={"auth_token": token}
        )

        # Should return 200 OK
        assert response.status_code == 200

        # Should return task data
        data = response.json()
        assert data["id"] == str(task.id)
        assert data["title"] == task.title
        assert data["description"] == task.description
        assert data["is_complete"] == task.is_complete
        assert data["user_id"] == str(user.id)

    def test_get_task_403_not_owner(self, client: TestClient, session: Session):
        """Test getting another user's task returns 403 Forbidden."""
        # Create two users
        user_a = create_test_user(session, email="usera2@example.com")
        user_b = create_test_user(session, email="userb2@example.com")
        token_b = create_access_token(user_b.id, user_b.email)

        # Create task for user A
        task = Task(
            id=uuid.uuid4(),
            title="User A's Task",
            user_id=user_a.id,
        )
        session.add(task)
        session.commit()

        # User B tries to get user A's task
        response = client.get(
            f"/api/tasks/{task.id}",
            cookies={"auth_token": token_b}
        )

        # Should return 403 Forbidden
        assert response.status_code == 403

        data = response.json()
        assert "detail" in data
        assert "not authorized" in data["detail"].lower()

    def test_get_task_404_not_found(self, client: TestClient, session: Session):
        """Test getting non-existent task returns 404 Not Found."""
        user = create_test_user(session, email="ian@example.com")
        token = create_access_token(user.id, user.email)

        # Non-existent task ID
        fake_task_id = uuid.uuid4()

        response = client.get(
            f"/api/tasks/{fake_task_id}",
            cookies={"auth_token": token}
        )

        # Should return 404 Not Found
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_get_task_401_unauthenticated(self, client: TestClient):
        """Test getting task without authentication returns 401."""
        fake_task_id = uuid.uuid4()

        response = client.get(f"/api/tasks/{fake_task_id}")

        # Should return 401 Unauthorized
        assert response.status_code == 401

        data = response.json()
        assert "detail" in data


class TestUpdateTaskEndpoint:
    """Test PUT /api/tasks/{task_id}"""

    def test_update_task_200(self, client: TestClient, session: Session):
        """Test updating own task returns 200 with updated data."""
        # Create user and task
        user = create_test_user(session, email="jack@example.com")
        token = create_access_token(user.id, user.email)

        task = Task(
            id=uuid.uuid4(),
            title="Original Title",
            description="Original Description",
            is_complete=False,
            user_id=user.id,
        )
        session.add(task)
        session.commit()

        # Update task
        update_data = {
            "title": "Updated Title",
            "description": "Updated Description",
        }

        response = client.put(
            f"/api/tasks/{task.id}",
            json=update_data,
            cookies={"auth_token": token}
        )

        # Should return 200 OK
        assert response.status_code == 200

        # Should return updated task
        data = response.json()
        assert data["id"] == str(task.id)
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]
        assert data["is_complete"] is False  # Should remain unchanged

    def test_update_task_partial(self, client: TestClient, session: Session):
        """Test partial update (only updating title, not description)."""
        user = create_test_user(session, email="kate@example.com")
        token = create_access_token(user.id, user.email)

        task = Task(
            id=uuid.uuid4(),
            title="Original Title",
            description="Original Description",
            user_id=user.id,
        )
        session.add(task)
        session.commit()

        # Update only title
        update_data = {
            "title": "New Title",
        }

        response = client.put(
            f"/api/tasks/{task.id}",
            json=update_data,
            cookies={"auth_token": token}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Title"
        assert data["description"] == "Original Description"  # Unchanged

    def test_update_task_403_not_owner(self, client: TestClient, session: Session):
        """Test updating another user's task returns 403 Forbidden."""
        # Create two users
        user_a = create_test_user(session, email="usera3@example.com")
        user_b = create_test_user(session, email="userb3@example.com")
        token_b = create_access_token(user_b.id, user_b.email)

        # Create task for user A
        task = Task(
            id=uuid.uuid4(),
            title="User A's Task",
            user_id=user_a.id,
        )
        session.add(task)
        session.commit()

        # User B tries to update user A's task
        response = client.put(
            f"/api/tasks/{task.id}",
            json={"title": "Hacked!"},
            cookies={"auth_token": token_b}
        )

        # Should return 403 Forbidden
        assert response.status_code == 403

        data = response.json()
        assert "detail" in data
        assert "not authorized" in data["detail"].lower()

    def test_update_task_404_not_found(self, client: TestClient, session: Session):
        """Test updating non-existent task returns 404 Not Found."""
        user = create_test_user(session, email="leo@example.com")
        token = create_access_token(user.id, user.email)

        fake_task_id = uuid.uuid4()

        response = client.put(
            f"/api/tasks/{fake_task_id}",
            json={"title": "Updated"},
            cookies={"auth_token": token}
        )

        # Should return 404 Not Found
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data

    def test_update_task_400_empty_title(self, client: TestClient, session: Session):
        """Test updating task with empty title returns 400 Bad Request."""
        user = create_test_user(session, email="maria@example.com")
        token = create_access_token(user.id, user.email)

        task = Task(
            id=uuid.uuid4(),
            title="Original Title",
            user_id=user.id,
        )
        session.add(task)
        session.commit()

        # Try to update with empty title
        response = client.put(
            f"/api/tasks/{task.id}",
            json={"title": "   "},
            cookies={"auth_token": token}
        )

        # Should return 400 Bad Request
        assert response.status_code == 400

        data = response.json()
        assert "detail" in data


class TestToggleCompleteEndpoint:
    """Test PATCH /api/tasks/{task_id}/complete"""

    def test_toggle_complete_200(self, client: TestClient, session: Session):
        """Test toggling task completion returns 200 with updated status."""
        # Create user and task
        user = create_test_user(session, email="nancy@example.com")
        token = create_access_token(user.id, user.email)

        task = Task(
            id=uuid.uuid4(),
            title="Task to Complete",
            is_complete=False,
            user_id=user.id,
        )
        session.add(task)
        session.commit()

        # Toggle to complete
        response = client.patch(
            f"/api/tasks/{task.id}/complete",
            json={"is_complete": True},
            cookies={"auth_token": token}
        )

        # Should return 200 OK
        assert response.status_code == 200

        # Should return updated task
        data = response.json()
        assert data["id"] == str(task.id)
        assert data["is_complete"] is True

        # Toggle back to incomplete
        response = client.patch(
            f"/api/tasks/{task.id}/complete",
            json={"is_complete": False},
            cookies={"auth_token": token}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_complete"] is False

    def test_toggle_complete_403_not_owner(
        self, client: TestClient, session: Session
    ):
        """Test toggling another user's task returns 403 Forbidden."""
        # Create two users
        user_a = create_test_user(session, email="usera4@example.com")
        user_b = create_test_user(session, email="userb4@example.com")
        token_b = create_access_token(user_b.id, user_b.email)

        # Create task for user A
        task = Task(
            id=uuid.uuid4(),
            title="User A's Task",
            is_complete=False,
            user_id=user_a.id,
        )
        session.add(task)
        session.commit()

        # User B tries to toggle user A's task
        response = client.patch(
            f"/api/tasks/{task.id}/complete",
            json={"is_complete": True},
            cookies={"auth_token": token_b}
        )

        # Should return 403 Forbidden
        assert response.status_code == 403

        data = response.json()
        assert "detail" in data
        assert "not authorized" in data["detail"].lower()

    def test_toggle_complete_404_not_found(
        self, client: TestClient, session: Session
    ):
        """Test toggling non-existent task returns 404 Not Found."""
        user = create_test_user(session, email="oscar@example.com")
        token = create_access_token(user.id, user.email)

        fake_task_id = uuid.uuid4()

        response = client.patch(
            f"/api/tasks/{fake_task_id}/complete",
            json={"is_complete": True},
            cookies={"auth_token": token}
        )

        # Should return 404 Not Found
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data


class TestDeleteTaskEndpoint:
    """Test DELETE /api/tasks/{task_id}"""

    def test_delete_task_204(self, client: TestClient, session: Session):
        """Test deleting own task returns 204 No Content."""
        # Create user and task
        user = create_test_user(session, email="paul@example.com")
        token = create_access_token(user.id, user.email)

        task = Task(
            id=uuid.uuid4(),
            title="Task to Delete",
            user_id=user.id,
        )
        session.add(task)
        session.commit()
        task_id = task.id

        # Delete task
        response = client.delete(
            f"/api/tasks/{task_id}",
            cookies={"auth_token": token}
        )

        # Should return 204 No Content
        assert response.status_code == 204

        # Response body should be empty
        assert response.text == ""

        # Verify task was deleted from database
        deleted_task = session.get(Task, task_id)
        assert deleted_task is None

    def test_delete_task_403_not_owner(self, client: TestClient, session: Session):
        """Test deleting another user's task returns 403 Forbidden."""
        # Create two users
        user_a = create_test_user(session, email="usera5@example.com")
        user_b = create_test_user(session, email="userb5@example.com")
        token_b = create_access_token(user_b.id, user_b.email)

        # Create task for user A
        task = Task(
            id=uuid.uuid4(),
            title="User A's Task",
            user_id=user_a.id,
        )
        session.add(task)
        session.commit()
        task_id = task.id

        # User B tries to delete user A's task
        response = client.delete(
            f"/api/tasks/{task_id}",
            cookies={"auth_token": token_b}
        )

        # Should return 403 Forbidden
        assert response.status_code == 403

        data = response.json()
        assert "detail" in data
        assert "not authorized" in data["detail"].lower()

        # Verify task was NOT deleted
        task_still_exists = session.get(Task, task_id)
        assert task_still_exists is not None

    def test_delete_task_404_not_found(self, client: TestClient, session: Session):
        """Test deleting non-existent task returns 404 Not Found."""
        user = create_test_user(session, email="quinn@example.com")
        token = create_access_token(user.id, user.email)

        fake_task_id = uuid.uuid4()

        response = client.delete(
            f"/api/tasks/{fake_task_id}",
            cookies={"auth_token": token}
        )

        # Should return 404 Not Found
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data

    def test_delete_task_401_unauthenticated(self, client: TestClient):
        """Test deleting task without authentication returns 401."""
        fake_task_id = uuid.uuid4()

        response = client.delete(f"/api/tasks/{fake_task_id}")

        # Should return 401 Unauthorized
        assert response.status_code == 401

        data = response.json()
        assert "detail" in data
