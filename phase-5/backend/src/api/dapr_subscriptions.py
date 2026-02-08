"""
Dapr Subscription Endpoints

FastAPI endpoints that Dapr calls to deliver pub/sub messages.
Replaces the Kafka consumer polling mechanism with push-based delivery.

Endpoints:
- /dapr/subscribe: Returns list of subscriptions (Dapr discovery)
- /task-events: Handles task lifecycle events
- /reminders: Handles reminder events (for audit/consumer services)
"""

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Request, Response

from src.events.event_schemas import TaskEvent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dapr", tags=["dapr"])


# ================== SUBSCRIPTION DISCOVERY ==================


@router.get("/subscribe")
async def subscribe() -> List[Dict[str, str]]:
    """
    Dapr subscription discovery endpoint.

    Dapr calls this endpoint on startup to discover which topics
    this application subscribes to. Returns a list of subscription
    configurations.

    Returns:
        List of subscription configurations with pubsubname, topic, and route
    """
    subscriptions = [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events",
            "route": "/dapr/task-events",
        },
    ]

    logger.info(f"Dapr subscriptions registered: {[s['topic'] for s in subscriptions]}")
    return subscriptions


# ================== EVENT HANDLERS ==================


@router.post("/task-events")
async def handle_task_event(request: Request) -> Dict[str, str]:
    """
    Handle task events from Kafka (via Dapr pub/sub).

    Dapr publishes messages to this endpoint when events arrive on the
    'task-events' topic. Messages are wrapped in CloudEvents format.

    CloudEvents envelope format:
    {
        "specversion": "1.0",
        "source": "/todo-backend",
        "type": "task.created",
        "id": "unique-event-id",
        "time": "2024-01-01T00:00:00Z",
        "data": {
            "event_type": "task.created",
            "task_id": "...",
            "task_data": {...},
            "user_id": "...",
            "timestamp": "..."
        },
        "datacontenttype": "application/json"
    }

    Args:
        request: FastAPI request object

    Returns:
        Success response (200 OK acknowledges message)
    """
    try:
        # Parse CloudEvents envelope
        body = await request.json()
        logger.debug(f"Received Dapr event: {body.get('type', 'unknown')}")

        # Extract data from CloudEvents envelope
        # Dapr wraps Kafka messages in CloudEvents format
        if "data" in body:
            event_data = body["data"]
        else:
            # Fallback: message is not wrapped (shouldn't happen)
            event_data = body

        # Validate event
        task_event = TaskEvent.from_dict(event_data)
        logger.info(
            f"Processing {task_event.event_type} for task {task_event.task_id} "
            f"(user={task_event.user_id})"
        )

        # Route to appropriate handler based on event type
        if task_event.event_type == "task.created":
            await handle_task_created(task_event)
        elif task_event.event_type == "task.updated":
            await handle_task_updated(task_event)
        elif task_event.event_type == "task.completed":
            await handle_task_completed(task_event)
        elif task_event.event_type == "task.deleted":
            await handle_task_deleted(task_event)
        else:
            logger.warning(f"Unknown event type: {task_event.event_type}")

        # Return 200 OK to acknowledge message (commit offset)
        return {"status": "success", "event_type": task_event.event_type}

    except Exception as e:
        logger.error(f"Error processing task event: {e}", exc_info=True)
        # Return 500 to trigger retry (Dapr will redeliver)
        # Return 200 to skip invalid message (don't retry)
        # For transient errors, you might want to return 500
        # For malformed/invalid messages, return 200 to discard
        return Response(status_code=200)


# ================== EVENT HANDLERS ==================


async def handle_task_created(event: TaskEvent):
    """
    Handle task creation event.

    Args:
        event: Task event payload
    """
    logger.info(f"Task created: {event.task_id}")

    from src.services.dapr_client import get_dapr_client
    from src.events.dapr_publisher import get_event_publisher

    dapr_client = await get_dapr_client()

    # Update search index: cache task data in state store for fast lookups
    await dapr_client.save_state(
        store_name="postgres-statestore",
        key=f"task:{event.task_id}",
        value=event.task_data,
        metadata={"ttlInSeconds": "3600"},
    )

    # Publish audit log for analytics tracking
    publisher = await get_event_publisher()
    await publisher.publish_audit_log(
        event_type="audit.task.created",
        resource_type="task",
        resource_id=event.task_id,
        user_id=event.user_id,
        action="created",
        changes=event.task_data,
    )


async def handle_task_updated(event: TaskEvent):
    """
    Handle task update event.

    Args:
        event: Task event payload
    """
    logger.info(f"Task updated: {event.task_id}")

    from src.services.dapr_client import get_dapr_client
    from src.events.dapr_publisher import get_event_publisher

    dapr_client = await get_dapr_client()

    # Update search index: refresh cached task data
    await dapr_client.save_state(
        store_name="postgres-statestore",
        key=f"task:{event.task_id}",
        value=event.task_data,
        metadata={"ttlInSeconds": "3600"},
    )

    # Publish audit log for analytics tracking
    publisher = await get_event_publisher()
    await publisher.publish_audit_log(
        event_type="audit.task.updated",
        resource_type="task",
        resource_id=event.task_id,
        user_id=event.user_id,
        action="updated",
        changes=event.task_data,
    )


async def handle_task_completed(event: TaskEvent):
    """
    Handle task completion event.

    Args:
        event: Task event payload
    """
    logger.info(f"Task completed: {event.task_id}")

    from src.services.dapr_client import get_dapr_client
    from src.events.dapr_publisher import get_event_publisher

    dapr_client = await get_dapr_client()

    # Cache completion state for analytics and metrics
    await dapr_client.save_state(
        store_name="postgres-statestore",
        key=f"task:completed:{event.task_id}",
        value={
            "completed_at": event.timestamp.isoformat() if hasattr(event.timestamp, "isoformat") else str(event.timestamp),
            "user_id": event.user_id,
        },
        metadata={"ttlInSeconds": "86400"},  # Cache for 24 hours
    )

    # Publish audit log for completion analytics
    publisher = await get_event_publisher()
    await publisher.publish_audit_log(
        event_type="audit.task.completed",
        resource_type="task",
        resource_id=event.task_id,
        user_id=event.user_id,
        action="completed",
    )


async def handle_task_deleted(event: TaskEvent):
    """
    Handle task deletion event.

    Args:
        event: Task event payload
    """
    logger.info(f"Task deleted: {event.task_id}")

    from src.services.dapr_client import get_dapr_client
    from src.events.dapr_publisher import get_event_publisher

    dapr_client = await get_dapr_client()

    # Remove from search index: delete cached task data
    await dapr_client.delete_state(
        store_name="postgres-statestore",
        key=f"task:{event.task_id}",
    )

    # Clean up completion cache if it exists
    await dapr_client.delete_state(
        store_name="postgres-statestore",
        key=f"task:completed:{event.task_id}",
    )

    # Publish audit log for deletion tracking
    publisher = await get_event_publisher()
    await publisher.publish_audit_log(
        event_type="audit.task.deleted",
        resource_type="task",
        resource_id=event.task_id,
        user_id=event.user_id,
        action="deleted",
    )
