"""Watchlist ORM models.

Represents a user-defined monitoring rule and the alerts it generates.
"""

from __future__ import annotations
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, String, Text, Integer, Float, JSON, UniqueConstraint, text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.mixins import TimestampMixin
from app.db.session import Base


class Watchlist(Base, TimestampMixin):
    """Represents a user-defined alert/monitoring criteria."""

    __tablename__ = "watchlists"

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        server_default=text("gen_random_uuid()::text"),
    )
    name: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    rules: Mapped[list["WatchlistRule"]] = relationship(
        "WatchlistRule",
        back_populates="watchlist",
        cascade="all, delete-orphan",
    )
    alerts: Mapped[list["WatchlistAlert"]] = relationship(
        "WatchlistAlert",
        back_populates="watchlist",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Watchlist id={self.id!r} name={self.name!r}>"


class WatchlistRule(Base):
    """A specific matching criteria rule belonging to a Watchlist."""

    __tablename__ = "watchlist_rules"

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        server_default=text("gen_random_uuid()::text"),
    )
    watchlist_id: Mapped[str] = mapped_column(
        Text, ForeignKey("watchlists.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # E.g., 'risk_score', 'indicator_type', 'threat_actor', 'campaign', 'country', 'asn', 'asset_match'
    rule_type: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # E.g., '>=', '==', 'in', 'contains'
    operator: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # The target value. Using JSON allows storing lists (for 'in') or strings/numbers.
    value: Mapped[dict | list | str | int | float | bool] = mapped_column(JSON, nullable=False)

    watchlist: Mapped["Watchlist"] = relationship("Watchlist", back_populates="rules")

    def __repr__(self) -> str:
        return f"<WatchlistRule rule_type={self.rule_type!r} op={self.operator!r}>"


class WatchlistAlert(Base):
    """An alert generated when an indicator matches a Watchlist."""

    __tablename__ = "watchlist_alerts"

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        server_default=text("gen_random_uuid()::text"),
    )
    watchlist_id: Mapped[str] = mapped_column(
        Text, ForeignKey("watchlists.id", ondelete="CASCADE"), nullable=False, index=True
    )
    indicator_id: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    
    severity: Mapped[str] = mapped_column(String(50), nullable=False, default="high")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="NEW") # NEW, ACKNOWLEDGED, CLOSED
    
    risk_score_snapshot: Mapped[float | None] = mapped_column(Float, nullable=True)
    matched_rule: Mapped[str | None] = mapped_column(Text, nullable=True)
    matched_value: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        onupdate=text("now()"),
        nullable=False,
    )
    
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    acknowledged_by: Mapped[str | None] = mapped_column(Text, nullable=True)

    watchlist: Mapped["Watchlist"] = relationship("Watchlist", back_populates="alerts")

    __table_args__ = (
        UniqueConstraint("watchlist_id", "indicator_id", name="uq_watchlist_alert"),
    )

    def __repr__(self) -> str:
        return f"<WatchlistAlert watchlist_id={self.watchlist_id!r} indicator_id={self.indicator_id!r}>"
