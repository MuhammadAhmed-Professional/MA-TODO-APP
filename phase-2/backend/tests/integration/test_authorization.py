"""
Integration Tests for Authorization and Security

Tests cross-user access control, rate limiting, JWT expiration, and authorization
on all task endpoints.

Coverage:
- Ownership checks (User A cannot access User B's tasks)
- Rate limiting on login endpoint
- JWT token expiration validation
- Authorization checks on all task endpoints (GET, PUT, PATCH, DELETE)
"""

import time
from datetime import datetime, timedelta
from uuid import uuid4

from jose import jwt
import pytest
from fastapi.testclient import TestClient

from src.auth.jwt import create_access_token, hash_password, SECRET_KEY, ALGORITHM
from src.models.user import User


@pytest.fixture(name="user_a")
def user_a_fixture(session) -> User:
    """Create User A for cross-user access tests."""
    user = User(
        id=uuid4(),
        email="usera@example.com",
        name="User A",
        hashed_password=hash_password("password123"),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="user_b")
def user_b_fixture(session) -> User:
    """Create User B for cross-user access tests."""
    user = User(
        id=uuid4(),
        email="userb@example.com",
        name="User B",
        hashed_password=hash_password("password123"),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="user_a_token")
def user_a_token_fixture(user_a: User) -> str:
    """Generate JWT token for User A."""
    return create_access_token(user_a.id, user_a.email)


@pytest.fixture(name="user_b_token")
def user_b_token_fixture(user_b: User) -> str:
    """Generate JWT token for User B."""
    return create_access_token(user_b.id, user_b.email)


class TestOwnershipChecks:
    """Test that users cannot access other users' tasks."""

    def test_user_cannot_get_other_user_tasks(
        self, client: TestClient, user_a_token: str, user_b_token: str
    ):
        """User A creates task, User B cannot GET it (403 Forbidden)."""
        # User A creates task
        create_response = client.post(
            "/api/tasks",
            json={"title": "User A's task"},
            cookies={"auth_token": user_a_token},
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # User B tries to GET User A's task
        get_response = client.get(
            f"/api/tasks/{task_id}",
            cookies={"auth_token": user_b_token},
        )
        assert get_response.status_code == 403
        assert "not authorized" in get_response.json()["detail"].lower()

    def test_user_cannot_update_other_user_tasks(
        self, client: TestClient, user_a_token: str, user_b_token: str
    ):
        """User A creates task, User B cannot UPDATE it (403 Forbidden)."""
        # User A creates task
        create_response = client.post(
            "/api/tasks",
            json={"title": "User A's task"},
            cookies={"auth_token": user_a_token},
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # User B tries to UPDATE User A's task
        update_response = client.put(
            f"/api/tasks/{task_id}",
            json={"title": "Hacked title"},
            cookies={"auth_token": user_b_token},
        )
        assert update_response.status_code == 403
        assert "not authorized" in update_response.json()["detail"].lower()

    def test_user_cannot_delete_other_user_tasks(
        self, client: TestClient, user_a_token: str, user_b_token: str
    ):
        """User A creates task, User B cannot DELETE it (403 Forbidden)."""
        # User A creates task
        create_response = client.post(
            "/api/tasks",
            json={"title": "User A's task"},
            cookies={"auth_token": user_a_token},
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # User B tries to DELETE User A's task
        delete_response = client.delete(
            f"/api/tasks/{task_id}",
            cookies={"auth_token": user_b_token},
        )
        assert delete_response.status_code == 403
        assert "not authorized" in delete_response.json()["detail"].lower()

    def test_user_cannot_toggle_other_user_tasks(
        self, client: TestClient, user_a_token: str, user_b_token: str
    ):
        """User A creates task, User B cannot TOGGLE it (403 Forbidden)."""
        # User A creates task
        create_response = client.post(
            "/api/tasks",
            json={"title": "User A's task"},
            cookies={"auth_token": user_a_token},
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # User B tries to TOGGLE User A's task
        toggle_response = client.patch(
            f"/api/tasks/{task_id}/complete",
            json={"is_complete": True},
            cookies={"auth_token": user_b_token},
        )
        assert toggle_response.status_code == 403
        assert "not authorized" in toggle_response.json()["detail"].lower()

    def test_list_tasks_only_returns_own_tasks(
        self, client: TestClient, user_a_token: str, user_b_token: str
    ):
        """User A sees only their tasks, User B sees only their tasks."""
        # User A creates 2 tasks
        client.post(
            "/api/tasks",
            json={"title": "A1"},
            cookies={"auth_token": user_a_token},
        )
        client.post(
            "/api/tasks",
            json={"title": "A2"},
            cookies={"auth_token": user_a_token},
        )

        # User B creates 1 task
        client.post(
            "/api/tasks",
            json={"title": "B1"},
            cookies={"auth_token": user_b_token},
        )

        # User A lists tasks
        a_response = client.get("/api/tasks", cookies={"auth_token": user_a_token})
        assert a_response.status_code == 200
        a_tasks = a_response.json()
        assert len(a_tasks) == 2
        assert all(t["title"].startswith("A") for t in a_tasks)

        # User B lists tasks
        b_response = client.get("/api/tasks", cookies={"auth_token": user_b_token})
        assert b_response.status_code == 200
        b_tasks = b_response.json()
        assert len(b_tasks) == 1
        assert b_tasks[0]["title"] == "B1"

    def test_user_can_access_own_tasks_after_another_user_creates(
        self, client: TestClient, user_a_token: str, user_b_token: str
    ):
        """Verify User A can still access their own task after User B creates tasks."""
        # User A creates task
        create_response = client.post(
            "/api/tasks",
            json={"title": "User A's task"},
            cookies={"auth_token": user_a_token},
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # User B creates task
        client.post(
            "/api/tasks",
            json={"title": "User B's task"},
            cookies={"auth_token": user_b_token},
        )

        # User A can still access their own task
        get_response = client.get(
            f"/api/tasks/{task_id}",
            cookies={"auth_token": user_a_token},
        )
        assert get_response.status_code == 200
        assert get_response.json()["title"] == "User A's task"


class TestRateLimiting:
    """Test rate limiting on authentication endpoints."""

    def test_login_rate_limiting(self, client: TestClient, session):
        """Login endpoint rate limited to 5 attempts per minute."""
        # Create a user to test against
        user = User(
            id=uuid4(),
            email="ratelimit@example.com",
            name="Rate Limit Test",
            hashed_password=hash_password("correctpassword"),
        )
        session.add(user)
        session.commit()

        # Make 5 login attempts with wrong password (should all return 401)
        for i in range(5):
            response = client.post(
                "/api/auth/login",
                json={"email": "ratelimit@example.com", "password": "wrongpassword"},
            )
            assert response.status_code == 401, f"Attempt {i+1} should return 401 Unauthorized"

        # 6th attempt should be rate limited (429 Too Many Requests)
        response = client.post(
            "/api/auth/login",
            json={"email": "ratelimit@example.com", "password": "wrongpassword"},
        )
        assert response.status_code == 429, "6th attempt should be rate limited"
        assert "rate limit" in response.text.lower() or "too many" in response.text.lower()

    def test_successful_login_not_affected_by_rate_limit(self, client: TestClient, session):
        """Valid login attempts should succeed within rate limit."""
        # Create a user
        user = User(
            id=uuid4(),
            email="valid@example.com",
            name="Valid User",
            hashed_password=hash_password("correctpassword"),
        )
        session.add(user)
        session.commit()

        # Make 3 successful login attempts (should all succeed)
        for i in range(3):
            response = client.post(
                "/api/auth/login",
                json={"email": "valid@example.com", "password": "correctpassword"},
            )
            assert response.status_code == 200, f"Attempt {i+1} should succeed"
            assert "auth_token" in response.cookies


class TestJWTExpiration:
    """Test JWT token expiration validation."""

    def test_expired_jwt_returns_401(self, client: TestClient, user_a: User):
        """Expired JWT token returns 401 Unauthorized."""
        # Create an expired JWT token (expired 1 minute ago)
        expired_payload = {
            "user_id": str(user_a.id),
            "email": user_a.email,
            "exp": datetime.utcnow() - timedelta(minutes=1),
            "iat": datetime.utcnow() - timedelta(minutes=16),
        }
        expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)

        # Try to access protected endpoint with expired token
        response = client.get(
            "/api/tasks",
            cookies={"auth_token": expired_token},
        )
        assert response.status_code == 401
        error_detail = response.json()["detail"].lower()
        assert "invalid" in error_detail or "expired" in error_detail or "token" in error_detail

    def test_valid_jwt_within_expiry_succeeds(self, client: TestClient, user_a_token: str):
        """Valid JWT token within expiry time should work."""
        # Valid token should allow access
        response = client.get(
            "/api/tasks",
            cookies={"auth_token": user_a_token},
        )
        assert response.status_code == 200

    def test_jwt_with_missing_exp_claim_rejected(self, client: TestClient, user_a: User):
        """JWT token without expiration claim should be rejected."""
        # Create token without exp claim
        invalid_payload = {
            "user_id": str(user_a.id),
            "email": user_a.email,
            # Missing exp claim
        }
        invalid_token = jwt.encode(invalid_payload, SECRET_KEY, algorithm=ALGORITHM)

        # Try to access protected endpoint
        response = client.get(
            "/api/tasks",
            cookies={"auth_token": invalid_token},
        )
        # Should be rejected (401) due to missing exp claim
        assert response.status_code == 401

    def test_jwt_with_invalid_signature_rejected(self, client: TestClient, user_a: User):
        """JWT token with invalid signature should be rejected."""
        # Create token with wrong secret
        payload = {
            "user_id": str(user_a.id),
            "email": user_a.email,
            "exp": datetime.utcnow() + timedelta(minutes=15),
            "iat": datetime.utcnow(),
        }
        invalid_token = jwt.encode(payload, "wrong-secret-key", algorithm=ALGORITHM)

        # Try to access protected endpoint
        response = client.get(
            "/api/tasks",
            cookies={"auth_token": invalid_token},
        )
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()


class TestAuthorizationOnAllEndpoints:
    """Test that all task endpoints require authentication."""

    def test_create_task_without_auth_returns_401(self, client: TestClient):
        """Creating task without authentication returns 401."""
        response = client.post(
            "/api/tasks",
            json={"title": "Test Task"},
        )
        assert response.status_code == 401
        assert "not authenticated" in response.json()["detail"].lower()

    def test_list_tasks_without_auth_returns_401(self, client: TestClient):
        """Listing tasks without authentication returns 401."""
        response = client.get("/api/tasks")
        assert response.status_code == 401
        assert "not authenticated" in response.json()["detail"].lower()

    def test_get_task_without_auth_returns_401(self, client: TestClient):
        """Getting single task without authentication returns 401."""
        task_id = uuid4()
        response = client.get(f"/api/tasks/{task_id}")
        assert response.status_code == 401
        assert "not authenticated" in response.json()["detail"].lower()

    def test_update_task_without_auth_returns_401(self, client: TestClient):
        """Updating task without authentication returns 401."""
        task_id = uuid4()
        response = client.put(
            f"/api/tasks/{task_id}",
            json={"title": "Updated Task"},
        )
        assert response.status_code == 401
        assert "not authenticated" in response.json()["detail"].lower()

    def test_toggle_task_without_auth_returns_401(self, client: TestClient):
        """Toggling task completion without authentication returns 401."""
        task_id = uuid4()
        response = client.patch(
            f"/api/tasks/{task_id}/complete",
            json={"is_complete": True},
        )
        assert response.status_code == 401
        assert "not authenticated" in response.json()["detail"].lower()

    def test_delete_task_without_auth_returns_401(self, client: TestClient):
        """Deleting task without authentication returns 401."""
        task_id = uuid4()
        response = client.delete(f"/api/tasks/{task_id}")
        assert response.status_code == 401
        assert "not authenticated" in response.json()["detail"].lower()

    def test_invalid_token_returns_401_for_all_endpoints(
        self, client: TestClient, user_a_token: str
    ):
        """Invalid JWT token returns 401 for all protected endpoints."""
        invalid_token = "invalid.jwt.token"

        # Test all task endpoints
        endpoints = [
            ("GET", "/api/tasks", None),
            ("POST", "/api/tasks", {"title": "Test"}),
            ("GET", f"/api/tasks/{uuid4()}", None),
            ("PUT", f"/api/tasks/{uuid4()}", {"title": "Updated"}),
            ("PATCH", f"/api/tasks/{uuid4()}/complete", {"is_complete": True}),
            ("DELETE", f"/api/tasks/{uuid4()}", None),
        ]

        for method, path, json_data in endpoints:
            if method == "GET":
                response = client.get(path, cookies={"auth_token": invalid_token})
            elif method == "POST":
                response = client.post(
                    path, json=json_data, cookies={"auth_token": invalid_token}
                )
            elif method == "PUT":
                response = client.put(
                    path, json=json_data, cookies={"auth_token": invalid_token}
                )
            elif method == "PATCH":
                response = client.patch(
                    path, json=json_data, cookies={"auth_token": invalid_token}
                )
            elif method == "DELETE":
                response = client.delete(path, cookies={"auth_token": invalid_token})

            assert response.status_code == 401, f"{method} {path} should return 401 with invalid token"
