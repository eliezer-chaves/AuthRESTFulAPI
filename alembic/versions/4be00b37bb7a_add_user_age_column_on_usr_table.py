"""add user age column on usr_table

Revision ID: 4be00b37bb7a
Revises: a4490daac075
Create Date: 2025-12-05 10:51:08.871225

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4be00b37bb7a'
down_revision: Union[str, Sequence[str], None] = 'a4490daac075'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('usr_users', sa.Column('usr_age', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    pass
