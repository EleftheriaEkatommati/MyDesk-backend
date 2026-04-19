"""add_sequence_for_desks_id

Revision ID: 4867549d23cf
Revises: 9e5a1b7c8d3f
Create Date: 2026-04-19 21:48:30.939523

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4867549d23cf'
down_revision: Union[str, Sequence[str], None] = '9e5a1b7c8d3f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
