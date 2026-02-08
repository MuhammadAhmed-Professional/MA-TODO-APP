"""
add priority and tags to tasks

Revision ID: 20260131_023941
Revises: 5b9aae697899
Create Date: 2025-01-31 02:39:41.000000

This migration adds:
1. priority column to tasks table (default: 2/medium)
2. due_date column to tasks table (optional)
3. tags table (user-owned tags with name and color)
4. task_tags association table (many-to-many relationship)
5. Indexes for improved query performance
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260131_023941'
down_revision: Union[str, None] = '5b9aae697899'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add priority, due_date columns to tasks table,
    create tags table, and create task_tags association table.
    """
    # Add priority column to tasks table (default: 2 = medium)
    op.add_column(
        'tasks',
        sa.Column(
            'priority',
            sa.Integer(),
            server_default='2',
            nullable=False
        )
    )

    # Add due_date column to tasks table (optional)
    op.add_column(
        'tasks',
        sa.Column(
            'due_date',
            sa.DateTime(timezone=True),
            nullable=True
        )
    )

    # Create index on priority for filtering/sorting
    op.create_index(
        'ix_tasks_priority',
        'tasks',
        ['priority']
    )

    # Create index on due_date for filtering
    op.create_index(
        'ix_tasks_due_date',
        'tasks',
        ['due_date']
    )

    # Create tags table
    op.create_table(
        'tags',
        sa.Column(
            'id',
            sa.String(),
            primary_key=True
        ),
        sa.Column(
            'name',
            sa.String(length=50),
            nullable=False
        ),
        sa.Column(
            'color',
            sa.String(length=7),
            server_default='#3b82f6',
            nullable=False
        ),
        sa.Column(
            'user_id',
            sa.String(),
            sa.ForeignKey('user.id', ondelete='CASCADE'),
            nullable=False
        ),
        # Unique constraint: tag names must be unique per user
        sa.UniqueConstraint(
            'user_id',
            'name',
            name='uq_tags_user_name'
        )
    )

    # Create index on user_id for tag queries
    op.create_index(
        'ix_tags_user_id',
        'tags',
        ['user_id']
    )

    # Create task_tags association table (many-to-many)
    op.create_table(
        'task_tags',
        sa.Column(
            'task_id',
            sa.String(),
            sa.ForeignKey('tasks.id', ondelete='CASCADE'),
            primary_key=True
        ),
        sa.Column(
            'tag_id',
            sa.String(),
            sa.ForeignKey('tags.id', ondelete='CASCADE'),
            primary_key=True
        )
    )

    # Add full-text search index on title and description
    # Note: PostgreSQL uses GIN indexes for full-text search
    # For MySQL/MariaDB, use FULLTEXT index instead
    try:
        # Try PostgreSQL GIN index
        op.execute("""
            CREATE INDEX ix_tasks_title_gin ON tasks
            USING GIN (to_tsvector('english', title));
        """)
        op.execute("""
            CREATE INDEX ix_tasks_description_gin ON tasks
            USING GIN (to_tsvector('english', description));
        """)
    except Exception:
        # Fallback: Regular indexes for title and description
        op.create_index('ix_tasks_title', 'tasks', ['title'])
        op.create_index('ix_tasks_description', 'tasks', ['description'])


def downgrade() -> None:
    """
    Remove priority, due_date columns, tags table, and task_tags table.
    """
    # Drop full-text search indexes (PostgreSQL)
    try:
        op.execute('DROP INDEX IF EXISTS ix_tasks_title_gin;')
        op.execute('DROP INDEX IF EXISTS ix_tasks_description_gin;')
    except Exception:
        pass

    # Drop regular indexes if they exist
    try:
        op.drop_index('ix_tasks_title', table_name='tasks')
        op.drop_index('ix_tasks_description', table_name='tasks')
    except Exception:
        pass

    # Drop task_tags association table
    op.drop_table('task_tags')

    # Drop tags table
    op.drop_index('ix_tags_user_id', table_name='tags')
    op.drop_table('tags')

    # Drop indexes on tasks
    op.drop_index('ix_tasks_due_date', table_name='tasks')
    op.drop_index('ix_tasks_priority', table_name='tasks')

    # Remove columns from tasks table
    op.drop_column('tasks', 'due_date')
    op.drop_column('tasks', 'priority')
