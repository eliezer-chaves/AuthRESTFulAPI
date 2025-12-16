"""add_email_verified_and_is_active_on_user_table

Revision ID: d72b8a4a9157
Revises: 8f18594e6efc
Create Date: 2025-12-16 08:37:33.856358

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Boolean


# revision identifiers, used by Alembic.
revision: str = 'd72b8a4a9157'
down_revision: Union[str, Sequence[str], None] = '8f18594e6efc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column(
        'usr_users',
        sa.Column(
            'usr_email_verified',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false')
        )
    )
    op.add_column(
        'usr_users',
        sa.Column(
            'usr_user_active',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false')
        )
    )


def downgrade() -> None:
    op.drop_column('usr_users', 'usr_user_active')
    op.drop_column('usr_users', 'usr_email_verified')