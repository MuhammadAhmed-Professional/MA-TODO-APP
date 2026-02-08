"""
Kafka Event Producer

Publishes events to Kafka topics using aiokafka:
- Task lifecycle events (task-events topic)
- Reminder notifications (reminders topic)
- Task updates (task-updates topic)
- Audit logs (audit-logs topic)
"""

import json
import logging
import os
from typing import Any, Dict, Optional

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from src.events.event_schemas import TaskEvent

logger = logging.getLogger(__name__)


class KafkaEventProducer:
    """
    Kafka event producer for publishing domain events.

    Uses aiokafka for async message publishing with automatic retries
    and error handling.
    """

    def __init__(
        self,
        bootstrap_servers: Optional[str] = None,
        client_id: str = "todo-backend",
    ):
        """
        Initialize Kafka producer.

        Args:
            bootstrap_servers: Kafka broker addresses (comma-separated)
            client_id: Client identifier for Kafka
        """
        self.bootstrap_servers = bootstrap_servers or os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
        )
        self.client_id = client_id
        self.producer: Optional[AIOKafkaProducer] = None

    async def start(self):
        """Start Kafka producer and establish connection."""
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                client_id=self.client_id,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                # Reliability settings
                acks="all",  # Wait for all replicas to acknowledge
                retries=3,  # Retry up to 3 times on failure
                max_in_flight_requests_per_connection=1,  # Ensure ordering
                # Performance settings
                compression_type="gzip",  # Compress messages
                linger_ms=10,  # Wait up to 10ms to batch messages
            )
            await self.producer.start()
            logger.info(
                f"Kafka producer started (bootstrap_servers={self.bootstrap_servers})"
            )
        except KafkaError as e:
            logger.error(f"Failed to start Kafka producer: {e}")
            raise

    async def stop(self):
        """Stop Kafka producer and close connection."""
        if self.producer:
            await self.producer.stop()
            logger.info("Kafka producer stopped")

    async def publish_event(
        self,
        topic: str,
        event_type: str,
        data: Dict[str, Any],
        key: Optional[str] = None,
    ) -> bool:
        """
        Publish an event to a Kafka topic.

        Args:
            topic: Kafka topic name
            event_type: Event type identifier (e.g., 'task.created')
            data: Event payload (must be JSON-serializable)
            key: Optional partition key for ordering (default: None = round-robin)

        Returns:
            True if publish succeeded, False otherwise

        Raises:
            RuntimeError: If producer is not started
        """
        if not self.producer:
            raise RuntimeError("Kafka producer not started. Call start() first.")

        try:
            # Add event_type to payload if not present
            if "event_type" not in data:
                data["event_type"] = event_type

            # Encode key if provided
            key_bytes = key.encode("utf-8") if key else None

            # Send message
            await self.producer.send_and_wait(
                topic=topic,
                value=data,
                key=key_bytes,
            )

            logger.debug(f"Published event to {topic}: {event_type}")
            return True

        except KafkaError as e:
            logger.error(f"Failed to publish event to {topic}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error publishing event: {e}", exc_info=True)
            return False

    async def publish_task_event(
        self,
        event_type: str,
        task_data: Dict[str, Any],
        user_id: str,
    ) -> bool:
        """
        Publish a task lifecycle event.

        Args:
            event_type: Event type (task.created, task.updated, task.completed, task.deleted)
            task_data: Full task object as dictionary
            user_id: User ID who triggered the event

        Returns:
            True if publish succeeded
        """
        event = TaskEvent(
            event_type=event_type,
            task_id=task_data.get("id"),
            task_data=task_data,
            user_id=user_id,
        )

        return await self.publish_event(
            topic="task-events",
            event_type=event_type,
            data=event.to_dict(),
            key=task_data.get("id"),  # Use task_id as partition key for ordering
        )

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
            event_type="reminder.due",
            data=reminder_data,
            key=reminder_data.get("task_id"),  # Use task_id as partition key
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
            event_type=event_type,
            data={
                "event_type": event_type,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "user_id": user_id,
                "action": action,
                "changes": changes,
            },
            key=resource_id,  # Use resource_id as partition key
        )


# Global producer instance (singleton pattern)
_producer_instance: Optional[KafkaEventProducer] = None


async def get_kafka_producer() -> KafkaEventProducer:
    """
    Get global Kafka producer instance (FastAPI dependency).

    Returns:
        Shared KafkaEventProducer instance
    """
    global _producer_instance
    if _producer_instance is None:
        _producer_instance = KafkaEventProducer()
        await _producer_instance.start()
    return _producer_instance


async def shutdown_kafka_producer():
    """Shutdown global Kafka producer (call on app shutdown)."""
    global _producer_instance
    if _producer_instance:
        await _producer_instance.stop()
        _producer_instance = None
