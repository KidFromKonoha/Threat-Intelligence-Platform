"""Indicator ORM model.

An Indicator represents an observable that may indicate malicious activity.
It is the primary searchable object on the platform.

Enum values are stored as VARCHAR strings rather than PostgreSQL native ENUM
types so that new values can be added without requiring a DDL migration.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    ARRAY,
    JSON,
    CheckConstraint,
    DateTime,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.enums import IndicatorStatus, IndicatorType, Severity
from app.db.mixins import TimestampMixin
from app.db.session import Base


class Indicator(Base, TimestampMixin):
    """Represents a threat observable (IP, domain, hash, URL, etc.)."""

    __tablename__ = "indicators"

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        server_default=text("gen_random_uuid()::text"),
    )
    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="IndicatorType enum value stored as string",
    )
    value: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_value: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    confidence: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=Severity.MEDIUM.value,
        comment="Severity enum value stored as string",
    )
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=IndicatorStatus.ACTIVE.value,
        index=True,
        comment="IndicatorStatus enum value stored as string",
    )
    first_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )

    # Optional enrichment fields
    country: Mapped[str | None] = mapped_column(String(2), nullable=True, index=True)
    asn: Mapped[str | None] = mapped_column(String(20), nullable=True)
    whois: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    passive_dns: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    reputation: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    tags: Mapped[list | None] = mapped_column(ARRAY(Text), nullable=True)

    source_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # ── Relationships ─────────────────────────────────────────────────────────
    threat_actors: Mapped[list] = relationship(
        "ThreatActor",
        secondary="indicator_threat_actor",
        back_populates="indicators",
    )
    malware: Mapped[list] = relationship(
        "Malware",
        secondary="indicator_malware",
        back_populates="indicators",
    )
    campaigns: Mapped[list] = relationship(
        "Campaign",
        secondary="indicator_campaign",
        back_populates="indicators",
    )
    techniques: Mapped[list] = relationship(
        "MITRETechnique",
        secondary="indicator_mitre_technique",
        back_populates="indicators",
    )
    assets: Mapped[list] = relationship(
        "Asset",
        secondary="indicator_asset",
        back_populates="indicators",
    )
    reports: Mapped[list] = relationship(
        "Report",
        secondary="indicator_report",
        back_populates="indicators",
    )
    feeds: Mapped[list] = relationship(
        "Feed",
        secondary="indicator_feed",
        back_populates="indicators",
    )
    investigations: Mapped[list] = relationship(
        "Investigation",
        secondary="investigation_indicator",
        back_populates="indicators",
    )

    __table_args__ = (
        CheckConstraint("confidence BETWEEN 0 AND 100", name="ck_indicator_confidence"),
        CheckConstraint("risk_score BETWEEN 0 AND 100", name="ck_indicator_risk_score"),
        # Deduplication key: same type+value is always the same indicator.
        Index("ix_indicator_type_normalized_value", "type", "normalized_value", unique=True),
    )

    def __repr__(self) -> str:
        return f"<Indicator id={self.id!r} type={self.type!r} value={self.value!r}>"
