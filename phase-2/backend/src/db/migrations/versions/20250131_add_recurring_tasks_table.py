"""Add recurring_tasks table

Revision ID: 20250131_add_recurring_tasks_table
Revises: 20250131_add_tags_tables
Create Date: 2025-01-31 00:00:00.000000

This migration creates a recurring_tasks table to support auto-generated
recurring tasks. When a recurring task template exists, the system can
automatically create new task instances based on the recurrence rule.

Key features:
- Templates for recurring tasks (e.g., "Weekly team meeting")
- Next due date calculation for automatic task generation
- Active/inactive toggle to pause recurrence
- Support for complex recurrence patterns (daily, weekly, monthly, etc.)
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20250131_add_recurring_tasks_table"
down_revision: Union[str, Sequence[str], None] = "20250131_add_tags_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create recurring_tasks table with constraints and indexes."""
    # Create recurring_tasks table
    op.create_table(
        'recurring_tasks',
        sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('title', sqlmodel.sql.sqltypes.AutoString(length=200), nullable=False),
        sa.Column('description', sqlmodel.sql.sqltypes.AutoString(length=2000), nullable=True),
        sa.Column('priority', sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False, server_default='medium'),
        sa.Column(
            'recurrence_rule',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False
        ),
        sa.Column('next_due_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='fk_recurring_tasks_user_id'),
        sa.PrimaryKeyConstraint('id', name='pk_recurring_tasks')
    )

    # CHECK constraint for valid priority values
    op.create_check_constraint(
        'ck_recurring_tasks_priority_valid',
        'recurring_tasks',
        "priority IN ('low', 'medium', 'high', 'urgent')"
    )

    # Index for querying user's recurring tasks
    op.create_index(
        'ix_recurring_tasks_user_id',
        'recurring_tasks',
        ['user_id'],
        unique=False
    )

    # Composite index for querying upcoming due tasks (for cron job)
    op.create_index(
        'ix_recurring_tasks_user_id_next_due_at',
        'recurring_tasks',
        ['user_id', 'next_due_at'],
        unique=False
    )

    # Index for filtering active recurring tasks
    op.create_index(
        'ix_recurring_tasks_is_active',
        'recurring_tasks',
        ['is_active'],
        unique=False
    )

    # GIN index for recurrence_rule JSONB queries
    op.create_index(
        'ix_recurring_tasks_recurrence_rule',
        'recurring_tasks',
        ['recurrence_rule'],
        unique=False,
        postgresql_using='gin'
    )

    # Create trigger function to update updated_at timestamp
    # This function will be called automatically on row updates
    op.execute("""
        CREATE OR REPLACE FUNCTION update_recurring_tasks_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger to call the function before each update
    op.execute("""
        CREATE TRIGGER trigger_update_recurring_tasks_updated_at
        BEFORE UPDATE ON recurring_tasks
        FOR EACH ROW
        EXECUTE FUNCTION update_recurring_tasks_updated_at();
    """)


def downgrade() -> None:
    """Remove recurring_tasks table and associated objects."""
    # Drop trigger
    op.execute("""
        DROP TRIGGER IF EXISTS trigger_update_recurring_tasks_updated_at
        ON recurring_tasks
    """)

    # Drop trigger function
    op.execute("""
        DROP FUNCTION IF EXISTS update_recurring_tasks_updated_at()
    """)

    # Drop indexes
    op.drop_index('ix_recurring_tasks_recurrence_rule', table_name='recurring_tasks')
    op.drop_index('ix_recurring_tasks_is_active', table_name='recurring_tasks')
    op.drop_index('ix_recurring_tasks_user_id_next_due_at', table_name='recurring_tasks')
    op.drop_index('ix_recurring_tasks_user_id', table_name='recurring_tasks')

    # Drop CHECK constraint
    op.drop_constraint('ck_recurring_tasks_priority_valid', 'recurring_tasks', type_='check')

    # Drop table
    op.drop_table('recurring_tasks')
