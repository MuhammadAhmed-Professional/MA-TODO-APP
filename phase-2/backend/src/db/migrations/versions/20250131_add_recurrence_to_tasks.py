"""Add recurrence_rule column to tasks table

Revision ID: 20250131_add_recurrence_to_tasks
Revises: 20250131_add_reminders_to_tasks
Create Date: 2025-01-31 00:00:00.000000

This migration adds a recurrence_rule column to the tasks table to support
recurring tasks (daily, weekly, monthly, etc.).

The recurrence_rule uses JSONB format compatible with popular libraries:
{
  "frequency": "daily" | "weekly" | "monthly" | "yearly",
  "interval": 1,  // Every N days/weeks/months
  "days": ["mon", "wed", "fri"],  // For weekly recurrence
  "end_date": "2025-12-31T23:59:59Z"  // Optional end date
}
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20250131_add_recurrence_to_tasks"
down_revision: Union[str, Sequence[str], None] = "20250131_add_reminders_to_tasks"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add recurrence_rule column to tasks table with GIN index."""
    # Add recurrence_rule column (nullable, JSONB for complex recurrence rules)
    op.add_column(
        'tasks',
        sa.Column(
            'recurrence_rule',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True
        )
    )

    # Create GIN index for efficient JSONB queries
    # GIN indexes are ideal for JSONB containment and existence queries
    op.create_index(
        'ix_tasks_recurrence_rule',
        'tasks',
        ['recurrence_rule'],
        unique=False,
        postgresql_using='gin'
    )


def downgrade() -> None:
    """Remove recurrence_rule column from tasks table."""
    # Drop GIN index
    op.drop_index('ix_tasks_recurrence_rule', table_name='tasks')

    # Drop column
    op.drop_column('tasks', 'recurrence_rule')
