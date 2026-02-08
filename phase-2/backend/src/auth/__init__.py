"""
Authentication Package

Provides JWT token handling, password hashing, and auth dependencies.
"""

from src.auth.dependencies import get_current_user, get_optional_user
from src.auth.jwt import (
    create_access_token,
    hash_password,
    verify_password,
    verify_token,
)

__all__ = [
    "create_access_token",
    "verify_token",
    "hash_password",
    "verify_password",
    "get_current_user",
    "get_optional_user",
]
