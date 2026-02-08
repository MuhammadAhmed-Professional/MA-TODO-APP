"""
Task-Tag Association Table

Many-to-many relationship between tasks and tags.
A task can have multiple tags, and a tag can be applied to multiple tasks.
"""

from sqlmodel import Field, SQLModel


class TaskTag(SQLModel, table=True):
    """
    Task-Tag association table (many-to-many).

    Links tasks to tags. A single task can have multiple tags,
    and a single tag can be applied to multiple tasks.

    Composite primary key ensures the same tag is not applied
    to the same task multiple times.

    Attributes:
        task_id: Foreign key to tasks table (part of composite PK)
        tag_id: Foreign key to tags table (part of composite PK)

    Example:
        # Tag a task with "work" and "urgent" tags
        TaskTag(task_id="...", tag_id="work_tag_id")
        TaskTag(task_id="...", tag_id="urgent_tag_id")
    """

    __tablename__ = "task_tags"

    # Better Auth uses string IDs
    task_id: str = Field(
        foreign_key="tasks.id",
        primary_key=True,
        description="Task ID (part of composite primary key)",
    )
    tag_id: str = Field(
        foreign_key="tags.id",
        primary_key=True,
        description="Tag ID (part of composite primary key)",
    )

    class Config:
        """SQLModel configuration"""

        json_schema_extra = {
            "example": {
                "task_id": "650e8400-e29b-41d4-a716-446655440001",
                "tag_id": "750e8400-e29b-41d4-a716-446655440002",
            }
        }
