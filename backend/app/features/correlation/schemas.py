"""Pydantic schemas for the Correlation API.

GET /indicators/{id}/relationships  →  RelationshipsResponse
GET /indicators/{id}/related        →  RelatedIndicatorsResponse
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


# ── Indicator anchor ───────────────────────────────────────────────────────────

class IndicatorAnchor(BaseModel):
    """Minimal self-representation of the indicator being correlated."""

    id: str
    type: str
    value: str
    confidence: int
    severity: str

    model_config = {"from_attributes": True}


# ── Related-entity summaries (reused across both endpoints) ───────────────────

class FeedRef(BaseModel):
    id: str
    name: str
    type: str

    model_config = {"from_attributes": True}


class MalwareRef(BaseModel):
    id: str
    name: str
    category: str | None = None

    model_config = {"from_attributes": True}


class CampaignRef(BaseModel):
    id: str
    name: str

    model_config = {"from_attributes": True}


class ThreatActorRef(BaseModel):
    id: str
    name: str
    country: str | None = None

    model_config = {"from_attributes": True}


class MitreTechniqueRef(BaseModel):
    id: str
    technique_id: str
    name: str
    tactic: str

    model_config = {"from_attributes": True}


class ReportRef(BaseModel):
    id: str
    title: str
    author: str | None = None

    model_config = {"from_attributes": True}


class VulnerabilityRef(BaseModel):
    id: str
    cve: str
    cvss: float | None = None
    kev: bool = False

    model_config = {"from_attributes": True}


# ── GET /indicators/{id}/relationships ────────────────────────────────────────

class RelationshipsResponse(BaseModel):
    """Full relationship graph for a single indicator."""

    indicator:       IndicatorAnchor
    feeds:           list[FeedRef]           = []
    malware:         list[MalwareRef]        = []
    campaigns:       list[CampaignRef]       = []
    threat_actors:   list[ThreatActorRef]    = []
    mitre_techniques: list[MitreTechniqueRef] = []
    reports:         list[ReportRef]         = []
    vulnerabilities: list[VulnerabilityRef]  = []


# ── GET /indicators/{id}/related ──────────────────────────────────────────────

class SharedContext(BaseModel):
    """Describes which shared entities link two indicators together."""

    malware:      list[str] = []   # names
    campaigns:    list[str] = []
    threat_actors: list[str] = []
    reports:      list[str] = []
    feeds:        list[str] = []


class RelatedIndicatorResponse(BaseModel):
    """A single indicator related to the anchor, with its overlap context."""

    id: str
    type: str
    value: str
    confidence: int
    severity: str
    first_seen: datetime
    last_seen: datetime
    shared_count: int             # total number of shared relationships
    shared_context: SharedContext  # which entities are shared

    model_config = {"from_attributes": True}


class RelatedIndicatorsResponse(BaseModel):
    """Ranked list of indicators that share relationships with the anchor."""

    indicator:   IndicatorAnchor
    related:     list[RelatedIndicatorResponse]
    total_found: int
