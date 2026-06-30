"""Vulnerability ORM model.

Represents a publicly disclosed vulnerability, identified by CVE. Includes
CVSS, EPSS, KEV (CISA Known Exploited Vulnerabilities), and exploitation data.
"""

from __future__ import annotations

from sqlalchemy import Boolean, Float, JSON, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.mixins import TimestampMixin
from app.db.session import Base


class Vulnerability(Base, TimestampMixin):
    """Represents a CVE or other publicly disclosed vulnerability."""

    __tablename__ = "vulnerabilities"

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        server_default=text("gen_random_uuid()::text"),
    )
    cve: Mapped[str] = mapped_column(
        String(30), nullable=False, unique=True, index=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # CVSS v3 base score (0.0–10.0)
    cvss: Mapped[float | None] = mapped_column(Float, nullable=True)
    # Exploit Prediction Scoring System probability (0.0–1.0)
    epss: Mapped[float | None] = mapped_column(Float, nullable=True)
    # Is it in CISA's Known Exploited Vulnerabilities catalogue?
    kev: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    exploited: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    patch_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    references: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # ── Relationships ─────────────────────────────────────────────────────────
    threat_actors: Mapped[list] = relationship(
        "ThreatActor",
        secondary="vulnerability_threat_actor",
        back_populates="vulnerabilities",
    )
    malware: Mapped[list] = relationship(
        "Malware",
        secondary="vulnerability_malware",
        back_populates="vulnerabilities",
    )
    campaigns: Mapped[list] = relationship(
        "Campaign",
        secondary="campaign_vulnerability",
        back_populates="vulnerabilities",
    )

    def __repr__(self) -> str:
        return f"<Vulnerability id={self.id!r} cve={self.cve!r}>"
