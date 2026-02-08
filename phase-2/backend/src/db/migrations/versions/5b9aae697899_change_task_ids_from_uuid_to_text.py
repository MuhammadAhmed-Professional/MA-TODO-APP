"""change task ids from uuid to text

Revision ID: 5b9aae697899
Revises: 003_add_conversation_tables
Create Date: 2025-12-28 05:19:38.933760

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '5b9aae697899'
down_revision: Union[str, Sequence[str], None] = '003_add_conversation_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - change tasks table UUID columns to TEXT."""
    # Step 1: Drop foreign key constraint (it prevents type change)
    op.drop_constraint('tasks_user_id_fkey', 'tasks', type_='foreignkey')

    # Step 2: Change tasks.id from uuid to text
    op.execute("ALTER TABLE tasks ALTER COLUMN id TYPE text USING id::text")

    # Step 3: Change tasks.user_id from uuid to text
    op.execute("ALTER TABLE tasks ALTER COLUMN user_id TYPE text USING user_id::text")

    # Step 4: Recreate foreign key (user.id is already text from Better Auth)
    op.create_foreign_key('tasks_user_id_fkey', 'tasks', 'user', ['user_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema - revert tasks table TEXT columns to UUID."""
    # Revert tasks.id from text to uuid
    op.execute("ALTER TABLE tasks ALTER COLUMN id TYPE uuid USING id::uuid")

    # Revert tasks.user_id from text to uuid
    op.execute("ALTER TABLE tasks ALTER COLUMN user_id TYPE uuid USING user_id::uuid")
