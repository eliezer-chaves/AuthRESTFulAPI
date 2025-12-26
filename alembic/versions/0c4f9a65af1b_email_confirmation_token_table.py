"""email confirmation token table

Revision ID: 0c4f9a65af1b
Revises: f5dbc96d3811
Create Date: 2025-12-17 15:59:47.533881

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c4f9a65af1b'
down_revision: Union[str, Sequence[str], None] = 'f5dbc96d3811'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'ect_email_confirmation_token',
        sa.Column('ect_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('ect_user_id', sa.Integer(), nullable=False),
        sa.Column('ect_expires_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('ect_token', sa.String(length=255), nullable=False),

        sa.ForeignKeyConstraint(
            ['ect_user_id'],
            ['usr_users.usr_id'],
            name='ect_email_confirmation_token_ibfk_1',
            ondelete='CASCADE'
        ),

        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )

    op.create_index(
        'ix_ect_email_confirmation_token_ect_id',
        'ect_email_confirmation_token',
        ['ect_id']
    )

    op.create_index(
        'ix_ect_email_confirmation_token_ect_hash_token',
        'ect_email_confirmation_token',
        ['ect_token']
    )

    op.create_index(
        'ect_user_id',
        'ect_email_confirmation_token',
        ['ect_user_id']
    )


def downgrade():
    op.drop_index('ect_user_id', table_name='ect_email_confirmation_token')
    op.drop_index('ix_ect_email_confirmation_token_ect_hash_token', table_name='ect_email_confirmation_token')
    op.drop_index('ix_ect_email_confirmation_token_ect_id', table_name='ect_email_confirmation_token')
    op.drop_table('ect_email_confirmation_token')