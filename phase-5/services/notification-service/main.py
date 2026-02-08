"""
Notification Service

Microservice for processing reminder notifications.
Subscribes to 'reminders' Kafka topic via Dapr pub/sub and
delivers notifications via email, push, or in-app methods.
"""

import json
import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict

import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Notification Service",
    description="Processes task reminder notifications",
    version="1.0.0",
)


# ================== MODELS ==================


class ReminderEvent(BaseModel):
    """Reminder event from Kafka"""

    reminder_id: str
    task_id: str
    task_title: str
    user_id: str
    remind_at: str  # ISO datetime
    notification_type: str  # email, push, in_app
    timestamp: str  # ISO datetime


class DaprSubscription(BaseModel):
    """Dapr subscription configuration"""

    pubsubname: str
    topic: str
    route: str


# ================== DAPR PUB/SUB ENDPOINTS ==================


@app.get("/dapr/subscribe")
async def subscribe():
    """
    Dapr subscription endpoint.

    Dapr calls this endpoint to discover topic subscriptions.
    Returns list of topics this service subscribes to.
    """
    subscriptions = [
        DaprSubscription(
            pubsubname="kafka-pubsub",
            topic="reminders",
            route="/reminders",
        ).model_dump()
    ]
    logger.info(f"Returning subscriptions: {subscriptions}")
    return subscriptions


@app.post("/reminders")
async def handle_reminder(request: Request):
    """
    Handle reminder notification events from Kafka (via Dapr).

    Dapr publishes messages to this endpoint when events arrive on 'reminders' topic.
    """
    try:
        # Parse Dapr CloudEvent envelope
        body = await request.json()
        logger.info(f"Received reminder event: {body}")

        # Extract data from CloudEvent (Dapr wraps Kafka messages in CloudEvent format)
        if "data" in body:
            event_data = body["data"]
        else:
            event_data = body

        # Validate event
        reminder = ReminderEvent(**event_data)

        # Process notification
        await send_notification(reminder)

        # Return 200 OK to acknowledge message
        return {"status": "success", "reminder_id": reminder.reminder_id}

    except Exception as e:
        logger.error(f"Error processing reminder: {e}", exc_info=True)
        # Return 200 to acknowledge (don't retry invalid messages)
        # For transient errors, return 500 to trigger retry
        raise HTTPException(status_code=500, detail=str(e))


# ================== NOTIFICATION LOGIC ==================


async def send_notification(reminder: ReminderEvent):
    """
    Send notification based on notification type.

    Args:
        reminder: Reminder event data
    """
    logger.info(
        f"Sending {reminder.notification_type} notification for task "
        f"'{reminder.task_title}' (user={reminder.user_id})"
    )

    if reminder.notification_type == "email":
        await send_email_notification(reminder)
    elif reminder.notification_type == "push":
        await send_push_notification(reminder)
    elif reminder.notification_type == "in_app":
        await send_in_app_notification(reminder)
    else:
        logger.warning(f"Unknown notification type: {reminder.notification_type}")


async def send_email_notification(reminder: ReminderEvent):
    """
    Send email notification.

    Logs a structured email payload. In production, replace the logger call
    with an actual email provider (SendGrid, AWS SES, etc.).
    """
    email_payload = {
        "from": "noreply@todo-app.example.com",
        "to": f"user-{reminder.user_id}@todo-app.example.com",
        "subject": f"Reminder: {reminder.task_title}",
        "body": (
            f"Hi,\n\n"
            f"This is a reminder for your task: '{reminder.task_title}'.\n"
            f"Scheduled reminder time: {reminder.remind_at}\n\n"
            f"-- Todo App Notification Service"
        ),
    }
    logger.info(
        f"[EMAIL] Sending email notification: {json.dumps(email_payload, indent=2)}"
    )
    logger.info(f"Email notification sent for reminder {reminder.reminder_id}")


async def send_push_notification(reminder: ReminderEvent):
    """
    Send push notification.

    Logs a structured push payload. In production, integrate with Firebase
    Cloud Messaging (FCM) or Apple Push Notification service (APNs).
    """
    push_payload = {
        "title": "Task Reminder",
        "body": f"{reminder.task_title} is due soon",
        "data": {
            "task_id": reminder.task_id,
            "reminder_id": reminder.reminder_id,
            "user_id": reminder.user_id,
        },
    }
    logger.info(
        f"[PUSH] Sending push notification: {json.dumps(push_payload, indent=2)}"
    )
    logger.info(f"Push notification sent for reminder {reminder.reminder_id}")


async def send_in_app_notification(reminder: ReminderEvent):
    """
    Send in-app notification.

    Stores the notification in the Dapr state store so the user sees it
    when they next visit the app.
    """
    logger.info(f"[IN-APP] Reminder for task: {reminder.task_title}")

    notification = {
        "id": str(uuid.uuid4()),
        "user_id": reminder.user_id,
        "type": "reminder",
        "title": "Task Reminder",
        "message": f"{reminder.task_title} is due soon",
        "task_id": reminder.task_id,
        "reminder_id": reminder.reminder_id,
        "created_at": datetime.utcnow().isoformat(),
        "is_read": False,
    }

    # Persist to Dapr state store for retrieval by the frontend
    dapr_port = int(os.getenv("DAPR_HTTP_PORT", "3500"))
    dapr_url = f"http://localhost:{dapr_port}/v1.0/state/postgres-statestore"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                dapr_url,
                json=[
                    {
                        "key": f"notification:{notification['id']}",
                        "value": notification,
                        "metadata": {"ttlInSeconds": "604800"},  # 7 days
                    }
                ],
            )
            if response.status_code == 204:
                logger.info(
                    f"In-app notification {notification['id']} saved to state store"
                )
            else:
                logger.warning(
                    f"Failed to save notification to state store: {response.status_code}"
                )
    except Exception as e:
        logger.warning(f"Dapr state store unavailable, notification logged only: {e}")

    logger.info(
        f"In-app notification created for reminder {reminder.reminder_id}: "
        f"{json.dumps(notification, indent=2)}"
    )


# ================== HEALTH ENDPOINTS ==================


@app.get("/health")
async def health():
    """Health check endpoint for Kubernetes liveness probe."""
    return {"status": "healthy", "service": "notification-service"}


@app.get("/health/ready")
async def readiness():
    """Readiness check endpoint for Kubernetes readiness probe."""
    # Check if service is ready to accept traffic
    # Example: verify Kafka connection, database connection, etc.
    return {"status": "ready", "service": "notification-service"}


# ================== JOB CALLBACK ENDPOINT (for Dapr Jobs) ==================


@app.post("/api/jobs/trigger")
async def job_trigger(request: Request):
    """
    Dapr job callback endpoint.

    Dapr can schedule jobs (cron-like tasks) that call this endpoint.
    Use this for periodic tasks like checking for due reminders.
    """
    try:
        body = await request.json()
        logger.info(f"Job triggered: {body}")

        # Example: Check for due reminders
        # await check_due_reminders()

        return {"status": "success"}
    except Exception as e:
        logger.error(f"Job execution error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ================== STARTUP/SHUTDOWN ==================


@app.on_event("startup")
async def startup_event():
    """Application startup tasks."""
    logger.info("Notification service starting up...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks."""
    logger.info("Notification service shutting down...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8001)),
        log_level="info",
    )
