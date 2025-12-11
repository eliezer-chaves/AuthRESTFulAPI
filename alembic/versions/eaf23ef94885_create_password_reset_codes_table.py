"""create password_reset_codes table

Revision ID: eaf23ef94885
Revises: d8227a7683e3
Create Date: 2025-12-11 14:17:58.686472

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eaf23ef94885'
down_revision: Union[str, Sequence[str], None] = 'd8227a7683e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.create_table(
        'psc_password_reset_codes',
        sa.Column('psc_id', sa.Integer, primary_key=True),
        sa.Column('psc_user_id', sa.Integer, sa.ForeignKey('usr_users.usr_id', ondelete='CASCADE')),
        sa.Column('psc_code', sa.String(6), nullable=False),
        sa.Column('psc_expires_at', sa.DateTime, nullable=False),
        sa.Column('psc_created_at', sa.DateTime, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table('psc_password_reset_codes')