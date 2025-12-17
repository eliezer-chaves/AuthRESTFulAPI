"""create password reset codes table

Revision ID: 2cf037885739
Revises: 0c4f9a65af1b
Create Date: 2025-12-17 16:02:00.141819

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2cf037885739'
down_revision: Union[str, Sequence[str], None] = '0c4f9a65af1b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'psc_password_reset_codes',
        sa.Column('psc_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('psc_user_id', sa.Integer(), nullable=False),
        sa.Column('psc_code', sa.String(length=6), nullable=False),
        sa.Column('psc_expires_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('psc_used_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('psc_created_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('psc_reset_id', sa.String(length=36), nullable=False),

        sa.ForeignKeyConstraint(
            ['psc_user_id'],
            ['usr_users.usr_id'],
            name='psc_password_reset_codes_ibfk_1',
            ondelete='CASCADE'
        ),

        sa.UniqueConstraint(
            'psc_reset_id',
            name='ix_psc_password_reset_codes_psc_reset_id'
        ),

        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )

    op.create_index(
        'ix_psc_password_reset_codes_psc_id',
        'psc_password_reset_codes',
        ['psc_id']
    )

    op.create_index(
        'psc_user_id',
        'psc_password_reset_codes',
        ['psc_user_id']
    )


def downgrade():
    op.drop_index('psc_user_id', table_name='psc_password_reset_codes')
    op.drop_index('ix_psc_password_reset_codes_psc_id', table_name='psc_password_reset_codes')
    op.drop_table('psc_password_reset_codes')
