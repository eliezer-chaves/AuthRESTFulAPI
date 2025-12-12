"""create_email_rate_limit_table

Revision ID: aaed62026e5e
Revises: 3e5638fc3adf
Create Date: 2025-12-12 10:43:11.734815

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime, timezone


# revision identifiers, used by Alembic.
revision: str = 'aaed62026e5e'
down_revision: Union[str, Sequence[str], None] = '3e5638fc3adf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def utcnow():
    return datetime.now(timezone.utc)


def upgrade():
    op.create_table(
        "erl_email_rate_limits",
        sa.Column("erl_id", sa.Integer, primary_key=True, index=True),
        sa.Column('erl_email', sa.String(length=255), nullable=False),
        sa.Column('erl_ip_address', sa.String(length=45), nullable=True),

        sa.Column("erl_attempts", sa.Integer, default=1),
        sa.Column("erl_first_attempt_at", sa.DateTime(
            timezone=True), default=utcnow),
        sa.Column("erl_last_attempt_at", sa.DateTime(
            timezone=True), default=utcnow),
        sa.Column("erl_blocked_until", sa.DateTime(
            timezone=True), nullable=True),
        sa.Column("erl_created_at", sa.DateTime(
            timezone=True), default=utcnow),
    )


def downgrade():
    op.drop_table("erl_email_rate_limits")
