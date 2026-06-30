"""Watchlist ORM model.

Represents a user-defined monitoring rule. When new intelligence matches
the rule, a notification should be generated (notification delivery is a
future phase — the model captures the rule data only).
"""

from __future__ import annotations

from sqlalchemy import Boolean, JSON, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.mixins import TimestampMixin
from app.db.session import Base


class Watchlist(Base, TimestampMixin):
    """Represents a user-defined alert/monitoring criterion."""

    __tablename__ = "watchlists"

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        server_default=text("gen_random_uuid()::text"),
    )
    name: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Free-form owner identifier; auth is a future phase.
    owner: Mapped[str | None] = mapped_column(Text, nullable=True, index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    # JSON object describing the matching rule (field, operator, value).
    # Schema is intentionally flexible to support future rule expansion.
    matching_rule: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<Watchlist id={self.id!r} name={self.name!r} enabled={self.enabled!r}>"
