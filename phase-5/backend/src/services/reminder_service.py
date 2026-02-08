"""
Reminder Service

Business logic for task reminder management:
- Schedule reminders for tasks
- Check for due reminders and trigger notifications
- Send notifications via Kafka events
"""

from datetime import datetime
from typing import List

from fastapi import Depends, HTTPException
from sqlmodel import Session, select

from src.db.session import get_session
from src.models.advanced_task import (
    NotificationType,
    TaskReminder,
    TaskReminderCreate,
    TaskReminderResponse,
)
from src.models.task import Task


class ReminderService:
    """Service for task reminder operations"""

    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    async def schedule_reminder(
        self,
        task_id: str,
        reminder_data: TaskReminderCreate,
        user_id: str,
    ) -> TaskReminderResponse:
        """
        Schedule a reminder for a task.

        Args:
            task_id: Task to set reminder for
            reminder_data: Reminder configuration
            user_id: User ID for ownership verification

        Returns:
            Created reminder

        Raises:
            HTTPException: 404 if task not found, 403 if not authorized,
                          400 if reminder time is in the past
        """
        # Verify task exists and user owns it
        task = self.session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        if task.user_id != user_id:
            raise HTTPException(
                status_code=403, detail="Not authorized to modify this task"
            )

        # Validate reminder time is in the future
        if reminder_data.remind_at <= datetime.utcnow():
            raise HTTPException(
                status_code=400,
                detail="Reminder time must be in the future",
            )

        # Create reminder
        reminder = TaskReminder(
            task_id=task_id,
            remind_at=reminder_data.remind_at,
            notification_type=reminder_data.notification_type,
            is_sent=False,
            created_at=datetime.utcnow(),
        )

        self.session.add(reminder)
        self.session.commit()
        self.session.refresh(reminder)

        return TaskReminderResponse.model_validate(reminder)

    async def check_due_reminders(self) -> List[TaskReminder]:
        """
        Check for reminders that are due and not yet sent.

        This method should be called periodically (e.g., every minute via cron job)
        to process pending reminders.

        Returns:
            List of reminders that need to be sent
        """
        now = datetime.utcnow()

        # Query reminders that are due and not sent
        query = select(TaskReminder).where(
            TaskReminder.remind_at <= now,
            TaskReminder.is_sent == False,  # noqa: E712
        )

        due_reminders = self.session.exec(query).all()
        return list(due_reminders)

    async def send_notification(
        self,
        reminder: TaskReminder,
    ) -> None:
        """
        Send notification for a reminder.

        Publishes an event to the 'reminders' topic via Dapr pub/sub for the
        notification microservice to process. Marks reminder as sent in the database.

        Args:
            reminder: Reminder to send notification for

        Raises:
            HTTPException: 404 if associated task not found
        """
        # Get associated task
        task = self.session.get(Task, reminder.task_id)
        if not task:
            # Task was deleted - mark reminder as sent to prevent retries
            reminder.is_sent = True
            reminder.sent_at = datetime.utcnow()
            self.session.add(reminder)
            self.session.commit()
            return

        # Publish event to 'reminders' topic via Dapr pub/sub
        from src.events.dapr_publisher import get_event_publisher

        publisher = await get_event_publisher()
        event_data = {
            "reminder_id": reminder.id,
            "task_id": task.id,
            "task_title": task.title,
            "user_id": task.user_id,
            "remind_at": reminder.remind_at.isoformat(),
            "notification_type": reminder.notification_type.value,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await publisher.publish_reminder_event(event_data)

        # Mark reminder as sent
        reminder.is_sent = True
        reminder.sent_at = datetime.utcnow()
        self.session.add(reminder)
        self.session.commit()

    async def get_task_reminders(
        self,
        task_id: str,
        user_id: str,
    ) -> List[TaskReminderResponse]:
        """
        Get all reminders for a specific task.

        Args:
            task_id: Task ID
            user_id: User ID for ownership verification

        Returns:
            List of reminders for the task

        Raises:
            HTTPException: 404 if task not found, 403 if not authorized
        """
        # Verify task exists and user owns it
        task = self.session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        if task.user_id != user_id:
            raise HTTPException(
                status_code=403, detail="Not authorized to access this task"
            )

        # Get reminders for task
        query = select(TaskReminder).where(TaskReminder.task_id == task_id)
        reminders = self.session.exec(query).all()

        return [TaskReminderResponse.model_validate(r) for r in reminders]

    async def delete_reminder(
        self,
        reminder_id: str,
        user_id: str,
    ) -> None:
        """
        Delete a reminder.

        Args:
            reminder_id: Reminder ID to delete
            user_id: User ID for ownership verification

        Raises:
            HTTPException: 404 if reminder or task not found, 403 if not authorized
        """
        # Get reminder
        reminder = self.session.get(TaskReminder, reminder_id)
        if not reminder:
            raise HTTPException(status_code=404, detail="Reminder not found")

        # Verify user owns the associated task
        task = self.session.get(Task, reminder.task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Associated task not found")
        if task.user_id != user_id:
            raise HTTPException(
                status_code=403, detail="Not authorized to delete this reminder"
            )

        # Delete reminder
        self.session.delete(reminder)
        self.session.commit()
