"""create usr_users table

Revision ID: f5dbc96d3811
Revises: 
Create Date: 2025-12-17 15:57:52.100082

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f5dbc96d3811'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'usr_users',
        sa.Column('usr_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('usr_first_name', sa.String(length=100), nullable=False),
        sa.Column('usr_last_name', sa.String(length=100), nullable=False),
        sa.Column('usr_phone', sa.String(length=20), nullable=True),
        sa.Column('usr_email', sa.String(length=80), nullable=False),
        sa.Column('usr_password', sa.String(length=255), nullable=False),
        sa.Column('usr_email_verified', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('usr_user_active', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.UniqueConstraint('usr_email', name='usr_email'),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )

    op.create_index(
        'ix_usr_users_usr_id',
        'usr_users',
        ['usr_id']
    )


def downgrade():
    op.drop_index('ix_usr_users_usr_id', table_name='usr_users')
    op.drop_table('usr_users')