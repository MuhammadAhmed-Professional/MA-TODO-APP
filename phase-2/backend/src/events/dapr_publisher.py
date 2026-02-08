"""
Dapr Event Publisher

Replaces direct Kafka producer with Dapr pub/sub API.
Publishes events to Kafka topics via Dapr sidecar.

Topics:
- task-events: Task lifecycle events
- reminders: Reminder notification events
- task-updates: Task update events
- audit-logs: Audit log events
"""

import asyncio
import logging
import os
from typing import Any, Dict, Optional

from src.events.event_schemas import TaskEvent
from src.services.dapr_client import DaprClient, get_dapr_client

logger = logging.getLogger(__name__)

# Dapr pub/sub component name (defined in dapr/components/pubsub-kafka.yaml)
PUBSUB_COMPONENT_NAME = "kafka-pubsub"

# Enable/disable event publishing via environment variable
EVENT_PUBLISHING_ENABLED = os.getenv("EVENT_PUBLISHING_ENABLED", "true").lower() == "true"


class DaprEventPublisher:
    """
    Dapr-based event publisher.

    Uses Dapr sidecar HTTP API to publish events to Kafka topics.
    Provides automatic retries and error handling via Dapr.
    """

    def __init__(self, dapr_client: Optional[DaprClient] = None):
        """
        Initialize Dapr event publisher.

        Args:
            dapr_client: Optional DaprClient instance (uses global if not provided)
        """
        self.dapr_client = dapr_client

    async def _get_client(self) -> DaprClient:
        """Get Dapr client (lazy initialization)."""
        if self.dapr_client is None:
            self.dapr_client = await get_dapr_client()
        return self.dapr_client

    async def publish_event(
        self,
        topic: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, str]] = None,
    ) -> bool:
        """
        Publish an event to a Kafka topic via Dapr pub/sub.

        Args:
            topic: Kafka topic name
            data: Event payload (JSON-serializable)
            metadata: Optional metadata (headers, content type, etc.)

        Returns:
            True if publish succeeded, False otherwise
        """
        if not EVENT_PUBLISHING_ENABLED:
            logger.debug(f"Event publishing disabled, skipping {topic}")
            return True  # Pretend success for graceful degradation

        try:
            client = await self._get_client()
            success = await client.publish_event(
                pubsub_name=PUBSUB_COMPONENT_NAME,
                topic=topic,
                data=data,
                metadata=metadata,
            )

            if success:
                logger.debug(f"Published event to {topic} via Dapr")
            else:
                logger.warning(f"Failed to publish event to {topic}")

            return success

        except Exception as e:
            logger.error(f"Error publishing event to {topic}: {e}", exc_info=True)
            return False

    async def publish_task_event(
        self,
        event_type: str,
        task_data: Dict[str, Any],
        user_id: str,
    ) -> bool:
        """
        Publish a task lifecycle event (fire-and-forget).

        Args:
            event_type: Event type (task.created, task.updated, task.completed, task.deleted)
            task_data: Full task object as dictionary
            user_id: User ID who triggered the event

        Returns:
            True if publish succeeded (or disabled)
        """
        if not EVENT_PUBLISHING_ENABLED:
            return True

        event = TaskEvent(
            event_type=event_type,
            task_id=task_data.get("id"),
            task_data=task_data,
            user_id=user_id,
        )

        # Fire-and-forget: publish in background task
        asyncio.create_task(
            self.publish_event(
                topic="task-events",
                data=event.to_dict(),
            )
        )
        return True

    async def publish_reminder_event(
        self,
        reminder_data: Dict[str, Any],
    ) -> bool:
        """
        Publish a reminder notification event.

        Args:
            reminder_data: Reminder event payload

        Returns:
            True if publish succeeded
        """
        return await self.publish_event(
            topic="reminders",
            data=reminder_data,
        )

    async def publish_audit_log(
        self,
        event_type: str,
        resource_type: str,
        resource_id: str,
        user_id: str,
        action: str,
        changes: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Publish an audit log event.

        Args:
            event_type: Audit event type
            resource_type: Type of resource (task, reminder, category)
            resource_id: Resource identifier
            user_id: User who performed the action
            action: Action performed (created, updated, deleted, viewed)
            changes: Optional before/after values

        Returns:
            True if publish succeeded
        """
        return await self.publish_event(
            topic="audit-logs",
            data={
                "event_type": event_type,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "user_id": user_id,
                "action": action,
                "changes": changes,
            },
        )


# Global publisher instance (singleton pattern)
_publisher_instance: Optional[DaprEventPublisher] = None


async def get_event_publisher() -> DaprEventPublisher:
    """
    Get global event publisher instance (FastAPI dependency).

    Returns:
        Shared DaprEventPublisher instance
    """
    global _publisher_instance
    if _publisher_instance is None:
        _publisher_instance = DaprEventPublisher()
    return _publisher_instance
