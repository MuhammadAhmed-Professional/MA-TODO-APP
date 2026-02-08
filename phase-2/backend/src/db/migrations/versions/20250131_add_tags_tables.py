"""Add tags and task_tags junction table

Revision ID: 20250131_add_tags_tables
Revises: 20250131_add_recurrence_to_tasks
Create Date: 2025-01-31 00:00:00.000000

This migration adds tags support for tasks:
- tags table: Stores user-defined tags with names and colors
- task_tags junction table: Many-to-many relationship between tasks and tags

This enables users to categorize and organize tasks with custom tags.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = "20250131_add_tags_tables"
down_revision: Union[str, Sequence[str], None] = "20250131_add_recurrence_to_tasks"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create tags and task_tags tables with constraints and indexes."""
    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('color', sqlmodel.sql.sqltypes.AutoString(length=7), nullable=False, server_default='#007bff'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='fk_tags_user_id'),
        sa.PrimaryKeyConstraint('id', name='pk_tags')
    )

    # Unique constraint: each user can have only one tag with a given name
    op.create_index(
        'ix_tags_user_id_name',
        'tags',
        ['user_id', 'name'],
        unique=True
    )

    # Index for querying user's tags
    op.create_index(
        'ix_tags_user_id',
        'tags',
        ['user_id'],
        unique=False
    )

    # Create task_tags junction table (many-to-many relationship)
    op.create_table(
        'task_tags',
        sa.Column('task_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('tag_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(
            ['task_id'],
            ['tasks.id'],
            name='fk_task_tags_task_id',
            ondelete='CASCADE'  # If task is deleted, remove tag associations
        ),
        sa.ForeignKeyConstraint(
            ['tag_id'],
            ['tags.id'],
            name='fk_task_tags_tag_id',
            ondelete='CASCADE'  # If tag is deleted, remove associations
        ),
        sa.PrimaryKeyConstraint('task_id', 'tag_id', name='pk_task_tags')
    )

    # Composite unique index (prevents duplicate tag assignments)
    op.create_index(
        'ix_task_tags_task_tag',
        'task_tags',
        ['task_id', 'tag_id'],
        unique=True
    )

    # Index for querying tags for a specific task
    op.create_index(
        'ix_task_tags_task_id',
        'task_tags',
        ['task_id'],
        unique=False
    )

    # Index for querying tasks with a specific tag
    op.create_index(
        'ix_task_tags_tag_id',
        'task_tags',
        ['tag_id'],
        unique=False
    )


def downgrade() -> None:
    """Remove tags and task_tags tables."""
    # Drop task_tags junction table (must be dropped first due to FK)
    op.drop_index('ix_task_tags_tag_id', table_name='task_tags')
    op.drop_index('ix_task_tags_task_id', table_name='task_tags')
    op.drop_index('ix_task_tags_task_tag', table_name='task_tags')
    op.drop_table('task_tags')

    # Drop tags table
    op.drop_index('ix_tags_user_id', table_name='tags')
    op.drop_index('ix_tags_user_id_name', table_name='tags')
    op.drop_table('tags')
