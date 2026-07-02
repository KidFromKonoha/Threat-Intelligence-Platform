"""Watchlist ORM models.

Represents a user-defined monitoring rule and the matches it generates.
"""

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String, Text, UniqueConstraint, ARRAY, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    # Entity type being watched (indicator, domain, ipv4, threat_actor, etc.)
    watchlist_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    
    # Rule used for matching (e.g., 'exact', 'contains')
    matching_rule: Mapped[str] = mapped_column(String(50), nullable=False, default="exact")
    
    # The actual values to look for
    values: Mapped[list] = mapped_column(ARRAY(Text), nullable=False, server_default="{}")

    # Relationships
    matches: Mapped[list["WatchlistMatch"]] = relationship(
        "WatchlistMatch",
        back_populates="watchlist",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Watchlist id={self.id!r} name={self.name!r} type={self.watchlist_type!r}>"


class WatchlistMatch(Base, TimestampMixin):
    """Records an instance where an entity matched a watchlist."""

    __tablename__ = "watchlist_matches"

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        server_default=text("gen_random_uuid()::text"),
    )
    watchlist_id: Mapped[str] = mapped_column(
        Text, ForeignKey("watchlists.id", ondelete="CASCADE"), nullable=False, index=True
    )
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    match_reason: Mapped[str] = mapped_column(Text, nullable=False)

    watchlist: Mapped["Watchlist"] = relationship("Watchlist", back_populates="matches")

    __table_args__ = (
        UniqueConstraint("watchlist_id", "entity_type", "entity_id", name="uq_watchlist_match"),
    )

    def __repr__(self) -> str:
        return f"<WatchlistMatch watchlist_id={self.watchlist_id!r} entity={self.entity_type!r}:{self.entity_id!r}>"
