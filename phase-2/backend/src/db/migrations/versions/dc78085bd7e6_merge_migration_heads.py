"""merge migration heads

Revision ID: dc78085bd7e6
Revises: 20250131_add_recurring_tasks_table, 20260201_fix_conv_uid
Create Date: 2026-02-08 20:02:43.721542

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dc78085bd7e6'
down_revision: Union[str, Sequence[str], None] = ('20250131_add_recurring_tasks_table', '20260201_fix_conv_uid')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
