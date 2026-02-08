"""
Unit Tests for Authentication Utilities (T036)

Tests JWT token creation/validation and password hashing/verification.
"""

import uuid
from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException
from jose import jwt

from src.auth.jwt import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    hash_password,
    verify_password,
    verify_token,
)


class TestPasswordHashing:
    """Test password hashing and verification"""

    def test_hash_password_creates_different_hashes_for_same_password(self):
        """
        Test that hash_password creates different hashes for same password.

        This ensures that bcrypt's salt is working correctly - each hash
        should be unique even for identical passwords.
        """
        password = "SecurePassword123!"

        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Hashes should be different (bcrypt uses random salt)
        assert hash1 != hash2

        # Both hashes should be non-empty strings
        assert isinstance(hash1, str)
        assert isinstance(hash2, str)
        assert len(hash1) > 0
        assert len(hash2) > 0

        # Both should start with bcrypt prefix
        assert hash1.startswith("$2b$")
        assert hash2.startswith("$2b$")

    def test_verify_password_works_with_correct_password(self):
        """
        Test that verify_password returns True for correct password.
        """
        password = "MySecurePassword123!"
        hashed = hash_password(password)

        # Correct password should verify successfully
        assert verify_password(password, hashed) is True

    def test_verify_password_fails_with_wrong_password(self):
        """
        Test that verify_password returns False for incorrect password.
        """
        password = "CorrectPassword123!"
        wrong_password = "WrongPassword456!"
        hashed = hash_password(password)

        # Wrong password should fail verification
        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_fails_with_slightly_different_password(self):
        """
        Test that even minor password differences fail verification.
        """
        password = "SecurePass123!"
        hashed = hash_password(password)

        # Test various incorrect variations
        assert verify_password("SecurePass123", hashed) is False  # Missing !
        assert verify_password("securepass123!", hashed) is False  # Wrong case
        assert verify_password("SecurePass123! ", hashed) is False  # Extra space
        assert verify_password(" SecurePass123!", hashed) is False  # Leading space


class TestJWTTokens:
    """Test JWT token creation and validation"""

    def test_create_access_token_generates_valid_jwt(self):
        """
        Test that create_access_token generates a valid JWT token.
        """
        user_id = uuid.uuid4()
        email = "test@example.com"

        token = create_access_token(user_id, email)

        # Token should be a non-empty string
        assert isinstance(token, str)
        assert len(token) > 0

        # Token should have 3 parts (header.payload.signature)
        assert token.count(".") == 2

        # Should be decodable with our secret
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload is not None

    def test_create_access_token_includes_correct_claims(self):
        """
        Test that JWT token contains expected claims.
        """
        user_id = uuid.uuid4()
        email = "alice@example.com"

        token = create_access_token(user_id, email)

        # Decode token to inspect claims
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Verify required claims
        assert payload["user_id"] == str(user_id)
        assert payload["email"] == email
        assert "exp" in payload  # Expiration time
        assert "iat" in payload  # Issued at time

        # Verify expiration is in the future
        exp_timestamp = payload["exp"]
        assert exp_timestamp > datetime.utcnow().timestamp()

    def test_verify_token_decodes_jwt_correctly(self):
        """
        Test that verify_token successfully decodes valid JWT.
        """
        user_id = uuid.uuid4()
        email = "bob@example.com"

        token = create_access_token(user_id, email)
        payload = verify_token(token)

        # Should return payload with correct claims
        assert payload["user_id"] == str(user_id)
        assert payload["email"] == email
        assert "exp" in payload
        assert "iat" in payload

    def test_verify_token_raises_http_exception_for_invalid_token(self):
        """
        Test that verify_token raises HTTPException for invalid token.
        """
        invalid_token = "invalid.jwt.token"

        with pytest.raises(HTTPException) as exc_info:
            verify_token(invalid_token)

        # Should raise 401 Unauthorized
        assert exc_info.value.status_code == 401
        assert "Invalid authentication token" in exc_info.value.detail

    def test_verify_token_raises_http_exception_for_expired_token(self):
        """
        Test that verify_token raises HTTPException for expired token.
        """
        user_id = uuid.uuid4()
        email = "expired@example.com"

        # Create expired token (expired 1 hour ago)
        expire = datetime.utcnow() - timedelta(hours=1)
        to_encode = {
            "user_id": str(user_id),
            "email": email,
            "exp": expire,
            "iat": datetime.utcnow() - timedelta(hours=2),
        }
        expired_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        with pytest.raises(HTTPException) as exc_info:
            verify_token(expired_token)

        # Should raise 401 Unauthorized
        assert exc_info.value.status_code == 401
        assert "Invalid authentication token" in exc_info.value.detail

    def test_verify_token_raises_http_exception_for_wrong_secret(self):
        """
        Test that token signed with different secret is rejected.
        """
        user_id = uuid.uuid4()
        email = "hacker@example.com"

        # Create token with wrong secret
        expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode = {
            "user_id": str(user_id),
            "email": email,
            "exp": expire,
            "iat": datetime.utcnow(),
        }
        wrong_secret_token = jwt.encode(
            to_encode,
            "wrong-secret-key",
            algorithm=ALGORITHM
        )

        with pytest.raises(HTTPException) as exc_info:
            verify_token(wrong_secret_token)

        # Should raise 401 Unauthorized
        assert exc_info.value.status_code == 401

    def test_create_access_token_with_different_users_creates_different_tokens(self):
        """
        Test that different users get different tokens.
        """
        user1_id = uuid.uuid4()
        user2_id = uuid.uuid4()

        token1 = create_access_token(user1_id, "user1@example.com")
        token2 = create_access_token(user2_id, "user2@example.com")

        # Tokens should be different
        assert token1 != token2

        # Decoding should reveal different user_ids
        payload1 = verify_token(token1)
        payload2 = verify_token(token2)

        assert payload1["user_id"] != payload2["user_id"]
        assert payload1["email"] != payload2["email"]
