# Data Model: Phase II Full-Stack Web Application

**Feature**: 004-phase-2-web-app
**Date**: 2025-12-06
**Purpose**: Define database schema and data models for user authentication and task management

## Overview

This document specifies the data models for Phase II using SQLModel (combining SQLAlchemy ORM + Pydantic validation). All models serve dual purpose: database schema definition and API request/response validation.

---

## Entity Relationship Diagram

```
┌─────────────────┐                ┌─────────────────┐
│      User       │                │      Task       │
├─────────────────┤                ├─────────────────┤
│ id (UUID, PK)   │1──────────────*│ id (UUID, PK)   │
│ email (UNIQUE)  │                │ title           │
│ name            │                │ description     │
│ hashed_password │                │ is_complete     │
│ created_at      │                │ user_id (FK)    │
│ updated_at      │                │ created_at      │
└─────────────────┘                │ updated_at      │
                                   └─────────────────┘

Relationship: One User has many Tasks (1:N)
Foreign Key: Task.user_id → User.id (ON DELETE CASCADE)
```

---

## User Model

### Purpose
Represents a registered application user with authentication credentials.

### Schema

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid

class User(SQLModel, table=True):
    """
    User account model for authentication and task ownership.

    Attributes:
        id: Unique identifier (UUID v4)
        email: Unique email address for login
        name: User's display name
        hashed_password: bcrypt/argon2 hashed password (never store plaintext)
        created_at: Account creation timestamp
        updated_at: Last modification timestamp
    """
    id: uuid.UUID = Field(
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
    name: str = Field(
        max_length=100,
        description="User's display name"
    )
    hashed_password: str = Field(
        description="Hashed password (bcrypt/argon2)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Account creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
```

### Constraints
- **Primary Key**: `id` (UUID)
- **Unique Constraint**: `email` (prevent duplicate accounts)
- **Index**: `email` (fast lookup for login)
- **NOT NULL**: All fields except none explicitly marked nullable
- **Max Length**: `email` (255), `name` (100)

### Validation Rules
- **Email**: Must match email regex pattern (RFC 5322)
- **Name**: 1-100 characters, no special validation
- **Password** (at signup): Minimum 8 characters, at least one letter and one number (validated before hashing)

### Security Notes
- **Never expose** `hashed_password` in API responses
- **Use bcrypt or argon2** for password hashing (min 12 rounds for bcrypt)
- **Validate email uniqueness** before account creation (handle race conditions)

---

## Task Model

### Purpose
Represents a todo task owned by a user.

### Schema

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid

class Task(SQLModel, table=True):
    """
    Task model for todo items with user ownership.

    Attributes:
        id: Unique identifier (UUID v4)
        title: Task title (required, 1-200 characters)
        description: Optional detailed description
        is_complete: Completion status (default: False)
        user_id: Foreign key to User (owner)
        created_at: Task creation timestamp
        updated_at: Last modification timestamp
    """
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique task identifier"
    )
    title: str = Field(
        min_length=1,
        max_length=200,
        index=True,
        description="Task title"
    )
    description: str | None = Field(
        default=None,
        max_length=2000,
        description="Optional task description"
    )
    is_complete: bool = Field(
        default=False,
        description="Task completion status"
    )
    user_id: uuid.UUID = Field(
        foreign_key="user.id",
        description="Owner user ID"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Task creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
```

### Constraints
- **Primary Key**: `id` (UUID)
- **Foreign Key**: `user_id` → `user.id` (ON DELETE CASCADE)
- **Index**: `title` (for search/filtering), `user_id` (for fast user-task queries)
- **NOT NULL**: `id`, `title`, `is_complete`, `user_id`, `created_at`, `updated_at`
- **Max Length**: `title` (200), `description` (2000)

### Validation Rules
- **Title**: 1-200 characters (trim whitespace)
- **Description**: 0-2000 characters (optional)
- **is_complete**: Boolean only (true/false)

### Business Logic
- **Ownership**: Tasks always belong to exactly one user
- **Cascade Delete**: When a user is deleted, all their tasks are automatically deleted
- **Update Timestamp**: `updated_at` should be updated on every modification (handled by service layer or DB trigger)

---

## API Request/Response Models

### User Models

```python
# Request Models (Pydantic)
class UserSignup(BaseModel):
    """Request body for user signup"""
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr  # Pydantic email validation
    password: str = Field(min_length=8, max_length=100)

class UserLogin(BaseModel):
    """Request body for user login"""
    email: EmailStr
    password: str

# Response Models (Pydantic)
class UserResponse(BaseModel):
    """Public user data (excludes hashed_password)"""
    id: uuid.UUID
    email: str
    name: str
    created_at: datetime

    class Config:
        from_attributes = True  # Allow ORM model conversion
```

### Task Models

```python
# Request Models (Pydantic)
class TaskCreate(BaseModel):
    """Request body for creating a task"""
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)

class TaskUpdate(BaseModel):
    """Request body for updating a task (all fields optional)"""
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)

class TaskToggleComplete(BaseModel):
    """Request body for toggling completion status"""
    is_complete: bool

# Response Models (Pydantic)
class TaskResponse(BaseModel):
    """Task data for API responses"""
    id: uuid.UUID
    title: str
    description: str | None
    is_complete: bool
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Allow ORM model conversion
```

---

## Database Migrations (Alembic)

### Initial Migration

```python
# alembic/versions/001_initial_schema.py
def upgrade():
    # Create users table
    op.create_table(
        'user',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_user_email', 'user', ['email'])

    # Create tasks table
    op.create_table(
        'task',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.String(2000), nullable=True),
        sa.Column('is_complete', sa.Boolean(), default=False, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_task_title', 'task', ['title'])
    op.create_index('ix_task_user_id', 'task', ['user_id'])

def downgrade():
    op.drop_table('task')
    op.drop_table('user')
```

---

## Sample Data (for Testing)

```python
# Seed data for development/testing
sample_users = [
    User(
        id=uuid.uuid4(),
        email="alice@example.com",
        name="Alice Smith",
        hashed_password="$2b$12$...",  # bcrypt hash of "password123"
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    ),
    User(
        id=uuid.uuid4(),
        email="bob@example.com",
        name="Bob Johnson",
        hashed_password="$2b$12$...",  # bcrypt hash of "password123"
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
]

sample_tasks = [
    Task(
        id=uuid.uuid4(),
        title="Buy groceries",
        description="Milk, eggs, bread, coffee",
        is_complete=False,
        user_id=sample_users[0].id,  # Alice's task
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    ),
    Task(
        id=uuid.uuid4(),
        title="Finish hackathon project",
        description="Complete Phase II implementation",
        is_complete=False,
        user_id=sample_users[0].id,  # Alice's task
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    ),
    Task(
        id=uuid.uuid4(),
        title="Call dentist",
        description=None,
        is_complete=True,
        user_id=sample_users[1].id,  # Bob's task
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
]
```

---

## Query Patterns

### Common Queries

```python
# Get all tasks for a user (most common query)
tasks = session.exec(
    select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
).all()

# Get single task with ownership check
task = session.exec(
    select(Task).where(Task.id == task_id, Task.user_id == user_id)
).first()
if not task:
    raise HTTPException(status_code=404, detail="Task not found")

# Count incomplete tasks for a user
incomplete_count = session.exec(
    select(func.count(Task.id)).where(
        Task.user_id == user_id,
        Task.is_complete == False
    )
).one()

# Find user by email (for login)
user = session.exec(
    select(User).where(User.email == email)
).first()
```

---

## Performance Considerations

### Indexes
- `user.email`: Fast login lookups
- `task.user_id`: Fast user-task retrieval (most frequent query)
- `task.title`: Enable future search/filter features

### Query Optimization
- Use `select().where()` instead of `.all()` then filter in Python
- Avoid N+1 queries (currently no relationships loaded, so N+1 not applicable)
- Use database-level pagination for large task lists (LIMIT/OFFSET)

### Scalability Notes
- UUIDs prevent ID enumeration but are slightly larger than integers (16 bytes vs 4-8 bytes)
- For >1M tasks per user, consider partitioning tasks table by user_id
- Neon serverless pooling handles connection scaling automatically

---

## Security Considerations

### Data Protection
- **Never return hashed_password** in API responses (use UserResponse model)
- **Validate user_id** from JWT token matches task owner before operations
- **Sanitize inputs** to prevent SQL injection (SQLModel handles automatically)
- **Use HTTPS** for all API requests (cookies with Secure flag)

### Audit Trail
- `created_at` and `updated_at` provide basic audit trail
- For compliance-heavy applications, consider adding `created_by` and `updated_by` fields

---

## Future Extensions

### Potential Schema Additions
- **User Profile**: Avatar URL, bio, preferences (separate table or JSONB column)
- **Task Categories**: Tags or categories for task organization
- **Task Priority**: High/medium/low priority field
- **Task Due Date**: Optional deadline for tasks
- **Shared Tasks**: Many-to-many relationship for collaborative lists
- **Task Comments**: One-to-many relationship for task discussions

### Migration Strategy
- Use Alembic for all schema changes (never modify tables directly)
- Test migrations on staging database before production
- Include rollback steps in all migrations
- Version migrations with timestamps: `YYYYMMDD_HHMMSS_description.py`
