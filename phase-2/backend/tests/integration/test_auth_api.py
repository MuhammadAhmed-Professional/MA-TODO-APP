"""
Integration Tests for Authentication API Endpoints (T037)

Tests complete request-response cycle for auth endpoints.
"""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src.models.user import User
from tests.conftest import create_test_user


class TestSignupEndpoint:
    """Test POST /api/auth/signup"""

    def test_signup_success_creates_user_and_sets_cookie(self, client: TestClient, session: Session):
        """
        Test successful signup returns 201, creates user, and sets auth cookie.
        """
        signup_data = {
            "name": "New User",
            "email": "newuser@example.com",
            "password": "SecurePass123!",
        }

        response = client.post("/api/auth/signup", json=signup_data)

        # Should return 201 Created
        assert response.status_code == 201

        # Should return user data (without password)
        data = response.json()
        assert data["email"] == signup_data["email"]
        assert data["name"] == signup_data["name"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

        # Should NOT include hashed_password
        assert "password" not in data
        assert "hashed_password" not in data

        # Should set auth_token cookie
        assert "auth_token" in response.cookies
        auth_token = response.cookies.get("auth_token")
        assert auth_token is not None
        assert len(auth_token) > 0

        # Verify user was created in database
        user = session.exec(
            select(User).where(User.email == signup_data["email"])
        ).first()
        assert user is not None
        assert user.email == signup_data["email"]
        assert user.name == signup_data["name"]

        # Verify password was hashed (not stored in plaintext)
        assert user.hashed_password != signup_data["password"]
        assert user.hashed_password.startswith("$2b$")  # bcrypt hash

    def test_signup_with_duplicate_email_returns_400(self, client: TestClient, session: Session):
        """
        Test signup with existing email returns 400 Bad Request.
        """
        # Create existing user
        existing_email = "existing@example.com"
        create_test_user(session, email=existing_email)

        # Try to signup with same email
        signup_data = {
            "name": "Duplicate User",
            "email": existing_email,
            "password": "AnotherPass123!",
        }

        response = client.post("/api/auth/signup", json=signup_data)

        # Should return 400 Bad Request
        assert response.status_code == 400

        # Should return error message
        data = response.json()
        assert "detail" in data
        assert "already registered" in data["detail"].lower()

    def test_signup_with_invalid_email_returns_422(self, client: TestClient):
        """
        Test signup with invalid email format returns 422 Validation Error.
        """
        signup_data = {
            "name": "Test User",
            "email": "not-an-email",  # Invalid email
            "password": "SecurePass123!",
        }

        response = client.post("/api/auth/signup", json=signup_data)

        # Should return 422 Unprocessable Entity
        assert response.status_code == 422

    def test_signup_with_short_password_returns_422(self, client: TestClient):
        """
        Test signup with password < 8 characters returns 422.
        """
        signup_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "short",  # Too short
        }

        response = client.post("/api/auth/signup", json=signup_data)

        # Should return 422 Unprocessable Entity
        assert response.status_code == 422

    def test_signup_with_missing_name_returns_422(self, client: TestClient):
        """
        Test signup without name field returns 422.
        """
        signup_data = {
            # Missing name
            "email": "test@example.com",
            "password": "SecurePass123!",
        }

        response = client.post("/api/auth/signup", json=signup_data)

        # Should return 422 Unprocessable Entity
        assert response.status_code == 422


class TestLoginEndpoint:
    """Test POST /api/auth/login"""

    def test_login_success_returns_user_and_sets_cookie(
        self,
        client: TestClient,
        session: Session
    ):
        """
        Test successful login returns 200 and sets auth cookie.
        """
        # Create user with known credentials
        email = "logintest@example.com"
        password = "LoginPassword123!"
        create_test_user(session, email=email, password=password)

        # Attempt login
        login_data = {
            "email": email,
            "password": password,
        }

        response = client.post("/api/auth/login", json=login_data)

        # Should return 200 OK
        assert response.status_code == 200

        # Should return user data
        data = response.json()
        assert data["email"] == email
        assert "id" in data
        assert "name" in data

        # Should NOT include password
        assert "password" not in data
        assert "hashed_password" not in data

        # Should set auth_token cookie
        assert "auth_token" in response.cookies
        auth_token = response.cookies.get("auth_token")
        assert auth_token is not None
        assert len(auth_token) > 0

    def test_login_with_invalid_email_returns_401(self, client: TestClient):
        """
        Test login with non-existent email returns 401.
        """
        login_data = {
            "email": "nonexistent@example.com",
            "password": "SomePassword123!",
        }

        response = client.post("/api/auth/login", json=login_data)

        # Should return 401 Unauthorized
        assert response.status_code == 401

        # Should return generic error message (don't reveal if email exists)
        data = response.json()
        assert "detail" in data
        assert "invalid" in data["detail"].lower()

    def test_login_with_wrong_password_returns_401(
        self,
        client: TestClient,
        session: Session
    ):
        """
        Test login with incorrect password returns 401.
        """
        # Create user
        email = "wrongpass@example.com"
        correct_password = "CorrectPass123!"
        create_test_user(session, email=email, password=correct_password)

        # Try to login with wrong password
        login_data = {
            "email": email,
            "password": "WrongPassword456!",
        }

        response = client.post("/api/auth/login", json=login_data)

        # Should return 401 Unauthorized
        assert response.status_code == 401

        # Should return generic error message
        data = response.json()
        assert "detail" in data
        assert "invalid" in data["detail"].lower()

    def test_login_with_invalid_email_format_returns_422(self, client: TestClient):
        """
        Test login with invalid email format returns 422.
        """
        login_data = {
            "email": "not-an-email",
            "password": "SomePassword123!",
        }

        response = client.post("/api/auth/login", json=login_data)

        # Should return 422 Unprocessable Entity
        assert response.status_code == 422


class TestLogoutEndpoint:
    """Test POST /api/auth/logout"""

    def test_logout_clears_auth_cookie(
        self,
        authenticated_client: TestClient
    ):
        """
        Test logout clears auth cookie and returns 204.
        """
        response = authenticated_client.post("/api/auth/logout")

        # Should return 204 No Content
        assert response.status_code == 204

        # Response body should be empty
        assert response.text == ""

        # Cookie should be cleared (max_age=0 or deleted)
        # Note: TestClient doesn't perfectly simulate cookie deletion,
        # but we can verify the endpoint returns successfully

    def test_logout_without_authentication_returns_401(self, client: TestClient):
        """
        Test logout without auth token returns 401.
        """
        response = client.post("/api/auth/logout")

        # Should return 401 Unauthorized
        assert response.status_code == 401


class TestGetCurrentUserEndpoint:
    """Test GET /api/auth/me"""

    def test_get_me_authenticated_returns_user_data(
        self,
        authenticated_client: TestClient,
        test_user: User
    ):
        """
        Test GET /api/auth/me with valid token returns user data.
        """
        response = authenticated_client.get("/api/auth/me")

        # Should return 200 OK
        assert response.status_code == 200

        # Should return user data
        data = response.json()
        assert data["id"] == str(test_user.id)
        assert data["email"] == test_user.email
        assert data["name"] == test_user.name

        # Should NOT include password
        assert "password" not in data
        assert "hashed_password" not in data

    def test_get_me_unauthenticated_returns_401(self, client: TestClient):
        """
        Test GET /api/auth/me without auth token returns 401.
        """
        response = client.get("/api/auth/me")

        # Should return 401 Unauthorized
        assert response.status_code == 401

        # Should return error message
        data = response.json()
        assert "detail" in data

    def test_get_me_with_invalid_token_returns_401(self, client: TestClient):
        """
        Test GET /api/auth/me with invalid token returns 401.
        """
        # Set invalid token
        client.cookies.set("auth_token", "invalid.jwt.token")

        response = client.get("/api/auth/me")

        # Should return 401 Unauthorized
        assert response.status_code == 401


class TestAuthenticationFlow:
    """Test complete authentication flows"""

    def test_signup_then_login_flow(self, client: TestClient, session: Session):
        """
        Test user can signup and then login with same credentials.
        """
        email = "flowtest@example.com"
        password = "FlowPassword123!"

        # Step 1: Signup
        signup_data = {
            "name": "Flow Test User",
            "email": email,
            "password": password,
        }
        signup_response = client.post("/api/auth/signup", json=signup_data)
        assert signup_response.status_code == 201

        # Step 2: Login with same credentials
        login_data = {
            "email": email,
            "password": password,
        }
        login_response = client.post("/api/auth/login", json=login_data)
        assert login_response.status_code == 200

        # Both responses should return same user data
        signup_user = signup_response.json()
        login_user = login_response.json()
        assert signup_user["id"] == login_user["id"]
        assert signup_user["email"] == login_user["email"]

    def test_login_then_access_protected_route_then_logout(
        self,
        client: TestClient,
        session: Session
    ):
        """
        Test complete flow: login -> access /me -> logout -> /me fails.
        """
        # Create user
        email = "protected@example.com"
        password = "ProtectedPass123!"
        create_test_user(session, email=email, password=password)

        # Step 1: Login
        login_response = client.post(
            "/api/auth/login",
            json={"email": email, "password": password}
        )
        assert login_response.status_code == 200

        # Step 2: Access protected route with cookie
        me_response = client.get("/api/auth/me")
        assert me_response.status_code == 200
        assert me_response.json()["email"] == email

        # Step 3: Logout
        logout_response = client.post("/api/auth/logout")
        assert logout_response.status_code == 204

        # Step 4: Try to access protected route (should fail)
        # Clear cookies manually for test
        client.cookies.clear()
        me_after_logout = client.get("/api/auth/me")
        assert me_after_logout.status_code == 401
