from typing import Any
from datetime import datetime
from pydantic import BaseModel, Field

class EntityEventSchema(BaseModel):
    id: str
    entity_type: str
    entity_id: str
    event_type: str
    payload: dict[str, Any] | None
    created_at: datetime
    
    class Config:
        from_attributes = True

class InvestigationIndicatorBundle(BaseModel):
    indicator: dict[str, Any]
    risk_score: int | None
    enrichment: list[dict[str, Any]]
    threat_actors: list[dict[str, Any]]
    campaigns: list[dict[str, Any]]
    malware: list[dict[str, Any]]
    mitre_techniques: list[dict[str, Any]]
    assets: list[dict[str, Any]]
    timeline: list[EntityEventSchema]

class InvestigationThreatActorBundle(BaseModel):
    threat_actor: dict[str, Any]
    indicators: list[dict[str, Any]]
    campaigns: list[dict[str, Any]]
    malware: list[dict[str, Any]]
    mitre_techniques: list[dict[str, Any]]

class InvestigationCampaignBundle(BaseModel):
    campaign: dict[str, Any]
    threat_actors: list[dict[str, Any]]
    indicators: list[dict[str, Any]]
    malware: list[dict[str, Any]]
    mitre_techniques: list[dict[str, Any]]

class UnifiedSearchResponse(BaseModel):
    indicators: list[dict[str, Any]] = Field(default_factory=list)
    threat_actors: list[dict[str, Any]] = Field(default_factory=list)
    campaigns: list[dict[str, Any]] = Field(default_factory=list)
    malware: list[dict[str, Any]] = Field(default_factory=list)
    assets: list[dict[str, Any]] = Field(default_factory=list)
