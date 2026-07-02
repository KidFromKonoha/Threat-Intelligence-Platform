"""Enrichment ORM model.

Stores the result of an enrichment provider execution for an indicator.
"""

from __future__ import annotations

from sqlalchemy import Float, ForeignKey, JSON, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.enums import EnrichmentStatus
from app.db.mixins import TimestampMixin
from app.db.session import Base


class EnrichmentResult(Base, TimestampMixin):
    """Stores the execution result of an enrichment provider."""

    __tablename__ = "enrichment_results"

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        server_default=text("gen_random_uuid()::text"),
    )
    provider: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    indicator_id: Mapped[str] = mapped_column(
        Text, ForeignKey("indicators.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # Store the raw response from the provider for troubleshooting/re-processing
    raw_response: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    # Store structured attributes extracted from the raw response
    extracted_attributes: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    execution_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=EnrichmentStatus.PENDING.value,
        index=True,
        comment="EnrichmentStatus enum value stored as string",
    )
    execution_duration: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Note: No back_populates on Indicator to keep the Indicator model decoupled 
    # from enrichment in this phase, as per Phase 6 "no unnecessary columns" rule.

    def __repr__(self) -> str:
        return f"<EnrichmentResult id={self.id!r} provider={self.provider!r} status={self.execution_status!r}>"
