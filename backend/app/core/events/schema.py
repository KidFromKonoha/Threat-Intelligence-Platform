from datetime import datetime, timezone
import uuid
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")

class EventEnvelope(BaseModel, Generic[T]):
    """Standardized event envelope as defined in Architecture v1.0."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_version: str = "1.0"
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    producer: str
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    payload: T

class IndicatorPersistedPayload(BaseModel):
    """Payload for the tip.events.indicator.persisted event."""
    indicator_id: str
    feed_id: str

class IndicatorEnrichedPayload(BaseModel):
    """Payload for the tip.events.indicator.enriched event."""
    indicator_id: str

class RelationshipsUpdatedPayload(BaseModel):
    """Payload for the tip.events.relationships.updated event."""
    indicator_id: str
    new_edges_count: int
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RiskScoreCalculatedPayload(BaseModel):
    """Payload for the tip.events.risk_score.calculated event."""
    indicator_id: str
    risk_score: int
    risk_score_version: int
