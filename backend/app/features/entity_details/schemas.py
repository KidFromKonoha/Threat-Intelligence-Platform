"""Schemas for Entity Detail APIs."""

from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Any

from app.features.search.schemas import EntitySummary, IndicatorSummary


# ── Common ───────────────────────────────────────────────────────────────────

class TimelineEvent(BaseModel):
    event_type: str
    description: str
    timestamp: datetime


# ── Indicator Detail ─────────────────────────────────────────────────────────

class EnrichmentData(BaseModel):
    provider: str
    status: str
    data: dict | None = None
    timestamp: datetime


class IndicatorFullDetailResponse(BaseModel):
    # Metadata
    id: str
    type: str
    value: str
    confidence: int
    severity: str
    risk_score: int
    status: str
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    tags: list[str] | None = None
    created_at: datetime
    updated_at: datetime

    # Related
    feed_sources: list[EntitySummary] = []
    related_indicators: list[IndicatorSummary] = []
    threat_actors: list[EntitySummary] = []
    malware: list[EntitySummary] = []
    campaigns: list[EntitySummary] = []
    vulnerabilities: list[EntitySummary] = []
    assets: list[EntitySummary] = []
    mitre_techniques: list[EntitySummary] = []
    
    # Enrichment
    whois: dict | None = None
    passive_dns: list | None = None
    enrichments: list[EnrichmentData] = []
    
    timeline: list[TimelineEvent] = []
    comments: list[dict] = []
    
    model_config = ConfigDict(from_attributes=True)


# ── Threat Actor Detail ──────────────────────────────────────────────────────

class ThreatActorDetailResponse(BaseModel):
    id: str
    name: str
    aliases: list[str] | None = None
    description: str | None = None
    motivation: str | None = None
    country: str | None = None
    sophistication: str
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    created_at: datetime
    updated_at: datetime
    references: list[str] | None = None

    campaigns: list[EntitySummary] = []
    malware: list[EntitySummary] = []
    indicators: list[IndicatorSummary] = []
    mitre_techniques: list[EntitySummary] = []
    
    timeline: list[TimelineEvent] = []

    model_config = ConfigDict(from_attributes=True)


# ── Malware Detail ───────────────────────────────────────────────────────────

class MalwareDetailResponse(BaseModel):
    id: str
    name: str
    aliases: list[str] | None = None
    family: str | None = None
    category: str | None = None
    description: str | None = None
    capabilities: list[str] | None = None
    persistence: str | None = None
    communication: str | None = None
    created_at: datetime
    updated_at: datetime

    campaigns: list[EntitySummary] = []
    threat_actors: list[EntitySummary] = []
    indicators: list[IndicatorSummary] = []
    mitre_techniques: list[EntitySummary] = []
    
    timeline: list[TimelineEvent] = []

    model_config = ConfigDict(from_attributes=True)


# ── Campaign Detail ──────────────────────────────────────────────────────────

class CampaignDetailResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    created_at: datetime
    updated_at: datetime
    references: list[str] | None = None

    threat_actors: list[EntitySummary] = []
    malware: list[EntitySummary] = []
    indicators: list[IndicatorSummary] = []
    reports: list[EntitySummary] = []
    
    timeline: list[TimelineEvent] = []

    model_config = ConfigDict(from_attributes=True)


# ── Vulnerability Detail ─────────────────────────────────────────────────────

class VulnerabilityDetailResponse(BaseModel):
    id: str
    cve: str
    description: str | None = None
    cvss: float | None = None
    epss: float | None = None
    kev: bool
    exploited: bool
    patch_available: bool
    created_at: datetime
    updated_at: datetime
    references: list[str] | None = None

    threat_actors: list[EntitySummary] = []
    malware: list[EntitySummary] = []
    campaigns: list[EntitySummary] = []
    
    timeline: list[TimelineEvent] = []

    model_config = ConfigDict(from_attributes=True)
