# Backend Development Guidelines (FastAPI / SQLModel)

**Project**: Phase II Full-Stack Todo Application - Backend
**Framework**: FastAPI 0.110+, Python 3.13+
**ORM**: SQLModel (SQLAlchemy + Pydantic)
**Database**: Neon Serverless PostgreSQL
**Authentication**: JWT tokens (HS256), Better Auth integration

---

## Directory Structure

```
backend/
├── src/
│   ├── main.py                 # FastAPI app entry point
│   ├── api/                    # API route handlers (thin controllers)
│   │   ├── __init__.py
│   │   ├── auth.py             # Signup, login, logout endpoints
│   │   └── tasks.py            # Task CRUD endpoints
│   ├── models/                 # SQLModel database models
│   │   ├── __init__.py
│   │   ├── user.py             # User model (SQLModel + Pydantic)
│   │   └── task.py             # Task model (SQLModel + Pydantic)
│   ├── services/               # Business logic (fat services)
│   │   ├── __init__.py
│   │   ├── auth_service.py     # Authentication logic
│   │   └── task_service.py     # Task operations, validation
│   ├── auth/                   # Authentication utilities
│   │   ├── __init__.py
│   │   ├── jwt.py              # JWT creation, validation
│   │   └── dependencies.py     # FastAPI auth dependencies
│   ├── db/                     # Database connection and migrations
│   │   ├── __init__.py
│   │   ├── session.py          # SQLModel session management
│   │   └── migrations/         # Alembic migration scripts
│   │       └── versions/       # Timestamped migrations
│   └── config.py               # Configuration (env vars, settings)
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures (test DB, client)
│   ├── unit/                   # Unit tests
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   └── test_auth.py
│   └── integration/            # Integration tests
│       ├── test_auth_api.py
│       └── test_tasks_api.py
├── pyproject.toml              # UV project config (dependencies)
├── .env.example                # Example environment variables
└── CLAUDE.md                   # This file
```

---

## Core Principles (Enforced by Constitution v2.0.0)

### 1. Thin Controllers, Fat Services

**Keep route handlers (controllers) thin** - delegate business logic to services:

```python
# ✅ GOOD: Thin controller delegates to service
from fastapi import APIRouter, Depends, HTTPException
from src.services.task_service import TaskService
from src.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.post("/", status_code=201)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    task_service: TaskService = Depends()
):
    """Create a new task for the authenticated user."""
    return await task_service.create_task(task_data, current_user.id)
```

```python
# ❌ BAD: Fat controller with business logic
@router.post("/", status_code=201)
async def create_task(task_data: TaskCreate, current_user: User = Depends(get_current_user)):
    # ❌ Business logic in controller!
    if not task_data.title or len(task_data.title) > 200:
        raise HTTPException(400, "Invalid title")

    task = Task(
        id=uuid.uuid4(),
        title=task_data.title,
        user_id=current_user.id,
        # ...
    )
    session.add(task)
    session.commit()
    return task
```

**Services contain business logic**:

```python
# services/task_service.py - Business logic lives here
class TaskService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    async def create_task(self, task_data: TaskCreate, user_id: UUID) -> Task:
        """Create a new task with validation and business rules."""
        # Validation
        if not task_data.title.strip():
            raise ValueError("Title cannot be empty")

        # Business logic
        task = Task(
            id=uuid.uuid4(),
            title=task_data.title.strip(),
            description=task_data.description,
            is_complete=False,
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task
```

### 2. SQLModel for Unified Models

**Use SQLModel for database models** (combines SQLAlchemy ORM + Pydantic validation):

```python
# ✅ GOOD: SQLModel unifies database and validation
from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid

class User(SQLModel, table=True):
    """User model - both database table and Pydantic schema."""
    id: UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique user identifier"
    )
    email: str = Field(
        unique=True,
        index=True,
        max_length=255,
        description="Unique email address"
    )
    name: str = Field(max_length=100, description="User's display name")
    hashed_password: str = Field(description="Hashed password (bcrypt/argon2)")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Account creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
```

**Separate request/response models** from database models:

```python
# ✅ GOOD: Separate Pydantic models for API
from pydantic import BaseModel, EmailStr

class UserSignup(BaseModel):
    """Request body for user signup."""
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)

class UserResponse(BaseModel):
    """Public user data (excludes hashed_password)."""
    id: UUID
    email: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True  # Allow ORM model conversion
```

### 3. Type Hints Everywhere

**Always use type hints** for function parameters, return values, and variables:

```python
# ✅ GOOD: Complete type annotations
from typing import Optional, List
from uuid import UUID

async def get_user_tasks(
    user_id: UUID,
    is_complete: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0
) -> List[Task]:
    """Get tasks for a user with optional filtering."""
    query = select(Task).where(Task.user_id == user_id)

    if is_complete is not None:
        query = query.where(Task.is_complete == is_complete)

    query = query.limit(limit).offset(offset).order_by(Task.created_at.desc())

    return session.exec(query).all()
```

```python
# ❌ BAD: Missing type hints
async def get_user_tasks(user_id, is_complete=None):  # ❌ No types!
    # ...
```

### 4. File Size Limit: 300 Lines

**Maximum 300 lines per file**. If a file exceeds this:

1. Extract functions to utility modules
2. Split large services into smaller, focused services
3. Move complex logic to separate helper modules

---

## Authentication Patterns

### JWT Token Generation and Validation

**Use python-jose or PyJWT** for JWT handling:

```python
# auth/jwt.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(user_id: UUID, email: str) -> str:
    """Create JWT access token with user claims."""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "user_id": str(user_id),
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    """Validate JWT token and return claims."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid token")

def hash_password(password: str) -> str:
    """Hash password with bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)
```

### FastAPI Dependency for Authentication

**Use dependency injection** for current user extraction:

```python
# auth/dependencies.py
from fastapi import Depends, HTTPException, Request
from src.auth.jwt import verify_token
from src.models.user import User
from src.db.session import get_session

async def get_current_user(
    request: Request,
    session: Session = Depends(get_session)
) -> User:
    """Extract current user from JWT token in HttpOnly cookie."""
    # Extract token from cookie
    token = request.cookies.get("auth_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Verify token and extract claims
    try:
        payload = verify_token(token)
        user_id = UUID(payload.get("user_id"))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Fetch user from database
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
```

**Usage in protected endpoints**:

```python
# ✅ GOOD: Dependency injection for authentication
@router.get("/api/tasks")
async def list_tasks(
    current_user: User = Depends(get_current_user),
    is_complete: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0
):
    """List all tasks for authenticated user."""
    # current_user is automatically extracted from JWT token
    tasks = await task_service.get_user_tasks(
        current_user.id, is_complete, limit, offset
    )
    return {"tasks": tasks, "total": len(tasks), "limit": limit, "offset": offset}
```

### Setting HttpOnly Cookies

**Set JWT tokens in HttpOnly cookies** to prevent XSS attacks:

```python
# api/auth.py
from fastapi import Response

@router.post("/api/auth/login")
async def login(
    credentials: UserLogin,
    response: Response,
    auth_service: AuthService = Depends()
):
    """Authenticate user and set JWT cookies."""
    user = await auth_service.authenticate(credentials.email, credentials.password)

    # Create tokens
    access_token = create_access_token(user.id, user.email)
    refresh_token = create_refresh_token(user.id)

    # Set HttpOnly cookies
    response.set_cookie(
        key="auth_token",
        value=access_token,
        httponly=True,
        secure=True,  # HTTPS only
        samesite="strict",
        max_age=15 * 60,  # 15 minutes
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=7 * 24 * 60 * 60,  # 7 days
    )

    return UserResponse.from_orm(user)
```

---

## Database Patterns

### Session Management

**Use context manager** for database sessions:

```python
# db/session.py
from sqlmodel import Session, create_engine
from contextlib import contextmanager

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

def get_session():
    """Dependency for FastAPI to get database session."""
    with Session(engine) as session:
        yield session

@contextmanager
def get_session_context():
    """Context manager for database sessions in scripts."""
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
```

### Query Optimization

**Use select() with filters** instead of loading all records:

```python
# ✅ GOOD: Database-level filtering
from sqlmodel import select

async def get_incomplete_tasks(user_id: UUID) -> List[Task]:
    """Get only incomplete tasks (database-level filter)."""
    query = select(Task).where(
        Task.user_id == user_id,
        Task.is_complete == False
    ).order_by(Task.created_at.desc())

    return session.exec(query).all()
```

```python
# ❌ BAD: Loading all tasks then filtering in Python
async def get_incomplete_tasks(user_id: UUID) -> List[Task]:
    """❌ Inefficient: loads all tasks then filters."""
    all_tasks = session.exec(select(Task).where(Task.user_id == user_id)).all()
    return [task for task in all_tasks if not task.is_complete]  # ❌ Filter in Python!
```

### Ownership Checks

**Always verify user owns resource** before operations:

```python
# ✅ GOOD: Ownership check before operation
async def get_task(task_id: UUID, user_id: UUID) -> Task:
    """Get task with ownership verification."""
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this task")

    return task
```

### Alembic Migrations

**Always use Alembic** for database schema changes:

```bash
# Generate migration after modifying SQLModel models
uv run alembic revision --autogenerate -m "Add priority field to tasks"

# Review generated migration in backend/src/db/migrations/versions/

# Apply migration
uv run alembic upgrade head

# Rollback if needed
uv run alembic downgrade -1
```

**Migration naming convention**:
- `YYYYMMDD_HHMMSS_description.py` (e.g., `20251206_143000_add_priority_field.py`)

---

## Error Handling

### Consistent Error Responses

**Use HTTPException with detail messages**:

```python
# ✅ GOOD: Clear, actionable error messages
from fastapi import HTTPException

@router.post("/api/tasks")
async def create_task(task_data: TaskCreate, current_user: User = Depends(get_current_user)):
    if not task_data.title.strip():
        raise HTTPException(
            status_code=400,
            detail="Title is required and cannot be empty"
        )

    if len(task_data.title) > 200:
        raise HTTPException(
            status_code=400,
            detail="Title must be 200 characters or less"
        )

    # ... create task
```

### Pydantic Validation Errors

**Let Pydantic handle validation** automatically:

```python
# ✅ GOOD: Pydantic validates automatically
from pydantic import BaseModel, Field, validator

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)

    @validator("title")
    def title_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip()
```

Pydantic will automatically return 422 Unprocessable Entity with validation errors:

```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "ensure this value has at most 200 characters",
      "type": "value_error.any_str.max_length"
    }
  ]
}
```

### Global Exception Handler

**Add global exception handler** for unexpected errors:

```python
# main.py
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all for unexpected errors."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

---

## CORS Configuration

**Configure CORS for frontend origins**:

```python
# main.py
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Get allowed origins from environment variable
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,  # Required for cookies
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)
```

**Environment variable** (`.env`):

```env
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

---

## Testing Patterns

### Fixtures for Test Database

**Use pytest fixtures** for test database and client:

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from src.main import app
from src.db.session import get_session

# In-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(TEST_DATABASE_URL, echo=False)

@pytest.fixture(scope="function")
def session():
    """Create fresh database for each test."""
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session
    SQLModel.metadata.drop_all(test_engine)

@pytest.fixture(scope="function")
def client(session):
    """TestClient with dependency override for database session."""
    def get_test_session():
        yield session

    app.dependency_overrides[get_session] = get_test_session
    yield TestClient(app)
    app.dependency_overrides.clear()
```

### Integration Tests for API Endpoints

**Test full request-response cycle**:

```python
# tests/integration/test_tasks_api.py
def test_create_task_authenticated(client, session):
    """Test creating a task with valid authentication."""
    # Create user and get auth token
    user = create_test_user(session, email="test@example.com")
    token = create_access_token(user.id, user.email)

    # Make request with auth cookie
    response = client.post(
        "/api/tasks",
        json={"title": "Test Task", "description": "Test Description"},
        cookies={"auth_token": token}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["user_id"] == str(user.id)
    assert data["is_complete"] is False

def test_create_task_unauthenticated(client):
    """Test creating a task without authentication returns 401."""
    response = client.post(
        "/api/tasks",
        json={"title": "Test Task"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
```

### Unit Tests for Services

**Test business logic in isolation**:

```python
# tests/unit/test_task_service.py
def test_task_service_validates_title_length():
    """Test service raises ValueError for title > 200 chars."""
    task_data = TaskCreate(title="a" * 201, description=None)

    with pytest.raises(ValueError, match="Title must be 200 characters or less"):
        task_service.create_task(task_data, user_id=UUID())
```

---

## Performance Optimization

### Database Connection Pooling

**Use connection pooling** for production (Neon handles this automatically):

```python
# db/session.py
from sqlmodel import create_engine

engine = create_engine(
    DATABASE_URL,
    echo=False,  # Disable SQL logging in production
    pool_size=5,  # Connection pool size
    max_overflow=10,  # Allow up to 10 overflow connections
    pool_pre_ping=True,  # Verify connections before use
)
```

### Query Optimization with Indexes

**Add indexes** to frequently queried columns:

```python
# ✅ GOOD: Index on user_id for fast task lookups
class Task(SQLModel, table=True):
    id: UUID = Field(primary_key=True)
    title: str = Field(index=True)  # Index for search
    user_id: UUID = Field(foreign_key="user.id", index=True)  # Index for user-task queries
```

### Pagination

**Always paginate** large result sets:

```python
# ✅ GOOD: Pagination with limit and offset
@router.get("/api/tasks")
async def list_tasks(
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100),  # Max 100 per page
    offset: int = Query(0, ge=0)
):
    """List tasks with pagination."""
    query = select(Task).where(Task.user_id == current_user.id)
    query = query.limit(limit).offset(offset).order_by(Task.created_at.desc())

    tasks = session.exec(query).all()
    total = session.exec(select(func.count(Task.id)).where(Task.user_id == current_user.id)).one()

    return {"tasks": tasks, "total": total, "limit": limit, "offset": offset}
```

---

## Security Best Practices

### Never Expose Hashed Passwords

**Exclude sensitive fields** from API responses:

```python
# ✅ GOOD: Response model excludes hashed_password
class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    created_at: datetime
    # ✅ hashed_password NOT included

    class Config:
        from_attributes = True
```

### Rate Limiting

**Add rate limiting** to prevent abuse:

```python
# Use slowapi for rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.post("/api/auth/login")
@limiter.limit("5/minute")  # 5 login attempts per minute
async def login(request: Request, credentials: UserLogin):
    # ...
```

### Input Validation

**Always validate and sanitize** user input:

```python
# ✅ GOOD: Pydantic validation + additional sanitization
from pydantic import validator

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)

    @validator("title", "description", pre=True)
    def sanitize_string(cls, v):
        if v is None:
            return v
        # Strip whitespace and prevent XSS
        return v.strip()
```

---

## Environment Variables

**Required environment variables** (`.env`):

```env
# Database
DATABASE_URL=postgresql://user:password@host.region.neon.tech/dbname?sslmode=require

# Authentication
JWT_SECRET=your-256-bit-random-secret  # openssl rand -hex 32
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Environment
ENVIRONMENT=development  # development | staging | production
```

**NEVER commit** `.env` to version control. Use `.env.example` for documentation.

---

## Common Pitfalls to Avoid

### ❌ Don't Put Business Logic in Controllers

```python
# ❌ BAD: Business logic in route handler
@router.post("/api/tasks")
async def create_task(task_data: TaskCreate):
    # ❌ Validation, database operations in controller!
    if not task_data.title:
        raise HTTPException(400, "Title required")
    task = Task(...)
    session.add(task)
    session.commit()
```

### ❌ Don't Return Database Models Directly

```python
# ❌ BAD: Returning SQLModel directly (exposes hashed_password!)
@router.get("/api/users/{user_id}")
async def get_user(user_id: UUID):
    user = session.get(User, user_id)
    return user  # ❌ Includes hashed_password!

# ✅ GOOD: Return Pydantic response model
@router.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID):
    user = session.get(User, user_id)
    return UserResponse.from_orm(user)  # ✅ Only safe fields
```

### ❌ Don't Skip Ownership Checks

```python
# ❌ BAD: No ownership verification!
@router.delete("/api/tasks/{task_id}")
async def delete_task(task_id: UUID):
    task = session.get(Task, task_id)
    session.delete(task)  # ❌ Any user can delete any task!

# ✅ GOOD: Verify ownership before deletion
@router.delete("/api/tasks/{task_id}", status_code=204)
async def delete_task(task_id: UUID, current_user: User = Depends(get_current_user)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    if task.user_id != current_user.id:
        raise HTTPException(403, "Not authorized")
    session.delete(task)
    session.commit()
```

---

## Quick Reference

| Task | Command |
|------|---------|
| **Start dev server** | `uv run uvicorn src.main:app --reload` |
| **Run tests** | `uv run pytest` |
| **Run with coverage** | `uv run pytest --cov=src` |
| **Generate migration** | `uv run alembic revision --autogenerate -m "description"` |
| **Apply migrations** | `uv run alembic upgrade head` |
| **Rollback migration** | `uv run alembic downgrade -1` |
| **Lint code** | `uv run ruff check src/` |
| **Format code** | `uv run ruff format src/` |

---

## Additional Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLModel Docs**: https://sqlmodel.tiangolo.com/
- **Pydantic Docs**: https://docs.pydantic.dev/
- **Alembic Docs**: https://alembic.sqlalchemy.org/
- **python-jose Docs**: https://python-jose.readthedocs.io/
- **Passlib Docs**: https://passlib.readthedocs.io/

For project-specific architecture, see:
- [Specification](../specs/004-phase-2-web-app/spec.md)
- [Implementation Plan](../specs/004-phase-2-web-app/plan.md)
- [API Contracts](../specs/004-phase-2-web-app/contracts/)
- [Data Model](../specs/004-phase-2-web-app/data-model.md)
