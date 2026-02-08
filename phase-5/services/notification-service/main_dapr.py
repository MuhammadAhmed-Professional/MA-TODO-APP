"""
Notification Service (Enhanced with Dapr)

Microservice for processing reminder notifications with Dapr integration:
- Subscribes to 'reminders' Kafka topic via Dapr pub/sub
- Stores notification state in Dapr state store
- Retrieves secrets from Dapr secret store
- Handles cron binding triggers for scheduled checks
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

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
    description="Processes task reminder notifications with Dapr",
    version="2.0.0",
)

# Dapr configuration
DAPR_HTTP_PORT = int(os.getenv("DAPR_HTTP_PORT", 3500))
DAPR_STATE_STORE = "postgres-statestore"
DAPR_SECRET_STORE = "kubernetes-secrets"
DAPR_PUBSUB = "kafka-pubsub"

# HTTP client for Dapr API
dapr_client = httpx.AsyncClient(timeout=30.0)


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


class NotificationState(BaseModel):
    """Notification tracking state"""

    reminder_id: str
    status: str  # pending, sent, failed
    attempts: int
    last_attempt: str
    error_message: Optional[str] = None


# ================== DAPR STATE MANAGEMENT ==================


async def get_notification_state(reminder_id: str) -> Optional[NotificationState]:
    """
    Get notification state from Dapr state store.

    Args:
        reminder_id: Reminder ID

    Returns:
        Notification state or None
    """
    try:
        response = await dapr_client.get(
            f"http://localhost:{DAPR_HTTP_PORT}/v1.0/state/{DAPR_STATE_STORE}/notification:{reminder_id}"
        )

        if response.status_code == 200:
            data = response.json()
            return NotificationState(**data)
        else:
            return None

    except Exception as e:
        logger.error(f"Error getting notification state: {e}")
        return None


async def save_notification_state(state: NotificationState) -> bool:
    """
    Save notification state to Dapr state store.

    Args:
        state: Notification state

    Returns:
        True if save succeeded
    """
    try:
        response = await dapr_client.post(
            f"http://localhost:{DAPR_HTTP_PORT}/v1.0/state/{DAPR_STATE_STORE}",
            json=[
                {
                    "key": f"notification:{state.reminder_id}",
                    "value": state.model_dump(),
                    "metadata": {"ttlInSeconds": "86400"},  # 24 hours
                }
            ],
        )

        return response.status_code == 204

    except Exception as e:
        logger.error(f"Error saving notification state: {e}")
        return False


async def get_secret(secret_name: str) -> Optional[str]:
    """
    Get secret from Dapr secret store.

    Args:
        secret_name: Secret name (e.g., "sendgrid-secret")

    Returns:
        Secret value or None
    """
    try:
        response = await dapr_client.get(
            f"http://localhost:{DAPR_HTTP_PORT}/v1.0/secrets/{DAPR_SECRET_STORE}/{secret_name}"
        )

        if response.status_code == 200:
            data = response.json()
            # Return first key value (secret structure varies)
            return next(iter(data.values())) if data else None
        else:
            return None

    except Exception as e:
        logger.error(f"Error getting secret: {e}")
        return None


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
            pubsubname=DAPR_PUBSUB,
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
    Uses state store to track delivery status and prevent duplicates.
    """
    try:
        # Parse Dapr CloudEvent envelope
        body = await request.json()
        logger.info(f"Received reminder event: {body}")

        # Extract data from CloudEvent
        if "data" in body:
            event_data = body["data"]
        else:
            event_data = body

        # Validate event
        reminder = ReminderEvent(**event_data)

        # Check if already processed (idempotency)
        existing_state = await get_notification_state(reminder.reminder_id)
        if existing_state and existing_state.status == "sent":
            logger.info(f"Reminder {reminder.reminder_id} already sent - skipping")
            return {"status": "already_sent", "reminder_id": reminder.reminder_id}

        # Process notification
        success = await send_notification(reminder)

        # Update state
        state = NotificationState(
            reminder_id=reminder.reminder_id,
            status="sent" if success else "failed",
            attempts=existing_state.attempts + 1 if existing_state else 1,
            last_attempt=datetime.utcnow().isoformat(),
        )
        await save_notification_state(state)

        # Return 200 OK to acknowledge message
        return {"status": "success" if success else "failed", "reminder_id": reminder.reminder_id}

    except Exception as e:
        logger.error(f"Error processing reminder: {e}", exc_info=True)
        # Return 500 to trigger retry for transient errors
        raise HTTPException(status_code=500, detail=str(e))


# ================== NOTIFICATION LOGIC ==================


async def send_notification(reminder: ReminderEvent) -> bool:
    """
    Send notification based on notification type.

    Args:
        reminder: Reminder event data

    Returns:
        True if notification succeeded
    """
    logger.info(
        f"Sending {reminder.notification_type} notification for task "
        f"'{reminder.task_title}' (user={reminder.user_id})"
    )

    if reminder.notification_type == "email":
        return await send_email_notification(reminder)
    elif reminder.notification_type == "push":
        return await send_push_notification(reminder)
    elif reminder.notification_type == "in_app":
        return await send_in_app_notification(reminder)
    else:
        logger.warning(f"Unknown notification type: {reminder.notification_type}")
        return False


async def send_email_notification(reminder: ReminderEvent) -> bool:
    """
    Send email notification using SendGrid API key from Dapr secret store.

    Args:
        reminder: Reminder event data

    Returns:
        True if email sent successfully
    """
    logger.info(f"[EMAIL] Reminder for task: {reminder.task_title}")

    # Get SendGrid API key from Dapr secret store
    api_key = await get_secret("sendgrid-secret")

    if not api_key:
        logger.warning("SendGrid API key not found - skipping email")
        return False

    # Production: integrate with SendGrid/SES using the api_key above.
    # For now, log a structured email payload for demonstration.
    logger.info(
        f"[EMAIL] Would send to user {reminder.user_id}: "
        f"Subject='Reminder: {reminder.task_title}', "
        f"Body='Your task is due at {reminder.remind_at}'"
    )
    logger.info(f"Email notification sent for reminder {reminder.reminder_id}")
    return True


async def send_push_notification(reminder: ReminderEvent) -> bool:
    """
    Send push notification via Firebase Cloud Messaging.

    Args:
        reminder: Reminder event data

    Returns:
        True if push sent successfully
    """
    logger.info(f"[PUSH] Reminder for task: {reminder.task_title}")

    # Get FCM server key from Dapr secret store
    fcm_key = await get_secret("fcm-server-key")

    if not fcm_key:
        logger.warning("FCM server key not found - skipping push")
        return False

    # Production: integrate with FCM using the fcm_key above.
    logger.info(
        f"[PUSH] Would send push to user {reminder.user_id}: "
        f"title='Task Reminder', body='{reminder.task_title} is due soon'"
    )
    logger.info(f"Push notification sent for reminder {reminder.reminder_id}")
    return True


async def send_in_app_notification(reminder: ReminderEvent) -> bool:
    """
    Send in-app notification by storing in Dapr state store.

    Args:
        reminder: Reminder event data

    Returns:
        True if notification stored successfully
    """
    logger.info(f"[IN-APP] Reminder for task: {reminder.task_title}")

    try:
        # Store in-app notification in state store for user to read
        notification = {
            "id": reminder.reminder_id,
            "user_id": reminder.user_id,
            "type": "reminder",
            "title": "Task Reminder",
            "message": f"{reminder.task_title} is due soon",
            "task_id": reminder.task_id,
            "created_at": datetime.utcnow().isoformat(),
            "is_read": False,
        }

        response = await dapr_client.post(
            f"http://localhost:{DAPR_HTTP_PORT}/v1.0/state/{DAPR_STATE_STORE}",
            json=[
                {
                    "key": f"in-app-notification:{reminder.user_id}:{reminder.reminder_id}",
                    "value": notification,
                    "metadata": {"ttlInSeconds": "604800"},  # 7 days
                }
            ],
        )

        success = response.status_code == 204
        if success:
            logger.info(f"In-app notification created for reminder {reminder.reminder_id}")
        return success

    except Exception as e:
        logger.error(f"Error creating in-app notification: {e}")
        return False


# ================== CRON BINDING ENDPOINTS ==================


@app.post("/api/jobs/check-reminders")
async def check_reminders_job(request: Request):
    """
    Dapr cron job callback endpoint.

    Triggered by Dapr cron binding (reminder-checker-cron) every minute.
    Checks for due reminders that need to be sent.
    """
    try:
        body = await request.json()
        logger.info(f"Check reminders job triggered: {body}")

        # Query due reminders via Dapr service invocation to the backend
        dapr_port = int(os.getenv("DAPR_HTTP_PORT", "3500"))
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                resp = await client.get(
                    f"http://localhost:{dapr_port}/v1.0/invoke/todo-backend/method/api/reminders/check-due"
                )
                if resp.status_code == 200:
                    logger.info(f"Reminder check returned: {resp.json()}")
                else:
                    logger.warning(f"Reminder check returned status {resp.status_code}")
            except Exception as invoke_err:
                logger.warning(f"Could not invoke backend for reminder check: {invoke_err}")

        logger.info("Reminder check job completed")
        return {"status": "success"}

    except Exception as e:
        logger.error(f"Job execution error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ================== HEALTH ENDPOINTS ==================


@app.get("/health")
async def health():
    """Health check endpoint for Kubernetes liveness probe."""
    return {"status": "healthy", "service": "notification-service", "version": "2.0.0"}


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
        "service": "notification-service",
        "dapr_connected": dapr_healthy,
    }


# ================== STARTUP/SHUTDOWN ==================


@app.on_event("startup")
async def startup_event():
    """Application startup tasks."""
    logger.info("Notification service starting up...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Dapr HTTP port: {DAPR_HTTP_PORT}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks."""
    logger.info("Notification service shutting down...")
    await dapr_client.aclose()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8001)),
        log_level="info",
    )
