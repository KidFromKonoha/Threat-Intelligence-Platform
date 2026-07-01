"""search_indexes

Performance indexes added to support Phase 5 Search API:

  - ix_indicator_confidence   — sort/range filter on confidence score
  - ix_indicator_source_count — sort on source_count
  - ix_indicator_first_seen   — sort/range filter on first_seen timestamp
  - ix_indicator_last_seen    — sort/range filter on last_seen timestamp

These columns are not covered by the existing composite unique index
(ix_indicator_type_normalized_value) or the scalar indexes added in
the foundation migration, so they require explicit DDL.

Revision ID: 830382a8ded4
Revises: 6d4d4982970a
Create Date: 2026-07-01 11:38:44.653191

"""
from collections.abc import Sequence

from alembic import op


revision: str = "830382a8ded4"
down_revision: str | None = "6d4d4982970a"
branch_labels: Sequence[str] | str | None = None
depends_on: Sequence[str] | str | None = None


def upgrade() -> None:
    op.create_index(
        "ix_indicator_confidence", "indicators", ["confidence"], unique=False
    )
    op.create_index(
        "ix_indicator_source_count", "indicators", ["source_count"], unique=False
    )
    op.create_index(
        "ix_indicator_first_seen", "indicators", ["first_seen"], unique=False
    )
    op.create_index(
        "ix_indicator_last_seen", "indicators", ["last_seen"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_indicator_last_seen", table_name="indicators")
    op.drop_index("ix_indicator_first_seen", table_name="indicators")
    op.drop_index("ix_indicator_source_count", table_name="indicators")
    op.drop_index("ix_indicator_confidence", table_name="indicators")
