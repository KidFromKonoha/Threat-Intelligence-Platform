"""Enrichment API schemas."""

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class EnrichmentSummary(BaseModel):
    """Summary of a single provider's enrichment execution."""

    provider: str
    execution_status: str
    execution_duration: float | None = None
    created_at: datetime
    extracted_attributes: dict | None = None
    
    model_config = ConfigDict(from_attributes=True)


class EnrichmentStatusResponse(BaseModel):
    """Response schema for GET /indicators/{id}/enrichment"""

    indicator_id: str
    providers_executed: int
    last_enrichment_at: datetime | None = None
    results: list[EnrichmentSummary]
