"""
Recurring Task Service (Phase V - Complete)

Microservice for processing recurring task events with full database integration.
Subscribes to 'task-events' Kafka topic via Dapr pub/sub and
spawns next task instance when a recurring task is completed.
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import asyncpg
from croniter import croniter
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Recurring Task Service",
    description="Processes recurring task events and spawns next instances",
    version="1.0.0",
)

# Database connection pool
db_pool: Optional[asyncpg.Pool] = None


# ================== MODELS ==================


class TaskEvent(BaseModel):
    """Task event from Kafka"""

    event_type: str  # task.created, task.updated, task.completed, task.deleted
    task_id: str
    task_data: Dict[str, Any]
    user_id: str
    timestamp: str  # ISO datetime
    metadata: Dict[str, Any] = {}


class DaprSubscription(BaseModel):
    """Dapr subscription configuration"""

    pubsubname: str
    topic: str
    route: str


# ================== DATABASE FUNCTIONS ==================


async def init_db():
    """Initialize database connection pool."""
    global db_pool

    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://todo_user:todo_password@localhost:5432/todo_db",
    )

    db_pool = await asyncpg.create_pool(
        database_url,
        min_size=2,
        max_size=10,
        command_timeout=60,
    )

    logger.info("Database connection pool initialized")


async def close_db():
    """Close database connection pool."""
    global db_pool

    if db_pool:
        await db_pool.close()
        logger.info("Database connection pool closed")


async def get_recurring_config(task_id: str) -> Optional[Dict[str, Any]]:
    """
    Get recurring configuration for a task.

    Args:
        task_id: Task ID to look up

    Returns:
        Recurring task configuration dict or None if not found
    """
    if not db_pool:
        logger.warning("Database pool not initialized")
        return None

    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT id, task_id, frequency, interval, next_due_at,
                   cron_expression, is_active
            FROM recurring_tasks
            WHERE task_id = $1 AND is_active = TRUE
            """,
            task_id,
        )

        if row:
            return dict(row)
        return None


async def create_task(
    title: str,
    description: Optional[str],
    user_id: str,
) -> Dict[str, Any]:
    """
    Create a new task instance.

    Args:
        title: Task title
        description: Task description (optional)
        user_id: Owner user ID

    Returns:
        Created task dict
    """
    if not db_pool:
        raise RuntimeError("Database pool not initialized")

    async with db_pool.acquire() as conn:
        task_id = str(__import__("uuid").uuid4())
        now = datetime.utcnow()

        await conn.execute(
            """
            INSERT INTO tasks (id, title, description, is_complete,
                             user_id, created_at, updated_at)
            VALUES ($1, $2, $3, FALSE, $4, $5, $5)
            """,
            task_id,
            title,
            description,
            user_id,
            now,
        )

        # Fetch the created task
        row = await conn.fetchrow("SELECT * FROM tasks WHERE id = $1", task_id)

        return dict(row)


async def update_recurring_config(
    recurring_id: str,
    next_due_at: datetime,
) -> None:
    """
    Update recurring configuration with next due date.

    Args:
        recurring_id: Recurring task ID
        next_due_at: Next occurrence timestamp
    """
    if not db_pool:
        raise RuntimeError("Database pool not initialized")

    async with db_pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE recurring_tasks
            SET next_due_at = $1, updated_at = $2
            WHERE id = $3
            """,
            next_due_at,
            datetime.utcnow(),
            recurring_id,
        )


# ================== RECURRING TASK LOGIC ==================


def calculate_next_occurrence(
    frequency: str,
    interval: int,
    cron_expression: Optional[str],
    base_time: datetime,
) -> datetime:
    """
    Calculate next occurrence based on recurrence rules.

    Args:
        frequency: Recurrence type (daily, weekly, monthly, custom)
        interval: Interval multiplier
        cron_expression: Optional cron for custom frequency
        base_time: Starting point for calculation

    Returns:
        Next occurrence datetime
    """
    if frequency == "custom":
        if not cron_expression:
            raise ValueError("Cron expression required for custom frequency")

        try:
            cron = croniter(cron_expression, base_time)
            return cron.get_next(datetime)
        except Exception as e:
            raise ValueError(f"Invalid cron expression: {str(e)}")

    elif frequency == "daily":
        return base_time + timedelta(days=interval)

    elif frequency == "weekly":
        return base_time + timedelta(weeks=interval)

    elif frequency == "monthly":
        # Approximate monthly (30 days * interval)
        return base_time + timedelta(days=30 * interval)

    else:
        raise ValueError(f"Unsupported frequency: {frequency}")


async def process_completed_task(event: TaskEvent):
    """
    Process completed task and spawn next instance if recurring.

    Args:
        event: Task completion event from Kafka
    """
    task_id = event.task_id
    task_data = event.task_data
    user_id = event.user_id

    logger.info(f"Processing completed task {task_id} for user {user_id}")

    try:
        # Get recurring configuration
        recurring = await get_recurring_config(task_id)

        if not recurring:
            logger.info(f"Task {task_id} is not recurring - skipping")
            return

        logger.info(
            f"Task {task_id} is recurring (frequency={recurring['frequency']})"
        )

        # Calculate next occurrence
        next_due = calculate_next_occurrence(
            frequency=recurring["frequency"],
            interval=recurring["interval"],
            cron_expression=recurring.get("cron_expression"),
            base_time=datetime.utcnow(),
        )

        logger.info(f"Next occurrence: {next_due.isoformat()}")

        # Create new task instance
        new_task = await create_task(
            title=task_data.get("title", ""),
            description=task_data.get("description"),
            user_id=user_id,
        )

        logger.info(f"Created new task instance: {new_task['id']}")

        # Update recurring config with next due date
        await update_recurring_config(recurring["id"], next_due)

        logger.info(f"Updated recurring config: next_due_at={next_due.isoformat()}")

        # The Dapr publisher in the main backend handles task.created events
        # when new recurring instances are persisted to the database.

    except Exception as e:
        logger.error(f"Error processing recurring task {task_id}: {e}", exc_info=True)
        raise


# ================== DAPR PUB/SUB ENDPOINTS ==================


@app.get("/dapr/subscribe")
async def subscribe():
    """
    Dapr subscription endpoint.

    Returns list of topics this service subscribes to.
    """
    subscriptions = [
        DaprSubscription(
            pubsubname="kafka-pubsub",
            topic="task-events",
            route="/task-events",
        ).model_dump()
    ]
    logger.info(f"Returning subscriptions: {subscriptions}")
    return subscriptions


@app.post("/task-events")
async def handle_task_event(request: Request):
    """
    Handle task events from Kafka (via Dapr).

    Processes task.completed events for recurring tasks.
    """
    try:
        # Parse Dapr CloudEvent envelope
        body = await request.json()
        logger.info(f"Received task event: {body.get('type', 'unknown')}")

        # Extract data from CloudEvent
        if "data" in body:
            event_data = body["data"]
        else:
            event_data = body

        # Validate event
        task_event = TaskEvent(**event_data)

        # Only process task.completed events
        if task_event.event_type == "task.completed":
            await process_completed_task(task_event)
        else:
            logger.debug(f"Ignoring event type: {task_event.event_type}")

        # Return 200 OK to acknowledge message
        return {"status": "success", "event_type": task_event.event_type}

    except Exception as e:
        logger.error(f"Error processing task event: {e}", exc_info=True)
        # Return 500 to trigger retry for transient errors
        raise HTTPException(status_code=500, detail=str(e))


# ================== HEALTH ENDPOINTS ==================


@app.get("/health")
async def health():
    """Health check endpoint for Kubernetes liveness probe."""
    status = {"status": "healthy", "service": "recurring-task-service"}

    # Check database connection
    if db_pool:
        try:
            async with db_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            status["database"] = "connected"
        except Exception as e:
            status["database"] = f"error: {str(e)}"
            status["status"] = "unhealthy"
    else:
        status["database"] = "not_initialized"

    return status


@app.get("/health/ready")
async def readiness():
    """Readiness check endpoint for Kubernetes readiness probe."""
    if db_pool:
        return {"status": "ready", "service": "recurring-task-service"}
    return {"status": "not_ready", "service": "recurring-task-service"}


# ================== STARTUP/SHUTDOWN ==================


@app.on_event("startup")
async def startup_event():
    """Application startup tasks."""
    logger.info("Recurring task service starting up...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")

    # Initialize database connection
    await init_db()


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks."""
    logger.info("Recurring task service shutting down...")

    # Close database connection
    await close_db()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8002")),
        log_level="info",
    )
