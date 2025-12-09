"""add_usr_phone_column_on_usr_table

Revision ID: d8227a7683e3
Revises: 38babc54f229
Create Date: 2025-12-09 10:54:24.294855

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd8227a7683e3'
down_revision: Union[str, Sequence[str], None] = '38babc54f229'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('usr_users', sa.Column('usr_phone', sa.String(20), nullable=True))



def downgrade() -> None:
    pass

