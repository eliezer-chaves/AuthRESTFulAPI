"""add reset_id to password reset codes

Revision ID: 8f18594e6efc
Revises: aaed62026e5e
Create Date: 2025-12-13 16:10:54.014185

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8f18594e6efc'
down_revision: Union[str, Sequence[str], None] = 'aaed62026e5e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("psc_password_reset_codes", sa.Column("psc_reset_id", sa.String(length=36), nullable=True))
    op.create_index(
        "ix_psc_password_reset_codes_psc_reset_id",
        "psc_password_reset_codes",
        ["psc_reset_id"],
        unique=True
    )

def downgrade():
    op.drop_index(
        "ix_psc_password_reset_codes_psc_reset_id",
        table_name="psc_password_reset_codes"
    )

    op.drop_column("psc_password_reset_codes", "psc_reset_id")