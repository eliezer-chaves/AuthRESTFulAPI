"""remove  user age column on usr_table

Revision ID: 38babc54f229
Revises: 4be00b37bb7a
Create Date: 2025-12-05 10:52:25.071980

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '38babc54f229'
down_revision: Union[str, Sequence[str], None] = '4be00b37bb7a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('usr_users', 'usr_age')


def downgrade() -> None:
    """Downgrade schema."""
    pass
