"""Add priority column to tasks table

Revision ID: 20250131_add_priority_to_tasks
Revises: 5b9aae697899
Create Date: 2025-01-31 00:00:00.000000

This migration adds a priority column to the tasks table to support
task prioritization (low, medium, high, urgent).
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = "20250131_add_priority_to_tasks"
down_revision: Union[str, Sequence[str], None] = "5b9aae697899"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add priority column to tasks table with constraints and index."""
    # Add priority column with CHECK constraint and default value
    op.add_column(
        'tasks',
        sa.Column(
            'priority',
            sqlmodel.sql.sqltypes.AutoString(length=20),
            nullable=False,
            server_default='medium'
        )
    )

    # Create CHECK constraint for valid priority values
    op.create_check_constraint(
        'ck_tasks_priority_valid',
        'tasks',
        "priority IN ('low', 'medium', 'high', 'urgent')"
    )

    # Create index for filtering by priority
    op.create_index(
        'ix_tasks_priority',
        'tasks',
        ['priority'],
        unique=False
    )


def downgrade() -> None:
    """Remove priority column from tasks table."""
    # Drop index
    op.drop_index('ix_tasks_priority', table_name='tasks')

    # Drop CHECK constraint
    op.drop_constraint('ck_tasks_priority_valid', 'tasks', type_='check')

    # Drop column
    op.drop_column('tasks', 'priority')
