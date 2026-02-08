"""
Tag Service

Business logic for tag CRUD operations.
Follows "fat services" pattern - all business logic lives here.
"""

import uuid
from typing import List, Optional

from fastapi import Depends, HTTPException
from sqlmodel import Session, select

from src.db.session import get_session
from src.models.tag import Tag, TagCreate, TagUpdate


class TagService:
    """
    Tag service handling tag CRUD operations.

    All business logic for tag management lives here, keeping
    route handlers thin and focused on HTTP concerns.
    """

    def __init__(self, session: Session = Depends(get_session)):
        """
        Initialize TagService with database session.

        Args:
            session: SQLModel database session (injected via FastAPI dependency)
        """
        self.session = session

    async def create_tag(
        self, tag_data: TagCreate, user_id: str
    ) -> Tag:
        """
        Create new tag for user.

        Business logic:
        1. Validate tag name is unique for user
        2. Create tag with user ownership
        3. Persist to database

        Args:
            tag_data: Tag creation data (name, color)
            user_id: Owner user ID

        Returns:
            Created Tag object

        Raises:
            ValueError: If tag name already exists for user
            ValueError: If tag name is empty

        Example:
            service = TagService(session)
            tag = await service.create_tag(
                TagCreate(name="work", color="#3b82f6"),
                user_id=uuid.UUID("...")
            )
        """
        # Validate tag name not empty
        if not tag_data.name.strip():
            raise ValueError("Tag name cannot be empty")

        # Check if tag with same name already exists for user
        existing = self.session.exec(
            select(Tag).where(
                Tag.user_id == user_id,
                Tag.name == tag_data.name.strip().lower()
            )
        ).first()

        if existing:
            raise ValueError(f"Tag '{tag_data.name}' already exists")

        # Create tag
        tag = Tag(
            id=str(uuid.uuid4()),
            name=tag_data.name.strip().lower(),
            color=tag_data.color,
            user_id=user_id,
        )

        # Persist to database
        self.session.add(tag)
        self.session.commit()
        self.session.refresh(tag)

        return tag

    async def get_user_tags(self, user_id: str) -> List[Tag]:
        """
        Get all tags for user.

        Args:
            user_id: User ID to get tags for

        Returns:
            List of Tag objects sorted by name (alphabetically)

        Example:
            tags = await service.get_user_tags(user_id)
        """
        query = select(Tag).where(Tag.user_id == user_id).order_by(Tag.name)

        tags = self.session.exec(query).all()
        return list(tags)

    async def get_tag(self, tag_id: str, user_id: str) -> Tag:
        """
        Get single tag with ownership verification.

        Args:
            tag_id: Tag ID to retrieve
            user_id: User ID (for ownership check)

        Returns:
            Tag object

        Raises:
            HTTPException 404: If tag not found
            HTTPException 403: If tag belongs to different user

        Example:
            tag = await service.get_tag(tag_id, current_user.id)
        """
        tag = self.session.get(Tag, tag_id)

        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")

        # Ownership check
        if tag.user_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to access this tag",
            )

        return tag

    async def update_tag(
        self, tag_id: str, tag_data: TagUpdate, user_id: str
    ) -> Tag:
        """
        Update tag fields.

        Args:
            tag_id: Tag ID to update
            tag_data: Fields to update (only provided fields are updated)
            user_id: User ID (for ownership check)

        Returns:
            Updated Tag object

        Raises:
            HTTPException 404: If tag not found
            HTTPException 403: If tag belongs to different user
            ValueError: If new tag name already exists for user

        Example:
            tag = await service.update_tag(
                tag_id,
                TagUpdate(name="personal", color="#22c55e"),
                current_user.id
            )
        """
        # Get tag with ownership check
        tag = await self.get_tag(tag_id, user_id)

        # Update only provided fields
        if tag_data.name is not None:
            new_name = tag_data.name.strip().lower()

            # Check if new name conflicts with existing tag
            existing = self.session.exec(
                select(Tag).where(
                    Tag.user_id == user_id,
                    Tag.name == new_name,
                    Tag.id != tag_id  # Exclude current tag
                )
            ).first()

            if existing:
                raise ValueError(f"Tag '{tag_data.name}' already exists")

            tag.name = new_name

        if tag_data.color is not None:
            tag.color = tag_data.color

        # Persist changes
        self.session.add(tag)
        self.session.commit()
        self.session.refresh(tag)

        return tag

    async def delete_tag(self, tag_id: str, user_id: str) -> None:
        """
        Delete tag.

        Also removes all task-tag associations for this tag.

        Args:
            tag_id: Tag ID to delete
            user_id: User ID (for ownership check)

        Raises:
            HTTPException 404: If tag not found
            HTTPException 403: If tag belongs to different user

        Example:
            await service.delete_tag(tag_id, current_user.id)
        """
        # Get tag with ownership check
        tag = await self.get_tag(tag_id, user_id)

        # Delete from database (cascade will handle task_tags)
        self.session.delete(tag)
        self.session.commit()

    async def get_or_create_tag(
        self, name: str, color: str, user_id: str
    ) -> Tag:
        """
        Get existing tag by name or create new one.

        Convenience method for tag selection in task forms.
        If tag with given name exists, return it. Otherwise create new tag.

        Args:
            name: Tag name
            color: Tag color (used only if creating new tag)
            user_id: Owner user ID

        Returns:
            Tag object (existing or newly created)

        Example:
            tag = await service.get_or_create_tag("urgent", "#ef4444", user_id)
        """
        # Try to find existing tag
        existing = self.session.exec(
            select(Tag).where(
                Tag.user_id == user_id,
                Tag.name == name.strip().lower()
            )
        ).first()

        if existing:
            return existing

        # Create new tag
        tag_data = TagCreate(name=name, color=color)
        return await self.create_tag(tag_data, user_id)

    async def get_tags_by_ids(
        self, tag_ids: List[str], user_id: str
    ) -> List[Tag]:
        """
        Get multiple tags by IDs with ownership verification.

        Only returns tags that belong to the user.

        Args:
            tag_ids: List of tag IDs to retrieve
            user_id: Owner user ID

        Returns:
            List of Tag objects (only those owned by user)

        Example:
            tags = await service.get_tags_by_ids(["id1", "id2"], user_id)
        """
        if not tag_ids:
            return []

        query = select(Tag).where(
            Tag.id.in_(tag_ids),
            Tag.user_id == user_id
        )

        tags = self.session.exec(query).all()
        return list(tags)
