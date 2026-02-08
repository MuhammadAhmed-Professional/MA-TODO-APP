"""
Recurring Task Service (Enhanced with Dapr)

Microservice for processing recurring task events with Dapr integration:
- Subscribes to 'task-events' Kafka topic via Dapr pub/sub
- Spawns next task instance when recurring task completed
- Uses Dapr service invocation to call backend API
- Stores processing state in Dapr state store
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

import httpx
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
    description="Processes recurring task events with Dapr",
    version="2.0.0",
)

# Dapr configuration
DAPR_HTTP_PORT = int(os.getenv("DAPR_HTTP_PORT", 3500))
DAPR_STATE_STORE = "postgres-statestore"
DAPR_PUBSUB = "kafka-pubsub"
BACKEND_APP_ID = "todo-backend"

# HTTP client for Dapr API
dapr_client = httpx.AsyncClient(timeout=30.0)


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


class ProcessingState(BaseModel):
    """Recurring task processing state"""

    task_id: str
    status: str  # pending, processing, completed, failed
    next_task_id: Optional[str] = None
    created_at: str
    updated_at: str
    error_message: Optional[str] = None


# ================== DAPR STATE MANAGEMENT ==================


async def get_processing_state(task_id: str) -> Optional[ProcessingState]:
    """
    Get processing state from Dapr state store.

    Args:
        task_id: Task ID

    Returns:
        Processing state or None
    """
    try:
        response = await dapr_client.get(
            f"http://localhost:{DAPR_HTTP_PORT}/v1.0/state/{DAPR_STATE_STORE}/recurring-processing:{task_id}"
        )

        if response.status_code == 200:
            data = response.json()
            return ProcessingState(**data)
        else:
            return None

    except Exception as e:
        logger.error(f"Error getting processing state: {e}")
        return None


async def save_processing_state(state: ProcessingState) -> bool:
    """
    Save processing state to Dapr state store.

    Args:
        state: Processing state

    Returns:
        True if save succeeded
    """
    try:
        response = await dapr_client.post(
            f"http://localhost:{DAPR_HTTP_PORT}/v1.0/state/{DAPR_STATE_STORE}",
            json=[
                {
                    "key": f"recurring-processing:{state.task_id}",
                    "value": state.model_dump(),
                    "metadata": {"ttlInSeconds": "3600"},  # 1 hour
                }
            ],
        )

        return response.status_code == 204

    except Exception as e:
        logger.error(f"Error saving processing state: {e}")
        return False


async def invoke_backend(
    method: str,
    data: Dict[str, Any],
    http_verb: str = "POST",
) -> Optional[Dict[str, Any]]:
    """
    Invoke backend service via Dapr service invocation.

    Args:
        method: Backend method/route
        data: Request payload
        http_verb: HTTP verb

    Returns:
        Response data or None
    """
    try:
        url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/invoke/{BACKEND_APP_ID}/method/{method}"

        if http_verb.upper() == "GET":
            response = await dapr_client.get(url, params=data)
        elif http_verb.upper() == "POST":
            response = await dapr_client.post(url, json=data)
        elif http_verb.upper() == "PUT":
            response = await dapr_client.put(url, json=data)
        elif http_verb.upper() == "DELETE":
            response = await dapr_client.delete(url)
        else:
            logger.error(f"Unsupported HTTP verb: {http_verb}")
            return None

        if response.status_code < 400:
            return response.json() if response.text else {}
        else:
            logger.error(f"Backend invocation failed: {response.status_code} {response.text}")
            return None

    except Exception as e:
        logger.error(f"Error invoking backend: {e}")
        return None


# ================== DAPR PUB/SUB ENDPOINTS ==================


@app.get("/dapr/subscribe")
async def subscribe():
    """
    Dapr subscription endpoint.

    Returns list of topics this service subscribes to.
    """
    subscriptions = [
        DaprSubscription(
            pubsubname=DAPR_PUBSUB,
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
    Uses state store to track processing and prevent duplicates.
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
        if task_event.event_type != "task.completed":
            logger.debug(f"Ignoring event type: {task_event.event_type}")
            return {"status": "ignored", "event_type": task_event.event_type}

        # Check if already processed (idempotency)
        existing_state = await get_processing_state(task_event.task_id)
        if existing_state and existing_state.status == "completed":
            logger.info(f"Task {task_event.task_id} already processed - skipping")
            return {"status": "already_processed", "task_id": task_event.task_id}

        # Process completed task
        await process_completed_task(task_event)

        # Return 200 OK to acknowledge message
        return {"status": "success", "event_type": task_event.event_type}

    except Exception as e:
        logger.error(f"Error processing task event: {e}", exc_info=True)
        # Return 500 to trigger retry
        raise HTTPException(status_code=500, detail=str(e))


# ================== RECURRING TASK LOGIC ==================


async def process_completed_task(event: TaskEvent):
    """
    Process completed task and spawn next instance if recurring.

    Uses Dapr service invocation to call backend API for:
    1. Checking if task is recurring
    2. Creating new task instance
    3. Updating recurring configuration

    Args:
        event: Task completion event
    """
    task_id = event.task_id
    task_data = event.task_data
    user_id = event.user_id

    logger.info(f"Processing completed task {task_id} for user {user_id}")

    # Update processing state
    state = ProcessingState(
        task_id=task_id,
        status="processing",
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat(),
    )
    await save_processing_state(state)

    try:
        # Check if task is recurring via backend API
        recurring_config = await invoke_backend(
            method=f"api/recurring/{task_id}",
            data={"user_id": user_id},
            http_verb="GET",
        )

        if not recurring_config or not recurring_config.get("is_active"):
            logger.info(f"Task {task_id} is not recurring - skipping")

            # Update state
            state.status = "completed"
            state.updated_at = datetime.utcnow().isoformat()
            await save_processing_state(state)
            return

        logger.info(f"Task {task_id} is recurring - spawning next instance")

        # Spawn next task instance via backend API
        new_task = await invoke_backend(
            method=f"api/recurring/{task_id}/spawn",
            data={"user_id": user_id},
            http_verb="POST",
        )

        if new_task:
            new_task_id = new_task.get("id")
            logger.info(f"Spawned new task instance: {new_task_id} from completed task {task_id}")

            # Update state
            state.status = "completed"
            state.next_task_id = new_task_id
            state.updated_at = datetime.utcnow().isoformat()
        else:
            logger.warning(f"Failed to spawn next instance for task {task_id}")
            state.status = "failed"
            state.error_message = "Failed to spawn next instance"

        await save_processing_state(state)

    except Exception as e:
        logger.error(f"Error processing recurring task {task_id}: {e}", exc_info=True)

        # Update state with error
        state.status = "failed"
        state.error_message = str(e)
        state.updated_at = datetime.utcnow().isoformat()
        await save_processing_state(state)

        raise


# ================== WEBHOOK ENDPOINTS ==================


@app.post("/api/tasks/created")
async def task_created_webhook(request: Request):
    """
    Webhook endpoint called by backend when a new task is created.

    Receives notification via Dapr service invocation from backend
    when a new recurring task instance is created.

    Args:
        request: FastAPI request

    Returns:
        Success response
    """
    try:
        data = await request.json()
        task_id = data.get("task_id")
        user_id = data.get("user_id")

        logger.info(f"Received task.created webhook: task_id={task_id}, user_id={user_id}")

        # New task events are handled by the Dapr subscription handlers
        # in the main backend (dapr_subscriptions.py) which update the
        # search index, cache, and publish audit logs automatically.

        return {"status": "success", "task_id": task_id}

    except Exception as e:
        logger.error(f"Error processing task.created webhook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ================== CRON BINDING ENDPOINTS ==================


@app.post("/api/jobs/process-recurring")
async def process_recurring_job(request: Request):
    """
    Dapr cron job callback endpoint.

    Triggered by Dapr cron binding (recurring-task-cron) every hour.
    Checks for recurring tasks that need new instances spawned.
    """
    try:
        body = await request.json()
        logger.info(f"Process recurring job triggered: {body}")

        # Query backend for due recurring tasks
        due_tasks = await invoke_backend(
            method="api/recurring/due",
            data={},
            http_verb="GET",
        )

        if due_tasks:
            logger.info(f"Found {len(due_tasks)} due recurring tasks")

            # Process each due task
            for task in due_tasks:
                task_id = task.get("task_id")
                user_id = task.get("user_id")

                logger.info(f"Processing due recurring task: {task_id}")

                # Spawn next instance
                new_task = await invoke_backend(
                    method=f"api/recurring/{task_id}/spawn",
                    data={"user_id": user_id},
                    http_verb="POST",
                )

                if new_task:
                    logger.info(f"Spawned task {new_task.get('id')} from recurring task {task_id}")

        logger.info("Recurring task processing job completed")
        return {"status": "success", "processed_count": len(due_tasks) if due_tasks else 0}

    except Exception as e:
        logger.error(f"Job execution error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ================== HEALTH ENDPOINTS ==================


@app.get("/health")
async def health():
    """Health check endpoint for Kubernetes liveness probe."""
    return {"status": "healthy", "service": "recurring-task-service", "version": "2.0.0"}


@app.get("/health/ready")
async def readiness():
    """Readiness check endpoint for Kubernetes readiness probe."""
    # Check if Dapr sidecar is accessible
    try:
        response = await dapr_client.get(f"http://localhost:{DAPR_HTTP_PORT}/v1.0/healthz")
        dapr_healthy = response.status_code == 200
    except:
        dapr_healthy = False

    return {
        "status": "ready" if dapr_healthy else "not_ready",
        "service": "recurring-task-service",
        "dapr_connected": dapr_healthy,
    }


# ================== STARTUP/SHUTDOWN ==================


@app.on_event("startup")
async def startup_event():
    """Application startup tasks."""
    logger.info("Recurring task service starting up...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Dapr HTTP port: {DAPR_HTTP_PORT}")
    logger.info(f"Backend app ID: {BACKEND_APP_ID}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks."""
    logger.info("Recurring task service shutting down...")
    await dapr_client.aclose()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8002)),
        log_level="info",
    )
