"""Add remind_at column to tasks table

Revision ID: 20250131_add_reminders_to_tasks
Revises: 20250131_add_due_dates_to_tasks
Create Date: 2025-01-31 00:00:00.000000

This migration adds a remind_at column to the tasks table to support
task reminders and notifications.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20250131_add_reminders_to_tasks"
down_revision: Union[str, Sequence[str], None] = "20250131_add_due_dates_to_tasks"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add remind_at column to tasks table with index."""
    # Add remind_at column (nullable, optional reminder timestamp)
    op.add_column(
        'tasks',
        sa.Column(
            'remind_at',
            sa.DateTime(timezone=True),
            nullable=True
        )
    )

    # Create index for querying upcoming reminders
    op.create_index(
        'ix_tasks_remind_at',
        'tasks',
        ['remind_at'],
        unique=False
    )


def downgrade() -> None:
    """Remove remind_at column from tasks table."""
    # Drop index
    op.drop_index('ix_tasks_remind_at', table_name='tasks')

    # Drop column
    op.drop_column('tasks', 'remind_at')
