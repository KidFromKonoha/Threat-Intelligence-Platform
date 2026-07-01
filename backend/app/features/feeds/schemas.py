"""Internal normalized data schemas for the feed collection framework.

These schemas represent the canonical internal format that every collector
must produce.  No raw feed format ever crosses this boundary.

Design:
- RawIndicator is the single normalized record type produced by all collectors.
- All fields match the Indicator ORM model columns exactly.
- Pydantic v2 is used for validation before any DB write.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.db.enums import IndicatorStatus, IndicatorType, Severity


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


class RawIndicator(BaseModel):
    """Normalized indicator produced by a collector after its normalize() step.

    Every field maps directly to the Indicator ORM model.  Collectors must
    produce this type — the storage pipeline handles the DB write.
    """

    type: IndicatorType
    value: str = Field(..., min_length=1)
    normalized_value: str = Field(..., min_length=1)
    confidence: int = Field(default=50, ge=0, le=100)
    severity: Severity = Severity.MEDIUM
    risk_score: int = Field(default=0, ge=0, le=100)
    status: IndicatorStatus = IndicatorStatus.ACTIVE
    first_seen: datetime = Field(default_factory=_utcnow)
    last_seen: datetime = Field(default_factory=_utcnow)

    # Optional enrichment fields — populated only when available from source.
    country: str | None = None
    asn: str | None = None
    tags: list[str] | None = None

    # Raw source payload preserved for auditing; never exposed to the app layer.
    raw: dict[str, Any] | None = None

    @field_validator("normalized_value", mode="before")
    @classmethod
    def strip_normalized(cls, v: str) -> str:
        return v.strip().lower() if isinstance(v, str) else v

    @field_validator("country", mode="before")
    @classmethod
    def uppercase_country(cls, v: str | None) -> str | None:
        return v.upper()[:2] if isinstance(v, str) and v else v

    model_config = {"use_enum_values": True}


class CollectorMetrics(BaseModel):
    """Metrics captured by the runner for a single collector execution."""

    feed_name: str
    records_received: int = 0
    records_added: int = 0
    records_updated: int = 0
    records_skipped: int = 0
    errors: list[str] = Field(default_factory=list)
    duration_seconds: float = 0.0
