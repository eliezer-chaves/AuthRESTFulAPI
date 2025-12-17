"""update column hash token name

Revision ID: 96970d2c9c2a
Revises: 772c5769c66f
Create Date: 2025-12-17 14:57:36.898883

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '96970d2c9c2a'
down_revision: Union[str, Sequence[str], None] = '772c5769c66f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("""
        ALTER TABLE ect_email_confirmation_token
        RENAME COLUMN ect_hash_token TO ect_token
    """)

def downgrade():
    op.execute("""
        ALTER TABLE ect_email_confirmation_token
        RENAME COLUMN ect_hash_token TO ect_token
    """)
