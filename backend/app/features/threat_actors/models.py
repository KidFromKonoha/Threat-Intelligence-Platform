"""ThreatActor ORM model.

Represents an adversary or adversary group (nation-state, ransomware group,
criminal organization, or unknown cluster).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import ARRAY, JSON, Boolean, DateTime, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.enums import ThreatActorSophistication
from app.db.mixins import TimestampMixin
from app.db.session import Base


class ThreatActor(Base, TimestampMixin):
    """Represents a threat adversary."""

    __tablename__ = "threat_actors"

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        server_default=text("gen_random_uuid()::text"),
    )
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True, index=True)
    aliases: Mapped[list | None] = mapped_column(ARRAY(Text), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    country: Mapped[str | None] = mapped_column(String(2), nullable=True, index=True)
    motivation: Mapped[str | None] = mapped_column(Text, nullable=True)
    sophistication: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=ThreatActorSophistication.UNKNOWN.value,
        comment="ThreatActorSophistication enum stored as string",
    )
    first_seen: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_seen: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    references: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # ── Relationships ─────────────────────────────────────────────────────────
    indicators: Mapped[list] = relationship(
        "Indicator",
        secondary="indicator_threat_actor",
        back_populates="threat_actors",
    )
    malware: Mapped[list] = relationship(
        "Malware",
        secondary="threat_actor_malware",
        back_populates="threat_actors",
    )
    campaigns: Mapped[list] = relationship(
        "Campaign",
        secondary="threat_actor_campaign",
        back_populates="threat_actors",
    )
    techniques: Mapped[list] = relationship(
        "MITRETechnique",
        secondary="threat_actor_mitre_technique",
        back_populates="threat_actors",
    )
    reports: Mapped[list] = relationship(
        "Report",
        secondary="threat_actor_report",
        back_populates="threat_actors",
    )
    vulnerabilities: Mapped[list] = relationship(
        "Vulnerability",
        secondary="vulnerability_threat_actor",
        back_populates="threat_actors",
    )
    investigations: Mapped[list] = relationship(
        "Investigation",
        secondary="investigation_threat_actor",
        back_populates="threat_actors",
    )

    def __repr__(self) -> str:
        return f"<ThreatActor id={self.id!r} name={self.name!r}>"
