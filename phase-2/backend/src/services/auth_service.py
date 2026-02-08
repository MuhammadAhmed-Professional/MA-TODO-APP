"""
Authentication Service

Business logic for user authentication operations (signup, login).
Follows "fat services" pattern - all business logic lives here.
"""

import uuid
from datetime import datetime

from fastapi import Depends, HTTPException
from sqlmodel import Session, select

from src.auth.jwt import hash_password, verify_password
from src.db.session import get_session
from src.models.user import User, UserCreate


class AuthService:
    """
    Authentication service handling user signup and login logic.

    All business logic for authentication lives here, keeping
    route handlers thin and focused on HTTP concerns.
    """

    def __init__(self, session: Session = Depends(get_session)):
        """
        Initialize AuthService with database session.

        Args:
            session: SQLModel database session (injected via FastAPI dependency)
        """
        self.session = session

    async def signup(self, user_data: UserCreate) -> User:
        """
        Create new user account with email and password.

        Business logic:
        1. Validate email uniqueness
        2. Hash password with bcrypt
        3. Create user with UUID
        4. Set timestamps
        5. Persist to database

        Args:
            user_data: User signup data (email, name, password)

        Returns:
            Created User object (excludes hashed_password in response)

        Raises:
            HTTPException 400: If email already exists
            HTTPException 422: If validation fails (caught by Pydantic)

        Example:
            service = AuthService(session)
            user = await service.signup(
                UserCreate(
                    email="alice@example.com",
                    name="Alice Smith",
                    password="SecurePass123!"
                )
            )
        """
        # Check if email already exists
        existing_user = self.session.exec(
            select(User).where(User.email == user_data.email)
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered. Please login or use a different email.",
            )

        # Hash password (never store plaintext!)
        hashed_password = hash_password(user_data.password)

        # Create user with hashed password
        user = User(
            id=uuid.uuid4(),
            email=user_data.email,
            name=user_data.name,
            hashed_password=hashed_password,
            createdAt=datetime.utcnow(),  # Better Auth uses camelCase
            updatedAt=datetime.utcnow(),  # Better Auth uses camelCase
        )

        # Persist to database
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        return user

    async def authenticate(self, email: str, password: str) -> User:
        """
        Authenticate user by email and password.

        Verifies credentials and returns User object if valid.
        Used internally by login endpoint.

        Args:
            email: User's email address
            password: Plain text password to verify

        Returns:
            User object if credentials are valid

        Raises:
            HTTPException 401: If email not found or password incorrect

        Example:
            service = AuthService(session)
            user = await service.authenticate("alice@example.com", "SecurePass123!")
        """
        # Find user by email
        user = self.session.exec(select(User).where(User.email == email)).first()

        if not user:
            # Don't reveal whether email exists (security best practice)
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password",
            )

        # Verify password
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password",
            )

        return user

    async def login(self, email: str, password: str) -> User:
        """
        Login user with email and password.

        Thin wrapper around authenticate() for semantic clarity.
        Route handlers call this method directly.

        Args:
            email: User's email address
            password: Plain text password

        Returns:
            User object if login successful

        Raises:
            HTTPException 401: If credentials invalid

        Example:
            service = AuthService(session)
            user = await service.login("alice@example.com", "SecurePass123!")
            # Route handler then creates JWT and sets cookie
        """
        return await self.authenticate(email, password)
