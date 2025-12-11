"""add psc_used_at column

Revision ID: 3e5638fc3adf
Revises: eaf23ef94885
Create Date: 2025-12-11 14:59:55.587990

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e5638fc3adf'
down_revision: Union[str, Sequence[str], None] = 'eaf23ef94885'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "psc_password_reset_codes",
        sa.Column("psc_used_at", sa.DateTime(), nullable=True)
    )


def downgrade():
    op.drop_column("psc_password_reset_codes", "psc_used_at")