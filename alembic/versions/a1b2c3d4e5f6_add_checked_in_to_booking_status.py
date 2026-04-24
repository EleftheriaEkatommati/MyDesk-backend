"""add checked in to booking status

Revision ID: a1b2c3d4e5f6
Revises: e5a9b8c7d6f0
Create Date: 2026-04-23 10:00:00.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'e5a9b8c7d6f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adds CHECKED_IN to the bookingstatus enum type in PostgreSQL."""
    op.execute("ALTER TYPE bookingstatus ADD VALUE 'CHECKED_IN'")


def downgrade() -> None:
    """Downgrading by removing an enum value is complex and potentially destructive.
    It requires creating a new enum, updating all tables, dropping the old enum,
    and renaming the new one. For this reason, a direct downgrade is not supported here.
    """
    pass