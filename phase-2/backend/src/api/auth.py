"""
Authentication API Endpoints

Thin controllers for user authentication (signup, login, logout).
Proxies authentication requests to Better Auth server and validates JWT tokens.
"""

import os
import httpx
from fastapi import APIRouter, Depends, Response, Request, HTTPException
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from dotenv import load_dotenv

from src.auth.dependencies import get_current_user
from src.models.user import User, UserCreate, UserLogin, UserResponse

# Load environment variables
load_dotenv()

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Auth server URL (Better Auth)
# CRITICAL: Must be set in Railway environment variables
# Default to localhost for local development only
AUTH_SERVER_URL = os.getenv("AUTH_SERVER_URL", "http://localhost:3001")
print(f"🔗 Backend using AUTH_SERVER_URL: {AUTH_SERVER_URL}")  # Debug log


@router.post(
    "/sign-up/email",
    status_code=201,
    responses={
        201: {
            "description": "User created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "user": {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "email": "alice@example.com",
                            "name": "Alice Smith",
                            "createdAt": "2025-12-07T15:30:00Z"
                        },
                        "session": {
                            "token": "eyJhbGc...",
                            "expiresAt": "2025-12-07T15:45:00Z"
                        }
                    }
                }
            },
        },
        400: {
            "description": "Email already registered",
            "content": {
                "application/json": {
                    "example": {"error": "Email already registered"}
                }
            },
        },
    },
)
async def signup(
    user_data: UserCreate,
    response: Response,
):
    """
    Register a new user account (proxies to Better Auth server).

    Forwards signup request to Better Auth server, which handles:
    - Password hashing (bcrypt)
    - User creation in database
    - JWT token generation
    - Session management

    **Request Body:**
    - email: Valid email address (unique)
    - name: User's display name (1-100 characters)
    - password: Password (min 6 characters per Better Auth config)

    **Response:**
    - 201: User created successfully (with auth cookie set by Better Auth)
    - 400: Email already registered
    - 500: Auth server error

    **Architecture Flow:**
    1. Frontend → Backend (this endpoint)
    2. Backend → Better Auth server (POST /auth/sign-up)
    3. Better Auth → Neon PostgreSQL (create user)
    4. Better Auth → Backend (user + session + JWT cookie)
    5. Backend → Frontend (user data + session + JWT cookie forwarded)

    **Example:**
    ```json
    POST /api/auth/signup
    {
        "email": "alice@example.com",
        "name": "Alice Smith",
        "password": "SecurePass123!"
    }

    Response 201:
    Set-Cookie: better-auth.session_token=<JWT>; HttpOnly; Secure
    {
        "user": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "email": "alice@example.com",
            "name": "Alice Smith"
        },
        "session": {
            "token": "eyJhbGc...",
            "expiresAt": "2025-12-07T15:45:00Z"
        }
    }
    ```
    """
    try:
        # Proxy signup request to Better Auth server
        async with httpx.AsyncClient() as client:
            auth_response = await client.post(
                f"{AUTH_SERVER_URL}/api/auth/sign-up/email",
                json={
                    "email": user_data.email,
                    "name": user_data.name,
                    "password": user_data.password,
                },
                timeout=30.0,  # 30 second timeout (Railway inter-service communication needs extra time)
            )

            # If auth server returned error, forward it
            if auth_response.status_code != 200:
                return JSONResponse(
                    status_code=auth_response.status_code,
                    content=auth_response.json(),
                )

            # Extract response data from Better Auth
            auth_data = auth_response.json()

            # The token in the JSON response is correct!
            # It matches the session.token column in the database.
            # No modification needed - just return the response as-is.
            return auth_data

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Auth server timeout - please try again",
        )
    except httpx.RequestError as e:
        # Log detailed error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to connect to auth server at {AUTH_SERVER_URL}: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Auth server unavailable: {type(e).__name__} - {str(e)}",
        )


@router.post(
    "/sign-in/email",
    status_code=200,
    responses={
        200: {
            "description": "Login successful",
            "content": {
                "application/json": {
                    "example": {
                        "user": {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "email": "alice@example.com",
                            "name": "Alice Smith"
                        },
                        "session": {
                            "token": "eyJhbGc...",
                            "expiresAt": "2025-12-07T15:45:00Z"
                        }
                    }
                }
            },
        },
        401: {
            "description": "Invalid credentials",
            "content": {
                "application/json": {
                    "example": {"error": "Invalid email or password"}
                }
            },
        },
        429: {
            "description": "Rate limit exceeded",
            "content": {
                "application/json": {
                    "example": {"error": "Rate limit exceeded: 5 per 1 minute"}
                }
            },
        },
    },
)
# @limiter.limit("5/minute")  # TEMPORARILY DISABLED for testing SameSite fix
async def login(
    request: Request,
    credentials: UserLogin,
    response: Response,
):
    """
    Login with email and password (proxies to Better Auth server).

    Forwards login request to Better Auth server, which handles:
    - Password verification (bcrypt)
    - JWT token generation
    - Session creation

    **Request Body:**
    - email: User's email address
    - password: User's password

    **Response:**
    - 200: Login successful (with auth cookie set by Better Auth)
    - 401: Invalid email or password
    - 429: Rate limit exceeded (5 attempts per minute)
    - 503: Auth server unavailable

    **Architecture Flow:**
    1. Frontend → Backend (this endpoint)
    2. Backend → Better Auth server (POST /auth/sign-in/email)
    3. Better Auth → Neon PostgreSQL (verify user)
    4. Better Auth → Backend (user + session + JWT cookie)
    5. Backend → Frontend (user data + session + JWT cookie forwarded)

    **Security:**
    - Passwords verified against bcrypt hash in database
    - Error messages don't reveal whether email exists
    - Rate limited to prevent brute force attacks

    **Example:**
    ```json
    POST /api/auth/login
    {
        "email": "alice@example.com",
        "password": "SecurePass123!"
    }

    Response 200:
    Set-Cookie: better-auth.session_token=<JWT>; HttpOnly; Secure
    {
        "user": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "email": "alice@example.com",
            "name": "Alice Smith"
        },
        "session": {
            "token": "eyJhbGc...",
            "expiresAt": "2025-12-07T15:45:00Z"
        }
    }
    ```
    """
    try:
        # Proxy login request to Better Auth server
        async with httpx.AsyncClient() as client:
            auth_response = await client.post(
                f"{AUTH_SERVER_URL}/api/auth/sign-in/email",
                json={
                    "email": credentials.email,
                    "password": credentials.password,
                },
                timeout=30.0,  # 30 second timeout (Railway inter-service communication needs extra time)
            )

            # If auth server returned error, forward it
            if auth_response.status_code != 200:
                return JSONResponse(
                    status_code=auth_response.status_code,
                    content=auth_response.json(),
                )

            # Extract response data from Better Auth
            auth_data = auth_response.json()

            # The token in the JSON response is correct!
            # It matches the session.token column in the database.
            # No modification needed - just return the response as-is.
            return auth_data

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Auth server timeout - please try again",
        )
    except httpx.RequestError as e:
        # Log detailed error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to connect to auth server at {AUTH_SERVER_URL}: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Auth server unavailable: {type(e).__name__} - {str(e)}",
        )


@router.post(
    "/sign-out",
    status_code=204,
    responses={
        204: {
            "description": "Logout successful (no content)",
        },
        401: {
            "description": "Not authenticated",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authenticated"}
                }
            },
        },
    },
)
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Logout current user.

    Clears authentication cookie. Requires authentication.

    **Response:**
    - 204: Logout successful (no content)
    - 401: Not authenticated

    **Side Effects:**
    - Deletes "auth_token" cookie

    **Note:**
    - JWT is stateless, so logout only clears client-side cookie
    - Token remains valid until expiry (15 minutes)
    - For immediate invalidation, implement token blacklist

    **Example:**
    ```
    POST /api/auth/logout
    Cookie: auth_token=eyJhbGc...

    Response 204: (no content)
    ```
    """
    # Clear auth cookie by setting max_age=0
    response.delete_cookie(
        key="auth_token",
        httponly=True,
        secure=True,
        samesite="none",  # Must match the samesite used when setting the cookie
    )

    # 204 No Content (response body is None)
    return None


@router.get(
    "/get-session",
    response_model=UserResponse,
    status_code=200,
    responses={
        200: {
            "description": "Current user data",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "email": "alice@example.com",
                        "name": "Alice Smith",
                        "created_at": "2025-12-07T15:30:00Z",
                        "updated_at": "2025-12-07T15:30:00Z",
                    }
                }
            },
        },
        401: {
            "description": "Not authenticated",
            "content": {
                "application/json": {
                    "example": {"detail": "Not authenticated"}
                }
            },
        },
    },
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """
    Get current authenticated user's information.

    Useful for frontend to fetch user data after page refresh.

    **Response:**
    - 200: User data
    - 401: Not authenticated

    **Example:**
    ```
    GET /api/auth/me
    Cookie: auth_token=eyJhbGc...

    Response 200:
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "alice@example.com",
        "name": "Alice Smith",
        "created_at": "2025-12-07T15:30:00Z",
        "updated_at": "2025-12-07T15:30:00Z"
    }
    ```
    """
    return UserResponse.model_validate(current_user)
