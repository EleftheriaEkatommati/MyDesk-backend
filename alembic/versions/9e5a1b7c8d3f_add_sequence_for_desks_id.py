"""add sequence for desks id

Revision ID: 9e5a1b7c8d3f
Revises: 4033d94ae4e1
Create Date: 2026-04-20 10:15:00.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e5a1b7c8d3f'
down_revision: Union[str, Sequence[str], None] = '4033d94ae4e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Sets up the auto-incrementing sequence for the desks.id primary key."""
    # This block ensures the sequence is created and linked to the desks.id column.
    # It's idempotent, so it's safe to run even if parts of it have been done before.
    op.execute("""
        DO $$
        BEGIN
            CREATE SEQUENCE IF NOT EXISTS desks_id_seq;
            ALTER TABLE desks ALTER COLUMN id SET DEFAULT nextval('desks_id_seq'::regclass);
            ALTER SEQUENCE desks_id_seq OWNED BY desks.id;
        END
        $$;
    """)


def downgrade() -> None:
    """Removes the auto-incrementing sequence setup."""
    # This block safely removes the sequence and the default value.
    op.execute("ALTER TABLE desks ALTER COLUMN id DROP DEFAULT;")
    op.execute("DROP SEQUENCE IF EXISTS desks_id_seq;")