"""Asset ORM model.

Represents an organization-owned resource. Assets enable relevance scoring —
when an indicator matches an asset, risk score increases.
"""

from __future__ import annotations

from sqlalchemy import ARRAY, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.enums import AssetCriticality, AssetType
from app.db.mixins import TimestampMixin
from app.db.session import Base


class Asset(Base, TimestampMixin):
    """Represents an organizational asset (IP, domain, product, etc.)."""

    __tablename__ = "assets"

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        server_default=text("gen_random_uuid()::text"),
    )
    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="AssetType enum stored as string",
    )
    name: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    # The actual asset value (IP address, domain name, product name, etc.)
    value: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    owner: Mapped[str | None] = mapped_column(Text, nullable=True)
    criticality: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=AssetCriticality.MEDIUM.value,
        index=True,
        comment="AssetCriticality enum stored as string",
    )
    tags: Mapped[list | None] = mapped_column(ARRAY(Text), nullable=True)

    # ── Relationships ─────────────────────────────────────────────────────────
    indicators: Mapped[list] = relationship(
        "Indicator",
        secondary="indicator_asset",
        back_populates="assets",
    )
    investigations: Mapped[list] = relationship(
        "Investigation",
        secondary="investigation_asset",
        back_populates="assets",
    )

    def __repr__(self) -> str:
        return f"<Asset id={self.id!r} type={self.type!r} value={self.value!r}>"
