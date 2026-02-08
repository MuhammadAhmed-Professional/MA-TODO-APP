"""Add due_date column to tasks table

Revision ID: 20250131_add_due_dates_to_tasks
Revises: 20250131_add_priority_to_tasks
Create Date: 2025-01-31 00:00:00.000000

This migration adds a due_date column to the tasks table to support
task deadlines and scheduling.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20250131_add_due_dates_to_tasks"
down_revision: Union[str, Sequence[str], None] = "20250131_add_priority_to_tasks"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add due_date column to tasks table with index."""
    # Add due_date column (nullable, optional deadline)
    op.add_column(
        'tasks',
        sa.Column(
            'due_date',
            sa.DateTime(timezone=True),
            nullable=True
        )
    )

    # Create index for filtering and sorting by due date
    op.create_index(
        'ix_tasks_due_date',
        'tasks',
        ['due_date'],
        unique=False
    )


def downgrade() -> None:
    """Remove due_date column from tasks table."""
    # Drop index
    op.drop_index('ix_tasks_due_date', table_name='tasks')

    # Drop column
    op.drop_column('tasks', 'due_date')
