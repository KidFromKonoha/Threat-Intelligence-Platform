"""Campaign ORM model.

Represents a coordinated malicious operation. Campaigns connect threat actors,
malware, indicators, and victims.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import ARRAY, JSON, DateTime, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.mixins import TimestampMixin
from app.db.session import Base


class Campaign(Base, TimestampMixin):
    """Represents a coordinated malicious operation."""

    __tablename__ = "campaigns"

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        server_default=text("gen_random_uuid()::text"),
    )
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    first_seen: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_seen: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # Stored as JSON arrays to allow multiple sectors/countries.
    target_sector: Mapped[list | None] = mapped_column(ARRAY(Text), nullable=True)
    target_country: Mapped[list | None] = mapped_column(ARRAY(Text), nullable=True)
    references: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # ── Relationships ─────────────────────────────────────────────────────────
    indicators: Mapped[list] = relationship(
        "Indicator",
        secondary="indicator_campaign",
        back_populates="campaigns",
    )
    threat_actors: Mapped[list] = relationship(
        "ThreatActor",
        secondary="threat_actor_campaign",
        back_populates="campaigns",
    )
    malware: Mapped[list] = relationship(
        "Malware",
        secondary="malware_campaign",
        back_populates="campaigns",
    )
    vulnerabilities: Mapped[list] = relationship(
        "Vulnerability",
        secondary="campaign_vulnerability",
        back_populates="campaigns",
    )
    techniques: Mapped[list] = relationship(
        "MITRETechnique",
        secondary="campaign_mitre_technique",
        back_populates="campaigns",
    )
    reports: Mapped[list] = relationship(
        "Report",
        secondary="campaign_report",
        back_populates="campaigns",
    )
    investigations: Mapped[list] = relationship(
        "Investigation",
        secondary="investigation_campaign",
        back_populates="campaigns",
    )

    def __repr__(self) -> str:
        return f"<Campaign id={self.id!r} name={self.name!r}>"
