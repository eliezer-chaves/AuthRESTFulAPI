"""create refresh tokens table

Revision ID: 0ee200f04a1f
Revises: 2cf037885739
Create Date: 2025-12-26 17:06:27.289358

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0ee200f04a1f'
down_revision: Union[str, Sequence[str], None] = '2cf037885739'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.create_table(
        'rft_refresh_tokens',
        sa.Column('rft_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('rft_user_id', sa.Integer(), nullable=False),
        sa.Column('rft_hash_token', sa.String(length=255), nullable=False),
        sa.Column('rft_expires_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('rft_revoked_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('rft_created_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('rft_last_used_at', sa.TIMESTAMP(), nullable=False),

        sa.ForeignKeyConstraint(
            ['rft_user_id'],
            ['usr_users.usr_id'],
            ondelete='CASCADE'
        ),
        
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )

    op.create_index(
        'ix_rft_hash_token', 
        'rft_refresh_tokens', 
        ['rft_hash_token'], 
        unique=True
    )

def downgrade():
    op.drop_index('ix_rft_hash_token', table_name='rft_refresh_tokens')
    op.drop_table('rft_refresh_tokens')