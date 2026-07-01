"""Pydantic schemas for the Global Search API (GET /search).

GlobalSearchResult aggregates lightweight summaries from all searchable
entity types. Each entity type returns at most `limit` results.
"""

from __future__ import annotations

from pydantic import BaseModel


class EntitySummary(BaseModel):
    """Minimal representation of any non-indicator searchable entity."""

    id: str
    name: str                 # Primary display field (title for reports, cve for vulns)
    entity_type: str          # Discriminator: "malware", "threat_actor", etc.
    description: str | None = None

    model_config = {"from_attributes": True}


class IndicatorSummary(BaseModel):
    """Minimal indicator representation for global search results."""

    id: str
    type: str
    value: str
    confidence: int
    severity: str
    entity_type: str = "indicator"

    model_config = {"from_attributes": True}


class GlobalSearchResult(BaseModel):
    """Top-level response for GET /search."""

    query: str
    total_hits: int

    indicators:    list[IndicatorSummary] = []
    malware:       list[EntitySummary]    = []
    threat_actors: list[EntitySummary]    = []
    campaigns:     list[EntitySummary]    = []
    reports:       list[EntitySummary]    = []
    techniques:    list[EntitySummary]    = []
    vulnerabilities: list[EntitySummary]  = []
