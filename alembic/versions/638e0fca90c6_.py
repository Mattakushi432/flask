"""empty message

Revision ID: 638e0fca90c6
Revises: 
Create Date: 2025-08-15 19:03:43.661942

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '638e0fca90c6'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()
    if 'users' in tables:
        existing_cols = [c['name'] for c in inspector.get_columns('users')]
        if 'country' not in existing_cols:
            op.add_column('users', sa.Column('country', sa.String(length=50), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()
    if 'users' in tables:
        existing_cols = [c['name'] for c in inspector.get_columns('users')]
        if 'country' in existing_cols:
            op.drop_column('users', 'country')
