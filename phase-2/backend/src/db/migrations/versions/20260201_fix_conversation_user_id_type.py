"""Change conversations and messages user_id from UUID to TEXT

Better Auth uses non-UUID string IDs (e.g. 'p2776Z8HHiUv8GxFHnuso20ALer4HHWy'),
but the conversation tables were created with user_id as UUID type.
This migration changes them to TEXT to match the user table and task table.

Revision ID: 20260201_fix_conv_uid
Revises: 20260131_023941
Create Date: 2026-02-01 11:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260201_fix_conv_uid"
down_revision: Union[str, Sequence[str], None] = "20260131_023941"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Change user_id columns from UUID to TEXT in conversations and messages."""
    # Drop foreign key constraints first
    op.execute(
        "ALTER TABLE conversations DROP CONSTRAINT IF EXISTS conversations_user_id_fkey"
    )
    op.execute(
        "ALTER TABLE messages DROP CONSTRAINT IF EXISTS messages_user_id_fkey"
    )

    # Change column types from UUID to TEXT
    op.execute(
        "ALTER TABLE conversations ALTER COLUMN user_id TYPE TEXT USING user_id::TEXT"
    )
    op.execute(
        "ALTER TABLE messages ALTER COLUMN user_id TYPE TEXT USING user_id::TEXT"
    )

    # Re-add foreign key constraints
    op.execute(
        'ALTER TABLE conversations ADD CONSTRAINT conversations_user_id_fkey '
        'FOREIGN KEY (user_id) REFERENCES "user"(id)'
    )
    op.execute(
        'ALTER TABLE messages ADD CONSTRAINT messages_user_id_fkey '
        'FOREIGN KEY (user_id) REFERENCES "user"(id)'
    )


def downgrade() -> None:
    """Revert user_id columns from TEXT back to UUID."""
    op.execute(
        "ALTER TABLE conversations DROP CONSTRAINT IF EXISTS conversations_user_id_fkey"
    )
    op.execute(
        "ALTER TABLE messages DROP CONSTRAINT IF EXISTS messages_user_id_fkey"
    )

    op.execute(
        "ALTER TABLE conversations ALTER COLUMN user_id TYPE UUID USING user_id::UUID"
    )
    op.execute(
        "ALTER TABLE messages ALTER COLUMN user_id TYPE UUID USING user_id::UUID"
    )

    op.execute(
        'ALTER TABLE conversations ADD CONSTRAINT conversations_user_id_fkey '
        'FOREIGN KEY (user_id) REFERENCES "user"(id)'
    )
    op.execute(
        'ALTER TABLE messages ADD CONSTRAINT messages_user_id_fkey '
        'FOREIGN KEY (user_id) REFERENCES "user"(id)'
    )
