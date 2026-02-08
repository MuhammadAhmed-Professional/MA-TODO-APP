"""
Recurring Task Service

Business logic for recurring task management:
- Create recurring task configurations
- Process completed recurring tasks (spawn next instance)
- Calculate next occurrence based on frequency rules
- Support daily, weekly, monthly, and custom cron patterns
"""

from datetime import datetime, timedelta
from typing import Optional

from croniter import croniter
from fastapi import Depends, HTTPException
from sqlmodel import Session, select

from src.db.session import get_session
from src.models.advanced_task import (
    FrequencyType,
    RecurringTask,
    RecurringTaskCreate,
    RecurringTaskResponse,
)
from src.models.task import Task, TaskCreate


class RecurringTaskService:
    """Service for recurring task operations"""

    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    async def create_recurring(
        self,
        task_id: str,
        recurring_data: RecurringTaskCreate,
        user_id: str,
    ) -> RecurringTaskResponse:
        """
        Set up recurring pattern for a task.

        Args:
            task_id: Task to make recurring
            recurring_data: Recurrence configuration
            user_id: User ID for ownership verification

        Returns:
            Created recurring task configuration

        Raises:
            HTTPException: 404 if task not found, 403 if not authorized,
                          400 if task already has recurrence
        """
        # Verify task exists and user owns it
        task = self.session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        if task.user_id != user_id:
            raise HTTPException(
                status_code=403, detail="Not authorized to modify this task"
            )

        # Check if task already has recurrence
        existing = self.session.exec(
            select(RecurringTask).where(RecurringTask.task_id == task_id)
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Task already has recurring configuration. Update or delete it first.",
            )

        # Calculate next occurrence
        next_due = self._calculate_next_occurrence(
            base_time=datetime.utcnow(),
            frequency=recurring_data.frequency,
            interval=recurring_data.interval,
            cron_expression=recurring_data.cron_expression,
        )

        # Create recurring task configuration
        recurring_task = RecurringTask(
            task_id=task_id,
            frequency=recurring_data.frequency,
            interval=recurring_data.interval,
            cron_expression=recurring_data.cron_expression,
            next_due_at=next_due,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        self.session.add(recurring_task)
        self.session.commit()
        self.session.refresh(recurring_task)

        return RecurringTaskResponse.model_validate(recurring_task)

    async def process_completed_recurring(
        self, task_id: str, user_id: str
    ) -> Optional[Task]:
        """
        Process a completed recurring task by spawning the next instance.

        Called when a recurring task is marked complete. Creates a new task
        instance with the same title/description and updates next_due_at.

        Args:
            task_id: Completed task ID
            user_id: User ID for ownership verification

        Returns:
            Newly created task instance, or None if task is not recurring

        Raises:
            HTTPException: 404 if task not found, 403 if not authorized
        """
        # Verify task exists and user owns it
        task = self.session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        if task.user_id != user_id:
            raise HTTPException(
                status_code=403, detail="Not authorized to modify this task"
            )

        # Check if task is recurring
        recurring = self.session.exec(
            select(RecurringTask).where(RecurringTask.task_id == task_id)
        ).first()

        if not recurring or not recurring.is_active:
            return None  # Not a recurring task or recurrence disabled

        # Calculate next occurrence
        next_due = self._calculate_next_occurrence(
            base_time=datetime.utcnow(),
            frequency=recurring.frequency,
            interval=recurring.interval,
            cron_expression=recurring.cron_expression,
        )

        # Create new task instance (copy title, description from original)
        new_task = Task(
            title=task.title,
            description=task.description,
            is_complete=False,
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Update recurring task's next_due_at
        recurring.next_due_at = next_due
        recurring.updated_at = datetime.utcnow()

        self.session.add(new_task)
        self.session.add(recurring)
        self.session.commit()
        self.session.refresh(new_task)

        return new_task

    def get_next_occurrence(
        self,
        task_id: str,
        user_id: str,
    ) -> Optional[datetime]:
        """
        Get the next scheduled occurrence for a recurring task.

        Args:
            task_id: Task ID
            user_id: User ID for ownership verification

        Returns:
            Next occurrence timestamp, or None if not recurring
        """
        # Verify ownership
        task = self.session.get(Task, task_id)
        if not task or task.user_id != user_id:
            return None

        # Get recurring configuration
        recurring = self.session.exec(
            select(RecurringTask).where(RecurringTask.task_id == task_id)
        ).first()

        if not recurring or not recurring.is_active:
            return None

        return recurring.next_due_at

    def _calculate_next_occurrence(
        self,
        base_time: datetime,
        frequency: FrequencyType,
        interval: int,
        cron_expression: Optional[str] = None,
    ) -> datetime:
        """
        Calculate next occurrence based on recurrence rules.

        Args:
            base_time: Starting point (usually current time)
            frequency: Recurrence frequency type
            interval: Interval multiplier
            cron_expression: Optional cron expression for custom frequency

        Returns:
            Next occurrence timestamp

        Raises:
            ValueError: If cron expression is invalid or required for custom frequency
        """
        if frequency == FrequencyType.CUSTOM:
            if not cron_expression:
                raise ValueError("Cron expression required for custom frequency")

            try:
                # Use croniter to calculate next occurrence
                cron = croniter(cron_expression, base_time)
                return cron.get_next(datetime)
            except Exception as e:
                raise ValueError(f"Invalid cron expression: {str(e)}")

        elif frequency == FrequencyType.DAILY:
            return base_time + timedelta(days=interval)

        elif frequency == FrequencyType.WEEKLY:
            return base_time + timedelta(weeks=interval)

        elif frequency == FrequencyType.MONTHLY:
            # Approximate monthly recurrence (30 days * interval)
            # For exact month handling, consider using dateutil.relativedelta
            return base_time + timedelta(days=30 * interval)

        else:
            raise ValueError(f"Unsupported frequency type: {frequency}")

    async def spawn_next_task(
        self,
        original_task: Task,
        recurring: RecurringTask,
    ) -> Task:
        """
        Spawn the next task instance from a recurring task.

        Helper method for creating new task instances with inherited properties.

        Args:
            original_task: Original task model
            recurring: Recurring task configuration

        Returns:
            Newly created task instance
        """
        new_task = Task(
            title=original_task.title,
            description=original_task.description,
            is_complete=False,
            user_id=original_task.user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        self.session.add(new_task)
        self.session.commit()
        self.session.refresh(new_task)

        return new_task
