"""add on delete cascade to floor desks fk

Revision ID: e5a9b8c7d6f0
Revises: 4867549d23cf
Create Date: 2026-04-22 11:30:45.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5a9b8c7d6f0'
down_revision: Union[str, Sequence[str], None] = '4867549d23cf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adds ON DELETE CASCADE to the foreign key from desks to floors."""
    # Drop the existing foreign key constraint (PostgreSQL default name is used)
    op.drop_constraint('desks_floor_id_fkey', 'desks', type_='foreignkey')
    # Recreate it with ON DELETE CASCADE
    op.create_foreign_key('desks_floor_id_fkey', 'desks', 'floors', ['floor_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    """Removes ON DELETE CASCADE from the foreign key from desks to floors."""
    # Drop the CASCADE constraint
    op.drop_constraint('desks_floor_id_fkey', 'desks', type_='foreignkey')
    # Recreate it without the CASCADE rule
    op.create_foreign_key('desks_floor_id_fkey', 'desks', 'floors', ['floor_id'], ['id'])