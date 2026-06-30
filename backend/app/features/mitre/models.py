"""MITRETechnique ORM model.

Represents an ATT&CK technique or sub-technique. Techniques describe attacker
behavior and are referenced by indicators, threat actors, malware, and campaigns.
"""

from __future__ import annotations

from sqlalchemy import String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class MITRETechnique(Base):
    """Represents a MITRE ATT&CK technique or sub-technique."""

    __tablename__ = "mitre_techniques"

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        server_default=text("gen_random_uuid()::text"),
    )
    # Official ATT&CK identifier, e.g. "T1059" or "T1059.001"
    technique_id: Mapped[str] = mapped_column(
        String(20), nullable=False, unique=True, index=True
    )
    tactic: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Relationships ─────────────────────────────────────────────────────────
    indicators: Mapped[list] = relationship(
        "Indicator",
        secondary="indicator_mitre_technique",
        back_populates="techniques",
    )
    threat_actors: Mapped[list] = relationship(
        "ThreatActor",
        secondary="threat_actor_mitre_technique",
        back_populates="techniques",
    )
    malware: Mapped[list] = relationship(
        "Malware",
        secondary="malware_mitre_technique",
        back_populates="techniques",
    )
    campaigns: Mapped[list] = relationship(
        "Campaign",
        secondary="campaign_mitre_technique",
        back_populates="techniques",
    )

    def __repr__(self) -> str:
        return f"<MITRETechnique id={self.id!r} technique_id={self.technique_id!r} name={self.name!r}>"
