"""
Database Session Management

Provides database session dependency for FastAPI and context manager
for scripts/tests. Uses connection pooling for production performance.

Example Usage:
    # In FastAPI endpoint:
    @app.get("/users")
    def get_users(session: Session = Depends(get_session)):
        users = session.exec(select(User)).all()
        return users

    # In scripts:
    with get_session_context() as session:
        user = User(name="Alice")
        session.add(user)
        # Auto-commits on context exit
"""

import os
from contextlib import contextmanager
from typing import Generator

from dotenv import load_dotenv
from sqlmodel import Session, create_engine

# Load environment variables (.env file is optional in production)
try:
    load_dotenv()
except Exception:
    # Ignore if .env file doesn't exist (production deployment)
    pass

# Get database URL from environment with Railway fallback
DATABASE_URL = (
    os.getenv("DATABASE_URL")
    or os.getenv("DB_URL")
    or os.getenv("POSTGRES_URL")
    or os.getenv("DATABASE_PRIVATE_URL")  # Railway sometimes uses this
)

if not DATABASE_URL:
    print("❌ No DATABASE_URL found in environment variables")
    print("Available environment variables:")
    for key in sorted(os.environ.keys()):
        if "URL" in key or "DATABASE" in key or "DB" in key or "POSTGRES" in key:
            print(f"  {key}={os.environ[key][:50]}...")
        else:
            print(f"  {key}")
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Please set DATABASE_URL in Railway environment variables."
    )

print(f"✅ Using database: {DATABASE_URL[:50]}...")

# Create SQLAlchemy engine with connection pooling
# For production with Neon Serverless PostgreSQL
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging in development
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=5,  # Number of persistent connections to maintain
    max_overflow=10,  # Allow up to 10 additional connections on demand
    pool_recycle=3600,  # Recycle connections after 1 hour
    connect_args={
        "connect_timeout": 10,  # Connection timeout in seconds
        "options": "-c timezone=utc",  # Use UTC timezone for all connections
    },
)


def get_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database sessions.

    Provides a SQLModel session for FastAPI routes. The session is
    automatically closed after the request completes.

    Yields:
        Session: SQLModel database session

    Example:
        @router.get("/tasks")
        def get_tasks(session: Session = Depends(get_session)):
            tasks = session.exec(select(Task)).all()
            return tasks
    """
    with Session(engine) as session:
        yield session


@contextmanager
def get_session_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions in scripts and tests.

    Provides a SQLModel session with automatic commit on success
    and rollback on exception. Use this for scripts, CLI tools,
    and tests that need database access outside of FastAPI.

    Yields:
        Session: SQLModel database session

    Example:
        with get_session_context() as session:
            task = Task(title="Write docs", description="...")
            session.add(task)
            session.commit()  # Manual commit
            # OR: Let context manager auto-commit on exit

        # Auto-rollback on exception:
        with get_session_context() as session:
            task = Task(title="Test")
            session.add(task)
            raise ValueError("Oops!")
            # Session is rolled back, task not saved
    """
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise


def init_db() -> None:
    """
    Initialize database tables.

    Creates all tables defined in SQLModel models. This is useful for
    testing and development. In production, use Alembic migrations instead.

    Note: This should only be called in development/testing environments.
    For production, use `alembic upgrade head` to apply migrations.

    Example:
        # In tests/conftest.py:
        from src.db.session import init_db
        init_db()  # Create all tables before running tests
    """
    from sqlmodel import SQLModel

    SQLModel.metadata.create_all(engine)


def check_connection() -> bool:
    """
    Check if database connection is working.

    Attempts to connect to the database and execute a simple query.
    Useful for health checks and startup validation.

    Returns:
        bool: True if connection successful, False otherwise

    Example:
        from src.db.session import check_connection

        if not check_connection():
            raise RuntimeError("Database connection failed!")
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
