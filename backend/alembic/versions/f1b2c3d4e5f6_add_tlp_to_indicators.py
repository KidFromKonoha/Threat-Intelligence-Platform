"""add_tlp_to_indicators

Revision ID: f1b2c3d4e5f6
Revises: 5acb6156270b
Create Date: 2026-07-14 10:00:00.000000

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = 'f1b2c3d4e5f6'
down_revision: str | None = 'd034091383d6'
branch_labels: Sequence[str] | str | None = None
depends_on: Sequence[str] | str | None = None


def upgrade() -> None:
    op.add_column('indicators', sa.Column('tlp', sa.String(length=10), nullable=True))
    op.create_index(op.f('ix_indicators_tlp'), 'indicators', ['tlp'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_indicators_tlp'), table_name='indicators')
    op.drop_column('indicators', 'tlp')
