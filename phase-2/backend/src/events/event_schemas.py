"""
Event Schemas

Data classes for Kafka event payloads:
- TaskEvent: Task lifecycle events (created, updated, completed, deleted)
- ReminderEvent: Reminder notifications
- Event serialization/deserialization utilities
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class TaskEvent:
    """
    Task lifecycle event payload.

    Published to 'task-events' topic when tasks are created, updated,
    completed, or deleted. Consumed by:
    - RecurringTaskConsumer (for spawning next recurring instance)
    - AuditLogConsumer (for logging all task operations)
    """

    event_type: str  # task.created, task.updated, task.completed, task.deleted
    task_id: str
    task_data: Dict[str, Any]  # Full task object as dict
    user_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize event to dictionary for Kafka."""
        return {
            "event_type": self.event_type,
            "task_id": self.task_id,
            "task_data": self.task_data,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata or {},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskEvent":
        """Deserialize event from Kafka message."""
        return cls(
            event_type=data["event_type"],
            task_id=data["task_id"],
            task_data=data["task_data"],
            user_id=data["user_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata"),
        )


@dataclass
class ReminderEvent:
    """
    Reminder notification event payload.

    Published to 'reminders' topic when a reminder is due.
    Consumed by NotificationService to deliver notifications via:
    - In-app notifications
    - Email
    - Push notifications
    """

    reminder_id: str
    task_id: str
    task_title: str
    user_id: str
    remind_at: datetime
    notification_type: str  # email, push, in_app
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize event to dictionary for Kafka."""
        return {
            "reminder_id": self.reminder_id,
            "task_id": self.task_id,
            "task_title": self.task_title,
            "user_id": self.user_id,
            "remind_at": self.remind_at.isoformat(),
            "notification_type": self.notification_type,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata or {},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReminderEvent":
        """Deserialize event from Kafka message."""
        return cls(
            reminder_id=data["reminder_id"],
            task_id=data["task_id"],
            task_title=data["task_title"],
            user_id=data["user_id"],
            remind_at=datetime.fromisoformat(data["remind_at"]),
            notification_type=data["notification_type"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata"),
        )


@dataclass
class AuditLogEvent:
    """
    Audit log event for compliance and debugging.

    Published to 'audit-logs' topic for all task operations.
    Consumed by AuditLogConsumer to store in audit log database.
    """

    event_type: str  # audit.task.created, audit.task.updated, etc.
    resource_type: str  # task, reminder, category
    resource_id: str
    user_id: str
    action: str  # created, updated, deleted, viewed
    timestamp: datetime = field(default_factory=datetime.utcnow)
    changes: Optional[Dict[str, Any]] = None  # Before/after values
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize event to dictionary for Kafka."""
        return {
            "event_type": self.event_type,
            "resource_type": resource_type,
            "resource_id": self.resource_id,
            "user_id": self.user_id,
            "action": self.action,
            "timestamp": self.timestamp.isoformat(),
            "changes": self.changes,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuditLogEvent":
        """Deserialize event from Kafka message."""
        return cls(
            event_type=data["event_type"],
            resource_type=data["resource_type"],
            resource_id=data["resource_id"],
            user_id=data["user_id"],
            action=data["action"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            changes=data.get("changes"),
            ip_address=data.get("ip_address"),
            user_agent=data.get("user_agent"),
        )
