"""
FastAPI Backend - Main Application Entry Point

Phase II Full-Stack Todo Application
"""

import logging
import os
import uuid
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlmodel import Session, select

from src.api import auth, chat, health, tags, tasks
from src.auth.dependencies import get_current_user
from src.db.session import get_session
from src.models.conversation import (
    Conversation,
    Message,
    MessageCreate,
)
from src.models.user import User
from src.services.agent_service import AgentService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """
    Middleware to force HTTPS in redirect responses.

    Railway's reverse proxy handles HTTPS but FastAPI's redirect_slashes
    generates HTTP redirect URLs. This middleware fixes the Location header.
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Log ALL responses for debugging
        logger.info(f"HTTPSRedirectMiddleware: {request.method} {request.url.path} → {response.status_code}")

        # Fix redirect Location headers to use HTTPS
        if response.status_code in (301, 302, 303, 307, 308):
            location = response.headers.get("location", "")
            logger.info(f"Redirect detected! Location header: {location}")
            if location.startswith("http://"):
                # Replace http:// with https://
                fixed_location = location.replace("http://", "https://", 1)
                response.headers["location"] = fixed_location
                logger.info(f"✅ Fixed redirect: {location} → {fixed_location}")
            else:
                logger.info(f"⚠️ Location already HTTPS or empty: {location}")

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add OWASP-recommended security headers.

    Headers added:
    - Strict-Transport-Security: Force HTTPS (HSTS)
    - X-Content-Type-Options: Prevent MIME-type sniffing
    - X-Frame-Options: Prevent clickjacking
    - Content-Security-Policy: Mitigate XSS attacks
    - X-XSS-Protection: Enable browser XSS protection
    - Referrer-Policy: Control referrer information
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # HSTS: Force HTTPS for 1 year (31536000 seconds)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Prevent MIME-type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking (deny iframe embedding)
        response.headers["X-Frame-Options"] = "DENY"

        # Content Security Policy - strict policy for API
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'"

        # Enable browser XSS protection (legacy, but still useful)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer policy - strict for security
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        return response


# Initialize limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Phase II Todo API",
    description="""
## Full-Stack Todo Application Backend

RESTful API for managing personal todo tasks with user authentication and authorization.

### Features

- **User Authentication**: Secure signup, login, and logout with JWT tokens
- **Task Management**: Complete CRUD operations for todo tasks
- **Authorization**: User-specific task ownership and access control
- **Security**: HttpOnly cookies, rate limiting, CORS protection
- **Pagination**: Efficient data retrieval with limit/offset pagination
- **Filtering**: Filter tasks by completion status

### Authentication

All protected endpoints require a valid JWT token in the `auth_token` HttpOnly cookie.
Tokens expire after 15 minutes and must be refreshed by re-authenticating.

### Rate Limiting

The login endpoint is rate-limited to 5 attempts per minute per IP address to prevent brute-force attacks.

### Error Handling

Standard HTTP status codes are used throughout:
- **200 OK**: Successful request
- **201 Created**: Resource created successfully
- **204 No Content**: Successful deletion
- **400 Bad Request**: Invalid input data
- **401 Unauthorized**: Missing or invalid authentication token
- **403 Forbidden**: Insufficient permissions (e.g., accessing another user's task)
- **404 Not Found**: Resource does not exist
- **422 Unprocessable Entity**: Request validation error
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Unexpected server error

### API Versioning

Current version: **v0.1.0**

All endpoints are prefixed with `/api/`.
    """,
    version="0.1.0",
    contact={
        "name": "Phase II Todo API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "authentication",
            "description": "User authentication endpoints (signup, login, logout, user info)",
        },
        {
            "name": "tasks",
            "description": "Task management endpoints (CRUD operations, filtering, pagination)",
        },
        {
            "name": "tags",
            "description": "Tag management endpoints (CRUD operations, task-tag associations)",
        },
        {
            "name": "chat",
            "description": "Chat and conversation endpoints with AI agent integration",
        },
        {
            "name": "health",
            "description": "Health check and monitoring endpoints",
        },
    ],
    redirect_slashes=False,  # Disable automatic trailing slash redirects (breaks CORS)
)

# CORS Configuration from environment variables
# Strip whitespace from each origin to handle potential config issues
CORS_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")]

# Log CORS origins for debugging
logger.info(f"CORS Origins configured: {CORS_ORIGINS}")

# Add HTTPS redirect middleware (MUST be first to fix Railway proxy redirects)
app.add_middleware(HTTPSRedirectMiddleware)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# TrustedHostMiddleware disabled for Railway deployment
# Railway provides its own host validation at the load balancer level

# Add rate limiting handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Global exception handler for unhandled errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for catching all unhandled exceptions.

    This handler:
    1. Logs the error details (method, URL, exception type, traceback)
    2. Generates a unique error ID (UUID) for correlation and debugging
    3. Returns a generic error response to the client (no internal details exposed)

    Args:
        request: The FastAPI request object
        exc: The unhandled exception

    Returns:
        JSONResponse with 500 status code and safe error details
    """
    # Generate unique error ID for tracking
    error_id = str(uuid.uuid4())

    # Log comprehensive error details for debugging
    logger.error(
        f"Unhandled exception [error_id={error_id}] | "
        f"Method: {request.method} | "
        f"URL: {request.url.path} | "
        f"Exception: {type(exc).__name__}: {str(exc)}",
        exc_info=True,  # Include full traceback
    )

    # Return safe error response to client (no sensitive information)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_id": error_id,
        },
    )


# Include routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(tags.router)
app.include_router(chat.router)


@app.post("/api/{user_id}/chat", response_model=dict, status_code=status.HTTP_200_OK, tags=["chat"])
async def chat(
    user_id: str,
    req: MessageCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Send a chat message and get AI assistant response.

    This endpoint provides a simplified chat interface that automatically
    handles conversation creation and management. Users can provide a
    conversation_id to continue an existing conversation, or omit it to
    create a new conversation.

    Args:
        user_id: UUID of the user (must match authenticated user)
        req: MessageCreate with user message content and optional conversation_id
        current_user: Authenticated user
        session: Database session

    Returns:
        Dictionary with conversation_id, message_id, content, tool_calls, and created_at

    Raises:
        403: user_id doesn't match authenticated user
        500: Agent processing failed
    """
    try:
        # Verify user_id matches current_user.id (Better Auth uses string IDs)
        if user_id != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this resource",
            )

        # Get or create conversation
        if req.conversation_id:
            # Use existing conversation
            conversation = session.get(Conversation, req.conversation_id)

            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found",
                )

            if conversation.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to access this conversation",
                )
        else:
            # Create new conversation
            conversation = Conversation(
                user_id=current_user.id,
                title=None,  # Auto-generated from first message
            )
            session.add(conversation)
            session.commit()
            session.refresh(conversation)

        # Store user message
        user_message = Message(
            conversation_id=conversation.id,
            user_id=current_user.id,
            role="user",
            content=req.content,
        )

        session.add(user_message)
        session.commit()
        session.refresh(user_message)

        # Retrieve conversation history (last 20 messages for context)
        history_query = (
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.asc())
            .limit(20)
        )
        history_messages = session.exec(history_query).all()

        # Format history for API
        conversation_history = [
            {"role": msg.role, "content": msg.content} for msg in history_messages
        ]

        # Process message through agent
        agent_service = AgentService(session)
        agent_result = await agent_service.process_user_message(
            user_id=str(current_user.id),
            user_message=req.content,
            conversation_history=conversation_history,
        )

        if not agent_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=agent_result.get("error", "Agent processing failed"),
            )

        # Store assistant message
        assistant_message = Message(
            conversation_id=conversation.id,
            user_id=current_user.id,
            role="assistant",
            content=agent_result["assistant_message"],
            tool_calls=agent_service.format_tool_calls_for_storage(
                agent_result.get("tool_calls", [])
            ),
        )

        session.add(assistant_message)
        conversation.updated_at = conversation.updated_at  # Trigger update
        session.add(conversation)
        session.commit()

        return {
            "conversation_id": str(conversation.id),
            "message_id": str(assistant_message.id),
            "content": agent_result["assistant_message"],
            "tool_calls": agent_result.get("tool_calls", []),
            "created_at": assistant_message.created_at.isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}",
        )


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Phase II Todo API",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    from src.api.auth import AUTH_SERVER_URL
    return {
        "status": "healthy",
        "auth_server_url": AUTH_SERVER_URL,
        "commit": "05f5bd1"  # Latest: Add is_complete to TaskUpdate model
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
