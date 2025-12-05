"""add user table

Revision ID: a4490daac075
Revises: 
Create Date: 2025-12-05 10:42:02.106572

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4490daac075'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
     op.create_table(
        "usr_users",
        sa.Column("usr_id", sa.Integer, primary_key=True, index=True),
        sa.Column("usr_first_name", sa.String(length=100), nullable=False),
        sa.Column("usr_last_name", sa.String(length=100), nullable=False),
        sa.Column("usr_email", sa.String(length=80), unique=True, nullable=False),
        sa.Column("usr_password", sa.String(length=255), nullable=False),
    )



def downgrade() -> None:
    """Downgrade schema."""
    pass
