"""
Search and Filter Service

Advanced search, filtering, and sorting for tasks:
- Full-text search by keyword (title, description)
- Filter by priority, category, due date range, completion status
- Sort by due_date, priority, created_at, title
- Combine filters for complex queries
"""

from datetime import datetime
from typing import List, Optional

from fastapi import Depends
from sqlmodel import Session, col, or_, select

from src.db.session import get_session
from src.models.advanced_task import TaskCategory, TaskPriority
from src.models.task import Task


class SearchService:
    """Service for advanced task search and filtering"""

    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    async def search_tasks(
        self,
        user_id: str,
        query: Optional[str] = None,
        priority: Optional[TaskPriority] = None,
        category_id: Optional[str] = None,
        is_complete: Optional[bool] = None,
        due_before: Optional[datetime] = None,
        due_after: Optional[datetime] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        limit: int = 50,
        offset: int = 0,
    ) -> List[Task]:
        """
        Search and filter tasks with multiple criteria.

        Args:
            user_id: User ID to search within
            query: Keyword to search in title/description (case-insensitive)
            priority: Filter by priority level
            category_id: Filter by category
            is_complete: Filter by completion status
            due_before: Filter tasks due before this date
            due_after: Filter tasks due after this date
            sort_by: Sort field (due_date, priority, created_at, title)
            sort_order: Sort direction (asc, desc)
            limit: Maximum results to return
            offset: Number of results to skip (pagination)

        Returns:
            List of matching tasks
        """
        # Start with user's tasks
        query_stmt = select(Task).where(Task.user_id == user_id)

        # Apply keyword search (title or description)
        if query:
            search_pattern = f"%{query.lower()}%"
            query_stmt = query_stmt.where(
                or_(
                    col(Task.title).ilike(search_pattern),
                    col(Task.description).ilike(search_pattern),
                )
            )

        # Filter by priority
        if priority:
            # NOTE: This assumes Task model has priority field (extended in Phase V)
            # If using base Task model, this filter will need to be removed
            # or implemented via JOIN with extended task table
            query_stmt = query_stmt.where(Task.priority == priority)

        # Filter by category
        if category_id:
            # NOTE: This assumes Task model has category_id field
            query_stmt = query_stmt.where(Task.category_id == category_id)

        # Filter by completion status
        if is_complete is not None:
            query_stmt = query_stmt.where(Task.is_complete == is_complete)

        # Filter by due date range
        if due_before:
            # NOTE: This assumes Task model has due_date field
            query_stmt = query_stmt.where(Task.due_date <= due_before)
        if due_after:
            query_stmt = query_stmt.where(Task.due_date >= due_after)

        # Apply sorting
        sort_column = self._get_sort_column(sort_by)
        if sort_order == "asc":
            query_stmt = query_stmt.order_by(sort_column)
        else:
            query_stmt = query_stmt.order_by(sort_column.desc())

        # Apply pagination
        query_stmt = query_stmt.limit(limit).offset(offset)

        # Execute query
        results = self.session.exec(query_stmt).all()
        return list(results)

    async def filter_tasks(
        self,
        user_id: str,
        priority: Optional[TaskPriority] = None,
        category_id: Optional[str] = None,
        is_complete: Optional[bool] = None,
    ) -> List[Task]:
        """
        Filter tasks by specific criteria (simplified interface).

        Args:
            user_id: User ID to filter within
            priority: Filter by priority level
            category_id: Filter by category
            is_complete: Filter by completion status

        Returns:
            List of matching tasks
        """
        return await self.search_tasks(
            user_id=user_id,
            priority=priority,
            category_id=category_id,
            is_complete=is_complete,
        )

    async def sort_tasks(
        self,
        user_id: str,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        limit: int = 50,
        offset: int = 0,
    ) -> List[Task]:
        """
        Sort tasks by specified field.

        Args:
            user_id: User ID to sort within
            sort_by: Sort field (due_date, priority, created_at, title)
            sort_order: Sort direction (asc, desc)
            limit: Maximum results to return
            offset: Number of results to skip

        Returns:
            List of sorted tasks
        """
        return await self.search_tasks(
            user_id=user_id,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset,
        )

    def _get_sort_column(self, sort_by: str):
        """
        Map sort field name to SQLModel column.

        Args:
            sort_by: Field name to sort by

        Returns:
            SQLModel column object

        Raises:
            ValueError: If sort field is invalid
        """
        sort_columns = {
            "created_at": Task.created_at,
            "updated_at": Task.updated_at,
            "title": Task.title,
            "due_date": Task.due_date,
            "priority": Task.priority,
        }

        if sort_by not in sort_columns:
            raise ValueError(
                f"Invalid sort field: {sort_by}. "
                f"Valid options: {', '.join(sort_columns.keys())}"
            )

        return sort_columns[sort_by]

    async def get_tasks_by_category(
        self,
        user_id: str,
        category_id: str,
        is_complete: Optional[bool] = None,
    ) -> List[Task]:
        """
        Get all tasks in a specific category.

        Args:
            user_id: User ID for ownership verification
            category_id: Category to filter by
            is_complete: Optional completion status filter

        Returns:
            List of tasks in the category
        """
        # Verify category exists and belongs to user
        category = self.session.get(TaskCategory, category_id)
        if not category or category.user_id != user_id:
            return []

        return await self.search_tasks(
            user_id=user_id,
            category_id=category_id,
            is_complete=is_complete,
        )

    async def get_overdue_tasks(self, user_id: str) -> List[Task]:
        """
        Get all overdue tasks (due_date < now and not complete).

        Args:
            user_id: User ID to search within

        Returns:
            List of overdue tasks
        """
        return await self.search_tasks(
            user_id=user_id,
            due_before=datetime.utcnow(),
            is_complete=False,
            sort_by="due_date",
            sort_order="asc",  # Oldest overdue first
        )

    async def get_upcoming_tasks(
        self,
        user_id: str,
        days_ahead: int = 7,
    ) -> List[Task]:
        """
        Get tasks due in the next N days.

        Args:
            user_id: User ID to search within
            days_ahead: Number of days to look ahead (default: 7)

        Returns:
            List of upcoming tasks
        """
        from datetime import timedelta

        now = datetime.utcnow()
        future_date = now + timedelta(days=days_ahead)

        return await self.search_tasks(
            user_id=user_id,
            due_after=now,
            due_before=future_date,
            is_complete=False,
            sort_by="due_date",
            sort_order="asc",  # Nearest deadline first
        )
