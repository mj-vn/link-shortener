"""Add ttl to urls model

Revision ID: d40509613ba9
Revises: 02dc151cac48
Create Date: 2025-12-10 14:28:01.427903

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd40509613ba9'
down_revision: Union[str, Sequence[str], None] = '02dc151cac48'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('urls', sa.Column('ttl', sa.DateTime(), nullable=True))



def downgrade() -> None:
    op.drop_column('urls', 'ttl')
