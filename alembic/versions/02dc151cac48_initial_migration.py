"""Initial migration

Revision ID: 02dc151cac48
Revises: 
Create Date: 2025-11-29 17:08:05.030376

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '02dc151cac48'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        sa.schema.CreateSequence(
            sa.Sequence('url_id_seq', start=62**7, increment=1)
        )
    )
    op.create_table(
        'urls',
        sa.Column(
            'short_code',
            sa.BigInteger(),
            server_default=sa.text("nextval('url_id_seq')"),
            nullable=False
        ),
        sa.Column('original_url', sa.String(), nullable=False),
        sa.Column('clicked_count', sa.Integer(), nullable=False),
        sa.Column('modified_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('short_code')
    )
    op.create_table(
        'url_access_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('url_id', sa.BigInteger(), nullable=False),
        sa.Column('ip_address', sa.String(), nullable=False),
        sa.Column('user_agent', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['url_id'], ['urls.short_code'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        op.f('ix_url_access_logs_id'),
        'url_access_logs',
        ['id'],
        unique=False
    )
    op.create_index(
        op.f('ix_url_access_logs_url_id'),
        'url_access_logs',
        ['url_id'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_url_access_logs_url_id'), table_name='url_access_logs')
    op.drop_index(op.f('ix_url_access_logs_id'), table_name='url_access_logs')
    op.drop_table('url_access_logs')
    op.drop_table('urls')
    op.execute(
        sa.schema.DropSequence(sa.Sequence('url_id_seq'))
    )
