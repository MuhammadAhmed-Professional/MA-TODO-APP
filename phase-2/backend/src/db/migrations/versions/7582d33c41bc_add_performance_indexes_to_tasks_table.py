"""Add performance indexes to tasks table

Revision ID: 7582d33c41bc
Revises: ba7aa1f810b4
Create Date: 2025-12-12 12:57:27.439317

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7582d33c41bc'
down_revision: Union[str, Sequence[str], None] = 'ba7aa1f810b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add performance indexes for common query patterns."""
    # Add index on title for search functionality
    op.create_index(
        op.f('ix_tasks_title'),
        'tasks',
        ['title'],
        unique=False
    )

    # Add index on created_at for sorting by creation date
    op.create_index(
        op.f('ix_tasks_created_at'),
        'tasks',
        ['created_at'],
        unique=False
    )

    # Add index on updated_at for sorting by last update
    op.create_index(
        op.f('ix_tasks_updated_at'),
        'tasks',
        ['updated_at'],
        unique=False
    )

    # Composite index on user_id + created_at for efficient user task queries
    op.create_index(
        'ix_tasks_user_id_created_at',
        'tasks',
        ['user_id', 'created_at'],
        unique=False
    )

    # Composite index on user_id + is_complete for filtered queries
    op.create_index(
        'ix_tasks_user_id_is_complete',
        'tasks',
        ['user_id', 'is_complete'],
        unique=False
    )


def downgrade() -> None:
    """Remove performance indexes."""
    op.drop_index('ix_tasks_user_id_is_complete', table_name='tasks')
    op.drop_index('ix_tasks_user_id_created_at', table_name='tasks')
    op.drop_index(op.f('ix_tasks_updated_at'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_created_at'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_title'), table_name='tasks')
