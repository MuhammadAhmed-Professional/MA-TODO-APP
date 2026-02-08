"""
FastAPI Authentication Dependencies

Provides dependency injection for extracting and validating authenticated users.
"""

import os
from datetime import datetime
from uuid import UUID

import httpx
from fastapi import Depends, HTTPException, Request
from sqlmodel import Session, select

from src.auth.jwt import verify_token
from src.db.session import get_session
from src.models.user import User
from src.models.session import BetterAuthSession

# Auth server URL (kept for reference, but no longer used for session validation)
AUTH_SERVER_URL = os.getenv("AUTH_SERVER_URL", "http://localhost:3001")


async def get_current_user(
    request: Request,
    db_session: Session = Depends(get_session),
) -> User:
    """
    FastAPI dependency to extract authenticated user from Better Auth session token.

    Validates session token by querying the Better Auth session table in the
    shared database. This is faster and more reliable than calling the auth
    server over HTTP, especially in cross-domain deployments.

    Token Sources (checked in order):
    1. Authorization header: "Bearer <token>"
    2. Cookie: "auth_token"

    Args:
        request: FastAPI Request object (contains headers and cookies)
        db_session: Database session (injected via dependency)

    Returns:
        User object for the authenticated user

    Raises:
        HTTPException 401: If token is missing, invalid, expired, or user not found

    Usage:
        @router.get("/api/tasks")
        async def list_tasks(current_user: User = Depends(get_current_user)):
            # current_user is automatically extracted and validated
            tasks = get_tasks_for_user(current_user.id)
            return tasks

    Example Flow:
        1. User logs in via Better Auth (returns session token in JSON)
        2. Frontend stores token and sends in Authorization header
        3. Dependency extracts token from header (or cookie fallback)
        4. Token is validated by querying Better Auth's `session` table
        5. User is fetched from database by userId from session
        6. User object is returned to route handler

    Architecture Note:
        This approach avoids the cross-domain cookie issues and HTTP overhead
        of calling the auth server. Both services share the same Neon database,
        so querying the session table directly is safe and efficient.
    """
    # Try Authorization header first (for cross-domain requests)
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]  # Remove "Bearer " prefix

    # Fallback to cookie (for same-domain requests)
    if not token:
        token = request.cookies.get("auth_token")

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated - missing auth token",
        )

    # Query Better Auth session table directly
    # The token from the login response JSON matches the session.token column (not id!)
    query = select(BetterAuthSession).where(BetterAuthSession.token == token)
    session_record = db_session.exec(query).first()

    if not session_record:
        raise HTTPException(
            status_code=401,
            detail="Invalid session token - session not found",
        )

    # Check if session has expired
    if session_record.expiresAt < datetime.utcnow():
        raise HTTPException(
            status_code=401,
            detail="Session expired - please log in again",
        )

    # Fetch user from database using userId from session
    # Better Auth uses string IDs, not UUIDs
    user_query = select(User).where(User.id == session_record.userId)
    user = db_session.exec(user_query).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found - session may be for deleted account",
        )

    return user


def get_optional_user(
    request: Request,
    session: Session = Depends(get_session),
) -> User | None:
    """
    FastAPI dependency to optionally extract authenticated user from Better Auth token.

    Similar to get_current_user but returns None instead of raising
    HTTPException when user is not authenticated. Useful for endpoints
    that work for both authenticated and anonymous users.

    Args:
        request: FastAPI Request object
        session: Database session (injected via dependency)

    Returns:
        User object if authenticated, None otherwise

    Usage:
        @router.get("/api/public/tasks")
        async def list_public_tasks(user: User | None = Depends(get_optional_user)):
            if user:
                # Show user's private tasks + public tasks
                tasks = get_all_tasks(user.id)
            else:
                # Show only public tasks
                tasks = get_public_tasks()
            return tasks
    """
    # Extract token from HttpOnly cookie
    token = request.cookies.get("auth_token")

    if not token:
        return None

    # Verify and decode JWT token
    try:
        payload = verify_token(token)

        # Better Auth uses 'userId' (camelCase) in JWT payload
        user_id_str = (
            payload.get("userId")  # Better Auth format
            or payload.get("user_id")  # Legacy format
            or payload.get("sub")  # Standard JWT 'subject' claim
        )

        if not user_id_str:
            return None

        user_id = UUID(user_id_str)

    except (ValueError, HTTPException):
        # Invalid token format or verification failed
        return None

    # Fetch user from database
    user = session.get(User, user_id)
    return user  # Returns None if user not found
