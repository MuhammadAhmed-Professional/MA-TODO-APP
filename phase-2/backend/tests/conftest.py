"""
Pytest Test Fixtures

Provides test database, FastAPI test client, and common test utilities.
"""

import os
import uuid
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from src.auth.jwt import create_access_token, hash_password
from src.db.session import get_session
from src.main import app
from src.models.user import User


# Use in-memory SQLite for tests (fast, isolated)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(name="engine")
def engine_fixture():
    """
    Create a fresh in-memory SQLite engine for each test.

    Uses StaticPool to maintain single connection for in-memory database.
    """
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,  # Set to True for SQL debugging
    )

    # Create all tables
    SQLModel.metadata.create_all(engine)

    yield engine

    # Drop all tables after test
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="session")
def session_fixture(engine) -> Generator[Session, None, None]:
    """
    Provide a clean database session for each test.

    Automatically rolls back changes after each test for isolation.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    # Rollback transaction and close connection
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """
    Provide FastAPI TestClient with test database session.

    Overrides the get_session dependency to use test database.
    """
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session) -> User:
    """
    Create a test user in the database.

    Returns:
        User object with known credentials:
        - Email: test@example.com
        - Password: TestPassword123!
    """
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        name="Test User",
        hashed_password=hash_password("TestPassword123!"),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@pytest.fixture(name="auth_token")
def auth_token_fixture(test_user: User) -> str:
    """
    Generate a valid JWT token for test_user.

    Returns:
        JWT access token string for authentication
    """
    return create_access_token(test_user.id, test_user.email)


@pytest.fixture(name="authenticated_client")
def authenticated_client_fixture(
    client: TestClient,
    auth_token: str
) -> TestClient:
    """
    Provide TestClient with authentication cookie set.

    Returns:
        TestClient with auth_token cookie for authenticated requests
    """
    client.cookies.set("auth_token", auth_token)
    return client


# Helper function for creating test users
def create_test_user(
    session: Session,
    email: str = "alice@example.com",
    name: str = "Alice Smith",
    password: str = "SecurePass123!"
) -> User:
    """
    Create a test user with custom data.

    Args:
        session: Database session
        email: User email (default: alice@example.com)
        name: User name (default: Alice Smith)
        password: Plain password (default: SecurePass123!)

    Returns:
        Created User object
    """
    user = User(
        id=uuid.uuid4(),
        email=email,
        name=name,
        hashed_password=hash_password(password),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user
