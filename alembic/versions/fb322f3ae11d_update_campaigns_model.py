"""create campaigns table (decision log)

Revision ID: fb322f3ae11d
Revises:
Create Date: 2025-12-28 15:20:16.595917
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'fb322f3ae11d'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # CREATE campaigns table (clean, correct schema)
    op.create_table(
        'campaigns',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('product_id', sa.Integer, sa.ForeignKey('products.id'), nullable=True),
        sa.Column('intention_id', sa.Integer, nullable=True),
        sa.Column('channel', sa.String(length=100), nullable=False),
        sa.Column('context_note', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='نشطة'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('campaigns')
