"""create email rate limits  table

Revision ID: d4165d43cfd7
Revises: 2cf037885739
Create Date: 2025-12-17 16:02:33.906427

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4165d43cfd7'
down_revision: Union[str, Sequence[str], None] = '2cf037885739'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'erl_email_rate_limits',
        sa.Column('erl_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('erl_email', sa.String(length=255), nullable=False),
        sa.Column('erl_ip_address', sa.String(length=45), nullable=True),
        sa.Column('erl_attempts', sa.Integer(), nullable=True),
        sa.Column('erl_first_attempt_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('erl_last_attempt_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('erl_blocked_until', sa.TIMESTAMP(), nullable=False),
        sa.Column('erl_created_at', sa.TIMESTAMP(), nullable=False),

        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )

    op.create_index(
        'ix_erl_email_rate_limits_erl_email',
        'erl_email_rate_limits',
        ['erl_email']
    )

    op.create_index(
        'ix_erl_email_rate_limits_erl_id',
        'erl_email_rate_limits',
        ['erl_id']
    )

    op.create_index(
        'ix_erl_email_rate_limits_erl_ip_address',
        'erl_email_rate_limits',
        ['erl_ip_address']
    )


def downgrade():
    op.drop_index('ix_erl_email_rate_limits_erl_ip_address', table_name='erl_email_rate_limits')
    op.drop_index('ix_erl_email_rate_limits_erl_id', table_name='erl_email_rate_limits')
    op.drop_index('ix_erl_email_rate_limits_erl_email', table_name='erl_email_rate_limits')
    op.drop_table('erl_email_rate_limits')