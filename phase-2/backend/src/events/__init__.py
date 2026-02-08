"""
Event Publishing Module

Provides event publishing capabilities for task lifecycle events:
- DaprEventPublisher: Primary publisher via Dapr sidecar
- KafkaEventProducer: Fallback direct Kafka publisher (for development)
- Event schemas for task, reminder, and audit events
"""

from src.events.dapr_publisher import DaprEventPublisher, get_event_publisher
from src.events.event_schemas import (
    AuditLogEvent,
    ReminderEvent,
    TaskEvent,
)

__all__ = [
    "DaprEventPublisher",
    "get_event_publisher",
    "TaskEvent",
    "ReminderEvent",
    "AuditLogEvent",
]
