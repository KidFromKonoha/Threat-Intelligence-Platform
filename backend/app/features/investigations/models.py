"""Investigation ORM model.

Represents an analyst investigation. Investigations are persistent and shareable
workspaces that link indicators, threat actors, malware, campaigns, and assets.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.enums import InvestigationPriority, InvestigationStatus
from app.db.mixins import TimestampMixin
from app.db.session import Base


class Investigation(Base, TimestampMixin):
    """Represents an analyst investigation workspace."""

    __tablename__ = "investigations"

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        server_default=text("gen_random_uuid()::text"),
    )
    title: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Free-form owner identifier (username / email); auth is a future phase.
    owner: Mapped[str | None] = mapped_column(Text, nullable=True, index=True)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=InvestigationStatus.OPEN.value,
        index=True,
        comment="InvestigationStatus enum stored as string",
    )
    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=InvestigationPriority.MEDIUM.value,
        comment="InvestigationPriority enum stored as string",
    )
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    indicators: Mapped[list["Indicator"]] = relationship(
        "Indicator",
        secondary="investigation_indicator",
        back_populates="investigations",
    )
    threat_actors: Mapped[list["ThreatActor"]] = relationship(
        "ThreatActor",
        secondary="investigation_threat_actor",
        back_populates="investigations",
    )
    malware: Mapped[list["Malware"]] = relationship(
        "Malware",
        secondary="investigation_malware",
        back_populates="investigations",
    )
    campaigns: Mapped[list["Campaign"]] = relationship(
        "Campaign",
        secondary="investigation_campaign",
        back_populates="investigations",
    )
    assets: Mapped[list["Asset"]] = relationship(
        "Asset",
        secondary="investigation_asset",
        back_populates="investigations",
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="investigation",
        cascade="all, delete-orphan",
        foreign_keys="Comment.investigation_id",
    )

    def __repr__(self) -> str:
        return f"<Investigation id={self.id!r} title={self.title!r} status={self.status!r}>"
