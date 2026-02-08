"""
Task Service

Business logic for task CRUD operations.
Follows "fat services" pattern - all business logic lives here.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import Depends, HTTPException
from sqlmodel import Session, select

from src.db.session import get_session
from src.models.priority import Priority
from src.models.tag import Tag
from src.models.task import Task, TaskCreate, TaskUpdate
from src.models.task_tag import TaskTag


class TaskService:
    """
    Task service handling task CRUD operations.

    All business logic for task management lives here, keeping
    route handlers thin and focused on HTTP concerns.
    """

    def __init__(self, session: Session = Depends(get_session)):
        """
        Initialize TaskService with database session.

        Args:
            session: SQLModel database session (injected via FastAPI dependency)
        """
        self.session = session

    async def create_task(
        self, task_data: TaskCreate, user_id: str
    ) -> Task:
        """
        Create new task for user.

        Business logic:
        1. Validate title not empty
        2. Create task with user ownership
        3. Set timestamps
        4. Associate with tags if provided
        5. Persist to database

        Args:
            task_data: Task creation data (title, description, priority, due_date, tag_ids)
            user_id: Owner user ID

        Returns:
            Created Task object with tags loaded

        Raises:
            ValueError: If title is empty after stripping whitespace
            ValueError: If tag IDs don't belong to user

        Example:
            service = TaskService(session)
            task = await service.create_task(
                TaskCreate(title="Buy groceries", description="Milk, eggs, bread"),
                user_id=uuid.UUID("...")
            )
        """
        # Validate title not empty
        if not task_data.title.strip():
            raise ValueError("Title cannot be empty or whitespace")

        # Validate tag ownership if tags provided
        tags = []
        if task_data.tag_ids:
            tags = self.session.exec(
                select(Tag).where(
                    Tag.id.in_(task_data.tag_ids),
                    Tag.user_id == user_id
                )
            ).all()

            if len(tags) != len(task_data.tag_ids):
                raise ValueError("One or more tag IDs are invalid or don't belong to user")

        # Create task
        task = Task(
            id=str(uuid.uuid4()),
            title=task_data.title.strip(),
            description=task_data.description.strip() if task_data.description else None,
            is_complete=False,
            priority=task_data.priority or Priority.MEDIUM,
            due_date=task_data.due_date,
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        # Persist to database
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        # Associate tags
        if tags:
            for tag in tags:
                task_tag = TaskTag(task_id=task.id, tag_id=tag.id)
                self.session.add(task_tag)
            self.session.commit()
            self.session.refresh(task)

        return task

    async def get_user_tasks(
        self,
        user_id: str,
        is_complete: Optional[bool] = None,
        priority: Optional[int] = None,
        tag_ids: Optional[List[str]] = None,
        search: Optional[str] = None,
        due_date_before: Optional[datetime] = None,
        due_date_after: Optional[datetime] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        limit: int = 50,
        offset: int = 0,
    ) -> List[Task]:
        """
        Get tasks for user with optional filtering, searching, and sorting.

        Args:
            user_id: User ID to get tasks for
            is_complete: Optional completion status filter
            priority: Optional priority filter (1=low, 2=medium, 3=high)
            tag_ids: Optional list of tag IDs to filter by (tasks must have ALL tags)
            search: Optional search query for title/description
            due_date_before: Optional due date upper bound
            due_date_after: Optional due date lower bound
            sort_by: Field to sort by (created_at, due_date, priority, title)
            sort_order: Sort direction (asc or desc)
            limit: Maximum tasks to return (default: 50)
            offset: Number of tasks to skip (default: 0)

        Returns:
            List of Task objects with tags loaded

        Example:
            # Get high priority incomplete tasks
            tasks = await service.get_user_tasks(
                user_id,
                is_complete=False,
                priority=Priority.HIGH
            )

            # Search tasks with keyword
            tasks = await service.get_user_tasks(
                user_id,
                search="urgent"
            )
        """
        # Build base query
        query = select(Task).where(Task.user_id == user_id)

        # Apply completion filter
        if is_complete is not None:
            query = query.where(Task.is_complete == is_complete)

        # Apply priority filter
        if priority is not None:
            query = query.where(Task.priority == priority)

        # Apply search filter (title or description)
        if search:
            search_term = f"%{search}%"
            query = query.where(
                (Task.title.ilike(search_term)) | (Task.description.ilike(search_term))
            )

        # Apply due date filters
        if due_date_before:
            query = query.where(Task.due_date <= due_date_before)
        if due_date_after:
            query = query.where(Task.due_date >= due_date_after)

        # Apply tag filter (tasks must have ALL specified tags)
        if tag_ids:
            for tag_id in tag_ids:
                # Subquery to check if task has this tag
                tag_subquery = select(TaskTag).where(
                    TaskTag.task_id == Task.id,
                    TaskTag.tag_id == tag_id
                )
                query = query.where(tag_subquery.exists())

        # Apply sorting
        sort_field = self._get_sort_field(sort_by)
        if sort_order == "desc":
            query = query.order_by(sort_field.desc())
        else:
            query = query.order_by(sort_field.asc())

        # Apply pagination
        query = query.limit(limit).offset(offset)

        # Execute query with eager loading of tags
        tasks = self.session.exec(query).all()

        # Manually load tags for each task (SQLModel limitation)
        for task in tasks:
            tag_query = select(Tag).join(TaskTag).where(TaskTag.task_id == task.id)
            task.tags = list(self.session.exec(tag_query).all())

        return list(tasks)

    def _get_sort_field(self, sort_by: str):
        """
        Get the Task field for sorting.

        Args:
            sort_by: Field name to sort by

        Returns:
            Task field object

        Raises:
            ValueError: If sort field is invalid
        """
        valid_fields = {
            "created_at": Task.created_at,
            "due_date": Task.due_date,
            "priority": Task.priority,
            "title": Task.title,
            "updated_at": Task.updated_at,
        }

        if sort_by not in valid_fields:
            raise ValueError(
                f"Invalid sort field '{sort_by}'. Valid options: {', '.join(valid_fields.keys())}"
            )

        return valid_fields[sort_by]

    async def count_user_tasks(
        self,
        user_id: str,
        is_complete: Optional[bool] = None,
        priority: Optional[int] = None,
        tag_ids: Optional[List[str]] = None,
        search: Optional[str] = None,
        due_date_before: Optional[datetime] = None,
        due_date_after: Optional[datetime] = None,
    ) -> int:
        """
        Count total tasks matching filters (for pagination).

        Args:
            user_id: User ID to count tasks for
            is_complete: Optional completion status filter
            priority: Optional priority filter
            tag_ids: Optional list of tag IDs to filter by
            search: Optional search query
            due_date_before: Optional due date upper bound
            due_date_after: Optional due date lower bound

        Returns:
            Total count of matching tasks
        """
        from sqlmodel import func

        # Build base query (same as get_user_tasks)
        query = select(Task).where(Task.user_id == user_id)

        if is_complete is not None:
            query = query.where(Task.is_complete == is_complete)

        if priority is not None:
            query = query.where(Task.priority == priority)

        if search:
            search_term = f"%{search}%"
            query = query.where(
                (Task.title.ilike(search_term)) | (Task.description.ilike(search_term))
            )

        if due_date_before:
            query = query.where(Task.due_date <= due_date_before)
        if due_date_after:
            query = query.where(Task.due_date >= due_date_after)

        if tag_ids:
            for tag_id in tag_ids:
                tag_subquery = select(TaskTag).where(
                    TaskTag.task_id == Task.id,
                    TaskTag.tag_id == tag_id
                )
                query = query.where(tag_subquery.exists())

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        return self.session.exec(count_query).one()

    async def get_task(self, task_id: str, user_id: str) -> Task:
        """
        Get single task with ownership verification.

        Args:
            task_id: Task ID to retrieve
            user_id: User ID (for ownership check)

        Returns:
            Task object with tags loaded

        Raises:
            HTTPException 404: If task not found
            HTTPException 403: If task belongs to different user

        Example:
            task = await service.get_task(task_id, current_user.id)
        """
        task = self.session.get(Task, task_id)

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Ownership check
        if task.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to access this task",
            )

        # Load tags
        tag_query = select(Tag).join(TaskTag).where(TaskTag.task_id == task.id)
        task.tags = list(self.session.exec(tag_query).all())

        return task

    async def update_task(
        self, task_id: str, task_data: TaskUpdate, user_id: str
    ) -> Task:
        """
        Update task fields.

        Args:
            task_id: Task ID to update
            task_data: Fields to update (only provided fields are updated)
            user_id: User ID (for ownership check)

        Returns:
            Updated Task object

        Raises:
            HTTPException 404: If task not found
            HTTPException 403: If task belongs to different user

        Example:
            task = await service.update_task(
                task_id,
                TaskUpdate(title="Updated title"),
                current_user.id
            )
        """
        # Get task with ownership check
        task = await self.get_task(task_id, user_id)

        # Update only provided fields
        if task_data.title is not None:
            if not task_data.title.strip():
                raise ValueError("Title cannot be empty")
            task.title = task_data.title.strip()

        if task_data.description is not None:
            task.description = task_data.description.strip() if task_data.description else None

        if task_data.is_complete is not None:
            task.is_complete = task_data.is_complete

        if task_data.priority is not None:
            task.priority = task_data.priority

        if task_data.due_date is not None:
            task.due_date = task_data.due_date

        # Update timestamp
        task.updated_at = datetime.utcnow()

        # Persist changes
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        return task

    async def toggle_complete(
        self, task_id: str, is_complete: bool, user_id: str
    ) -> Task:
        """
        Toggle task completion status.

        Args:
            task_id: Task ID to toggle
            is_complete: New completion status
            user_id: User ID (for ownership check)

        Returns:
            Updated Task object

        Raises:
            HTTPException 404: If task not found
            HTTPException 403: If task belongs to different user

        Example:
            task = await service.toggle_complete(task_id, True, current_user.id)
        """
        # Get task with ownership check
        task = await self.get_task(task_id, user_id)

        # Update completion status
        task.is_complete = is_complete
        task.updated_at = datetime.utcnow()

        # Persist changes
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        return task

    async def delete_task(self, task_id: str, user_id: str) -> None:
        """
        Delete task.

        Also removes all task-tag associations for this task.

        Args:
            task_id: Task ID to delete
            user_id: User ID (for ownership check)

        Raises:
            HTTPException 404: If task not found
            HTTPException 403: If task belongs to different user

        Example:
            await service.delete_task(task_id, current_user.id)
        """
        # Get task with ownership check
        task = await self.get_task(task_id, user_id)

        # Delete task-tag associations first
        self.session.exec(
            select(TaskTag).where(TaskTag.task_id == task_id)
        ).all()

        # Delete associations
        for tt in self.session.exec(
            select(TaskTag).where(TaskTag.task_id == task_id)
        ).all():
            self.session.delete(tt)

        # Delete from database
        self.session.delete(task)
        self.session.commit()

    async def add_tag_to_task(
        self, task_id: str, tag_id: str, user_id: str
    ) -> Task:
        """
        Add a tag to a task.

        Args:
            task_id: Task ID
            tag_id: Tag ID to add
            user_id: User ID (for ownership check)

        Returns:
            Updated Task object

        Raises:
            HTTPException 404: If task or tag not found
            HTTPException 403: If task or tag belongs to different user
            ValueError: If tag is already on task

        Example:
            task = await service.add_tag_to_task(task_id, tag_id, user_id)
        """
        # Verify task ownership
        task = await self.get_task(task_id, user_id)

        # Verify tag ownership
        tag = self.session.get(Tag, tag_id)
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")
        if tag.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this tag")

        # Check if association already exists
        existing = self.session.exec(
            select(TaskTag).where(
                TaskTag.task_id == task_id,
                TaskTag.tag_id == tag_id
            )
        ).first()

        if existing:
            raise ValueError("Tag is already on this task")

        # Create association
        task_tag = TaskTag(task_id=task_id, tag_id=tag_id)
        self.session.add(task_tag)
        self.session.commit()
        self.session.refresh(task)

        return task

    async def remove_tag_from_task(
        self, task_id: str, tag_id: str, user_id: str
    ) -> Task:
        """
        Remove a tag from a task.

        Args:
            task_id: Task ID
            tag_id: Tag ID to remove
            user_id: User ID (for ownership check)

        Returns:
            Updated Task object

        Raises:
            HTTPException 404: If task not found
            HTTPException 403: If task belongs to different user
            ValueError: If tag is not on task

        Example:
            task = await service.remove_tag_from_task(task_id, tag_id, user_id)
        """
        # Verify task ownership
        task = await self.get_task(task_id, user_id)

        # Find and delete association
        task_tag = self.session.exec(
            select(TaskTag).where(
                TaskTag.task_id == task_id,
                TaskTag.tag_id == tag_id
            )
        ).first()

        if not task_tag:
            raise ValueError("Tag is not on this task")

        self.session.delete(task_tag)
        self.session.commit()
        self.session.refresh(task)

        return task

    async def set_task_tags(
        self, task_id: str, tag_ids: List[str], user_id: str
    ) -> Task:
        """
        Replace all tags on a task with new set of tags.

        Removes all existing tags and adds the provided tags.

        Args:
            task_id: Task ID
            tag_ids: List of tag IDs to set
            user_id: User ID (for ownership check)

        Returns:
            Updated Task object

        Raises:
            HTTPException 404: If task not found
            ValueError: If tag IDs don't belong to user

        Example:
            task = await service.set_task_tags(task_id, [tag_id1, tag_id2], user_id)
        """
        # Verify task ownership
        task = await self.get_task(task_id, user_id)

        # Verify tag ownership
        tags = self.session.exec(
            select(Tag).where(
                Tag.id.in_(tag_ids),
                Tag.user_id == user_id
            )
        ).all()

        if len(tags) != len(tag_ids):
            raise ValueError("One or more tag IDs are invalid or don't belong to user")

        # Remove all existing associations
        for tt in self.session.exec(
            select(TaskTag).where(TaskTag.task_id == task_id)
        ).all():
            self.session.delete(tt)

        # Add new associations
        for tag_id in tag_ids:
            task_tag = TaskTag(task_id=task_id, tag_id=tag_id)
            self.session.add(task_tag)

        self.session.commit()
        self.session.refresh(task)

        return task
