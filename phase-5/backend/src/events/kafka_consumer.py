"""
Kafka Event Consumers

Base consumer class and specific consumers for:
- RecurringTaskConsumer: Spawns next task instance when recurring task completed
- ReminderConsumer: Processes due reminders (handled by notification service)
- AuditLogConsumer: Logs all task operations for compliance
"""

import asyncio
import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError

from src.events.event_schemas import TaskEvent

logger = logging.getLogger(__name__)


class KafkaEventConsumer(ABC):
    """
    Base class for Kafka event consumers.

    Provides common functionality for consuming and processing Kafka events.
    Subclasses implement handle_message() to process specific event types.
    """

    def __init__(
        self,
        topics: List[str],
        group_id: str,
        bootstrap_servers: Optional[str] = None,
    ):
        """
        Initialize Kafka consumer.

        Args:
            topics: List of topics to subscribe to
            group_id: Consumer group ID for load balancing
            bootstrap_servers: Kafka broker addresses
        """
        self.topics = topics
        self.group_id = group_id
        self.bootstrap_servers = bootstrap_servers or os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
        )
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.running = False

    async def start(self):
        """Start Kafka consumer and subscribe to topics."""
        try:
            self.consumer = AIOKafkaConsumer(
                *self.topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                # Reliability settings
                enable_auto_commit=False,  # Manual commit for at-least-once delivery
                auto_offset_reset="earliest",  # Start from beginning if no offset
                # Performance settings
                max_poll_records=10,  # Process 10 messages per poll
                session_timeout_ms=30000,  # 30 seconds
            )
            await self.consumer.start()
            logger.info(
                f"Kafka consumer started (group={self.group_id}, topics={self.topics})"
            )
        except KafkaError as e:
            logger.error(f"Failed to start Kafka consumer: {e}")
            raise

    async def stop(self):
        """Stop Kafka consumer and close connection."""
        self.running = False
        if self.consumer:
            await self.consumer.stop()
            logger.info(f"Kafka consumer stopped (group={self.group_id})")

    async def run(self):
        """
        Main consumer loop - poll and process messages.

        Runs until stop() is called. Processes messages in batches and
        commits offsets manually for reliability.
        """
        self.running = True
        logger.info(f"Consumer {self.group_id} started processing messages")

        try:
            async for message in self.consumer:
                if not self.running:
                    break

                try:
                    # Process message
                    await self.handle_message(message.value)

                    # Commit offset after successful processing
                    await self.consumer.commit()

                except Exception as e:
                    logger.error(
                        f"Error processing message (offset={message.offset}): {e}",
                        exc_info=True,
                    )
                    # Continue processing (don't commit offset - message will be retried)

        except asyncio.CancelledError:
            logger.info(f"Consumer {self.group_id} cancelled")
        except Exception as e:
            logger.error(f"Consumer {self.group_id} error: {e}", exc_info=True)
        finally:
            await self.stop()

    @abstractmethod
    async def handle_message(self, message: Dict[str, Any]):
        """
        Process a single message from Kafka.

        Must be implemented by subclasses to handle specific event types.

        Args:
            message: Deserialized message payload
        """
        pass


class RecurringTaskConsumer(KafkaEventConsumer):
    """
    Consumer for recurring task events.

    Listens to 'task-events' topic for 'task.completed' events.
    When a recurring task is completed, spawns the next task instance
    automatically based on recurrence rules.
    """

    def __init__(
        self,
        recurring_task_service=None,
        bootstrap_servers: Optional[str] = None,
    ):
        super().__init__(
            topics=["task-events"],
            group_id="recurring-task-consumer",
            bootstrap_servers=bootstrap_servers,
        )
        self.recurring_task_service = recurring_task_service

    async def handle_message(self, message: Dict[str, Any]):
        """
        Process task completion events for recurring tasks.

        Args:
            message: Task event payload
        """
        event = TaskEvent.from_dict(message)

        # Only process task.completed events
        if event.event_type != "task.completed":
            return

        task_id = event.task_id
        user_id = event.user_id

        logger.info(f"Processing completed task {task_id} for recurring check")

        try:
            # Check if task is recurring and spawn next instance
            if self.recurring_task_service:
                new_task = await self.recurring_task_service.process_completed_recurring(
                    task_id=task_id,
                    user_id=user_id,
                )

                if new_task:
                    logger.info(
                        f"Spawned new recurring task instance: {new_task.id} "
                        f"from completed task {task_id}"
                    )
            else:
                logger.warning("RecurringTaskService not injected - skipping processing")

        except Exception as e:
            logger.error(
                f"Error processing recurring task {task_id}: {e}",
                exc_info=True,
            )
            raise  # Re-raise to prevent offset commit (message will be retried)


class ReminderConsumer(KafkaEventConsumer):
    """
    Consumer for reminder events.

    NOTE: In Phase V architecture, this consumer runs in the
    notification-service microservice, not the main backend.
    Included here for reference.
    """

    def __init__(self, bootstrap_servers: Optional[str] = None):
        super().__init__(
            topics=["reminders"],
            group_id="reminder-consumer",
            bootstrap_servers=bootstrap_servers,
        )

    async def handle_message(self, message: Dict[str, Any]):
        """
        Process reminder notification events.

        Args:
            message: Reminder event payload
        """
        logger.info(f"Reminder due: {message.get('task_title')} for user {message.get('user_id')}")

        # Notification delivery (email, push, in-app) is handled by the
        # dedicated notification microservice at phase-5/services/notification-service/.
        # This consumer serves as a fallback logger when the microservice is unavailable.
        logger.info(
            f"[REMINDER] type={message.get('notification_type')} "
            f"task={message.get('task_title')} user={message.get('user_id')}"
        )


class AuditLogConsumer(KafkaEventConsumer):
    """
    Consumer for audit log events.

    Listens to 'task-events' and 'audit-logs' topics to log all
    task operations for compliance and debugging.
    """

    def __init__(self, bootstrap_servers: Optional[str] = None):
        super().__init__(
            topics=["task-events", "audit-logs"],
            group_id="audit-log-consumer",
            bootstrap_servers=bootstrap_servers,
        )

    async def handle_message(self, message: Dict[str, Any]):
        """
        Process and store audit log events.

        Args:
            message: Event payload
        """
        event_type = message.get("event_type", "unknown")
        resource_id = message.get("task_id") or message.get("resource_id")
        user_id = message.get("user_id")
        timestamp = message.get("timestamp")

        # Log structured audit entry (serves as persistent audit trail via log aggregation)
        logger.info(
            f"[AUDIT] {event_type} - Resource: {resource_id}, "
            f"User: {user_id}, Time: {timestamp}, "
            f"Data: {json.dumps(message, default=str)}"
        )


# Helper function to run consumers in background


async def run_consumers_background(consumers: List[KafkaEventConsumer]):
    """
    Run multiple consumers concurrently in background.

    Args:
        consumers: List of consumer instances to run
    """
    tasks = []
    for consumer in consumers:
        await consumer.start()
        task = asyncio.create_task(consumer.run())
        tasks.append(task)

    # Wait for all consumers
    await asyncio.gather(*tasks, return_exceptions=True)
