"""
Advanced Task API Endpoints

API controllers for Phase V advanced task features:
- Search and filter tasks
- Recurring task management
- Reminder scheduling
- Category management
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.auth.dependencies import get_current_user
from src.models.advanced_task import (
    RecurringTaskCreate,
    RecurringTaskResponse,
    TaskCategoryCreate,
    TaskCategoryResponse,
    TaskPriority,
    TaskReminderCreate,
    TaskReminderResponse,
)
from src.models.task import Task, TaskResponse
from src.models.user import User
from sqlmodel import Session, select

from src.db.session import get_session
from src.models.advanced_task import TaskCategory
from src.services.recurring_task_service import RecurringTaskService
from src.services.reminder_service import ReminderService
from src.services.search_service import SearchService

router = APIRouter(prefix="/api/tasks", tags=["advanced-tasks"])


# ================== SEARCH AND FILTER ENDPOINTS ==================


@router.get(
    "/search",
    response_model=List[TaskResponse],
    status_code=200,
    summary="Search and filter tasks",
    description="Advanced search with keyword, priority, category, and due date filters",
)
async def search_tasks(
    q: Optional[str] = Query(None, description="Search keyword (title/description)"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by priority"),
    category: Optional[str] = Query(None, description="Filter by category ID"),
    is_complete: Optional[bool] = Query(None, description="Filter by completion status"),
    due_before: Optional[datetime] = Query(None, description="Filter tasks due before this date"),
    due_after: Optional[datetime] = Query(None, description="Filter tasks due after this date"),
    sort_by: str = Query("created_at", description="Sort field (created_at, title, due_date, priority)"),
    sort_order: str = Query("desc", description="Sort order (asc, desc)"),
    limit: int = Query(50, ge=1, le=100, description="Max results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: User = Depends(get_current_user),
    search_service: SearchService = Depends(),
):
    """
    Search and filter tasks with multiple criteria.

    **Query Parameters:**
    - q: Keyword to search in title/description (case-insensitive)
    - priority: Filter by priority (low/medium/high/urgent)
    - category: Filter by category ID
    - is_complete: Filter by completion status (true/false/null for all)
    - due_before: Filter tasks due before this datetime (ISO 8601)
    - due_after: Filter tasks due after this datetime (ISO 8601)
    - sort_by: Sort field (created_at, title, due_date, priority)
    - sort_order: Sort direction (asc, desc)
    - limit: Maximum results (1-100, default 50)
    - offset: Pagination offset (default 0)

    **Example:**
    ```
    GET /api/tasks/search?q=documentation&priority=high&due_before=2026-02-01T00:00:00Z&sort_by=due_date
    ```

    **Returns:**
    - List of tasks matching all criteria (AND logic)
    """
    tasks = await search_service.search_tasks(
        user_id=current_user.id,
        query=q,
        priority=priority,
        category_id=category,
        is_complete=is_complete,
        due_before=due_before,
        due_after=due_after,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset,
    )

    return [TaskResponse.model_validate(task) for task in tasks]


# ================== RECURRING TASK ENDPOINTS ==================


@router.post(
    "/{task_id}/recurring",
    response_model=RecurringTaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Set up recurring task",
    description="Configure a task to repeat on a schedule",
)
async def create_recurring_task(
    task_id: str,
    recurring_data: RecurringTaskCreate,
    current_user: User = Depends(get_current_user),
    recurring_service: RecurringTaskService = Depends(),
):
    """
    Set up recurring pattern for a task.

    **Request Body:**
    - frequency: Recurrence type (daily/weekly/monthly/custom)
    - interval: Interval multiplier (e.g., every 2 weeks = weekly + interval=2)
    - cron_expression: Optional cron expression for custom frequency

    **Behavior:**
    - When a recurring task is marked complete, a new instance is automatically created
    - Original task is preserved in completed state
    - New task inherits title and description from original

    **Example:**
    ```json
    POST /api/tasks/650e8400-e29b-41d4-a716-446655440001/recurring
    {
        "frequency": "weekly",
        "interval": 1,
        "cron_expression": null
    }
    ```

    **Returns:**
    - 201: Recurring configuration created
    - 400: Task already has recurrence or invalid configuration
    - 403: Not authorized to modify task
    - 404: Task not found
    """
    return await recurring_service.create_recurring(
        task_id=task_id,
        recurring_data=recurring_data,
        user_id=current_user.id,
    )


@router.get(
    "/{task_id}/recurring",
    response_model=Optional[RecurringTaskResponse],
    status_code=200,
    summary="Get recurring task configuration",
)
async def get_recurring_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    recurring_service: RecurringTaskService = Depends(),
):
    """
    Get recurring configuration for a task.

    **Returns:**
    - Recurring configuration if task is recurring
    - null if task is not recurring
    """
    next_due = await recurring_service.get_next_occurrence(
        task_id=task_id,
        user_id=current_user.id,
    )

    if next_due is None:
        return None

    return {"next_due_at": next_due}


# ================== REMINDER ENDPOINTS ==================


@router.post(
    "/{task_id}/reminder",
    response_model=TaskReminderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Schedule task reminder",
    description="Set a reminder notification for a task",
)
async def create_reminder(
    task_id: str,
    reminder_data: TaskReminderCreate,
    current_user: User = Depends(get_current_user),
    reminder_service: ReminderService = Depends(),
):
    """
    Schedule a reminder for a task.

    **Request Body:**
    - remind_at: Datetime when reminder should trigger (ISO 8601, UTC)
    - notification_type: Delivery method (email/push/in_app)

    **Behavior:**
    - Reminder notification is sent at the specified time via Kafka event
    - Notification microservice processes the event and delivers notification
    - Reminders are sent even if task is already complete

    **Example:**
    ```json
    POST /api/tasks/650e8400-e29b-41d4-a716-446655440001/reminder
    {
        "remind_at": "2026-02-01T09:00:00Z",
        "notification_type": "in_app"
    }
    ```

    **Returns:**
    - 201: Reminder created successfully
    - 400: Reminder time is in the past
    - 403: Not authorized to modify task
    - 404: Task not found
    """
    return await reminder_service.schedule_reminder(
        task_id=task_id,
        reminder_data=reminder_data,
        user_id=current_user.id,
    )


@router.get(
    "/{task_id}/reminders",
    response_model=List[TaskReminderResponse],
    status_code=200,
    summary="Get task reminders",
    description="List all reminders for a task",
)
async def get_task_reminders(
    task_id: str,
    current_user: User = Depends(get_current_user),
    reminder_service: ReminderService = Depends(),
):
    """
    Get all reminders for a specific task.

    **Returns:**
    - List of reminders (both sent and pending)
    """
    return await reminder_service.get_task_reminders(
        task_id=task_id,
        user_id=current_user.id,
    )


@router.delete(
    "/reminders/{reminder_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete reminder",
    description="Cancel a scheduled reminder",
)
async def delete_reminder(
    reminder_id: str,
    current_user: User = Depends(get_current_user),
    reminder_service: ReminderService = Depends(),
):
    """
    Delete a reminder.

    **Returns:**
    - 204: Reminder deleted successfully
    - 403: Not authorized
    - 404: Reminder not found
    """
    await reminder_service.delete_reminder(
        reminder_id=reminder_id,
        user_id=current_user.id,
    )
    return None


# ================== CATEGORY ENDPOINTS ==================


@router.get(
    "/categories",
    response_model=List[TaskCategoryResponse],
    status_code=200,
    summary="List task categories",
    description="Get all categories for the authenticated user",
)
async def list_categories(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    List all task categories for the authenticated user.

    **Returns:**
    - List of user's categories
    """
    query = select(TaskCategory).where(TaskCategory.user_id == current_user.id)
    categories = session.exec(query).all()
    return [TaskCategoryResponse.model_validate(c) for c in categories]


@router.post(
    "/categories",
    response_model=TaskCategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create category",
    description="Create a new task category",
)
async def create_category(
    category_data: TaskCategoryCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Create a new task category.

    **Request Body:**
    - name: Category name (1-50 characters)
    - color: Hex color code (e.g., #ef4444)

    **Example:**
    ```json
    POST /api/tasks/categories
    {
        "name": "Work",
        "color": "#ef4444"
    }
    ```

    **Returns:**
    - 201: Category created successfully
    - 400: Invalid category data
    """
    category = TaskCategory(
        user_id=current_user.id,
        name=category_data.name,
        color=category_data.color,
    )
    session.add(category)
    session.commit()
    session.refresh(category)
    return TaskCategoryResponse.model_validate(category)


@router.get(
    "/categories/{category_id}",
    response_model=TaskCategoryResponse,
    status_code=200,
    summary="Get category",
    description="Get a specific category by ID",
)
async def get_category(
    category_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get a specific category by ID."""
    category = session.get(TaskCategory, category_id)
    if not category or category.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Category not found")
    return TaskCategoryResponse.model_validate(category)


@router.delete(
    "/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete category",
    description="Delete a task category",
)
async def delete_category(
    category_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Delete a task category.

    **Returns:**
    - 204: Category deleted successfully
    - 403: Not authorized
    - 404: Category not found
    """
    category = session.get(TaskCategory, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    if category.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    session.delete(category)
    session.commit()
    return None
