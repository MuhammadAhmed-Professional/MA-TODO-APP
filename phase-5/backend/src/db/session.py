"""
Database Session Management (Phase V)

SQLModel session configuration for PostgreSQL connection.
Uses environment variables for database configuration.
"""

import os
from contextlib import contextmanager
from typing import Generator

from sqlmodel import Session, create_engine

# Database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://todo_user:todo_password@localhost:5432/todo_db",
)

# Create database engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging in development
    pool_pre_ping=True,  # Verify connections before use
    pool_size=5,  # Connection pool size
    max_overflow=10,  # Allow up to 10 overflow connections
)


def get_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database session.

    Usage in route handlers:
        @router.get("/api/tasks")
        async def list_tasks(session: Session = Depends(get_session)):
            ...
    """
    with Session(engine) as session:
        yield session


@contextmanager
def get_session_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions in scripts and background tasks.

    Usage:
        with get_session_context() as session:
            task = session.get(Task, task_id)
            ...
            session.commit()
    """
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise


def init_db():
    """
    Initialize database tables.

    Call this on application startup to create all tables.
    For production, use Alembic migrations instead.
    """
    from src.models.advanced_task import (
        RecurringTask,
        TaskCategory,
        TaskReminder,
    )
    from src.models.task import Task

    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    # Initialize database when run directly
    init_db()
    print("Database tables created successfully!")
