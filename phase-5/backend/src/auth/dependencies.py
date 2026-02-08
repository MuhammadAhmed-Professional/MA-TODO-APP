"""
Authentication Dependencies (Phase V)

FastAPI dependencies for extracting authenticated user from JWT token.
"""

import os
from typing import Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from sqlmodel import Session, select

from src.db.session import get_session
from src.models.user import User

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# HTTP Bearer scheme for Authorization header
security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session: Session = Depends(get_session),
) -> User:
    """
    Extract authenticated user from JWT token.

    Supports both Authorization header and HttpOnly cookie.

    **Raises:**
    - HTTPException 401: Not authenticated or invalid token
    - HTTPException 404: User not found in database

    **Returns:**
    - User model from database
    """
    # Try Authorization header first
    token = credentials.credentials if credentials else None

    # Fallback to cookie
    if not token:
        token = request.cookies.get("auth_token")

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Decode and verify JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub") or payload.get("user_id")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")

    except jwt.JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    # Fetch user from database
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


async def get_optional_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    session: Session = Depends(get_session),
) -> Optional[User]:
    """
    Optional authentication - returns user if authenticated, None otherwise.

    Does not raise HTTPException if not authenticated.
    Useful for public endpoints that return personalized data when logged in.
    """
    try:
        return await get_current_user(request, credentials, session)
    except HTTPException:
        return None
