"""
JWT Token and Password Utilities

Handles JWT token creation/validation and bcrypt password hashing.
"""

import os
from datetime import datetime, timedelta
from typing import Dict
from uuid import UUID

import bcrypt
from dotenv import load_dotenv
from fastapi import HTTPException
from jose import ExpiredSignatureError, JWTError, jwt

# Load environment variables
load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET", "dev-secret-replace-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))


def create_access_token(user_id: UUID, email: str) -> str:
    """
    Create JWT access token with user claims.

    Args:
        user_id: User's UUID
        email: User's email address

    Returns:
        Encoded JWT token string

    Example:
        >>> token = create_access_token(user.id, user.email)
        >>> # Returns: "eyJhbGc..." (JWT string)
    """
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "user_id": str(user_id),
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Dict[str, str]:
    """
    Validate JWT token and return claims.

    Args:
        token: JWT token string to validate

    Returns:
        Dictionary containing user claims (user_id, email, exp, iat)

    Raises:
        HTTPException: 401 if token is invalid or expired

    Example:
        >>> payload = verify_token("eyJhbGc...")
        >>> print(payload["user_id"])
        >>> # Returns: "550e8400-e29b-41d4-a716-446655440000"
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        # Token has expired (exp claim exceeded)
        raise HTTPException(
            status_code=401,
            detail="Session expired. Please log in again.",
        )
    except JWTError as e:
        # Invalid token (signature mismatch, malformed, etc.)
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token. Please log in again.",
        )


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        Bcrypt hashed password string

    Example:
        >>> hashed = hash_password("SecurePass123!")
        >>> # Returns: "$2b$12$..." (bcrypt hash)
    """
    # Convert password to bytes
    password_bytes = password.encode("utf-8")

    # Generate salt and hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)

    # Return as string
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against bcrypt hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hashed password from database

    Returns:
        True if password matches, False otherwise

    Example:
        >>> is_valid = verify_password("SecurePass123!", user.hashed_password)
        >>> if is_valid:
        >>>     print("Password correct!")
    """
    # Convert both to bytes
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")

    # Verify password
    return bcrypt.checkpw(password_bytes, hashed_bytes)
