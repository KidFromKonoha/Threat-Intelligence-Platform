"""Schemas for the Dashboard APIs."""

from __future__ import annotations
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict
from typing import Any

from app.features.search.schemas import EntitySummary, IndicatorSummary


# ── Overview ─────────────────────────────────────────────────────────────────

class FeedHealthScore(BaseModel):
    healthy_feeds: int
    error_feeds: int
    total_active_feeds: int
    health_percentage: float


class DashboardOverviewResponse(BaseModel):
    total_indicators: int
    new_indicators_24h: int
    active_feeds: int
    feed_health: FeedHealthScore
    open_investigations: int


# ── Threat Activity ──────────────────────────────────────────────────────────

class DailyCount(BaseModel):
    date: str
    count: int


class TopEntity(BaseModel):
    id: str
    name: str
    count: int


class DashboardThreatActivityResponse(BaseModel):
    indicators_by_day: list[DailyCount]
    top_threat_actors: list[TopEntity]
    top_malware_families: list[TopEntity]
    top_campaigns: list[TopEntity]
    top_countries: list[TopEntity]
    top_mitre_techniques: list[TopEntity]


# ── Organization ─────────────────────────────────────────────────────────────

class DashboardOrganizationResponse(BaseModel):
    high_risk_asset_matches: int
    supplier_threats: int
    automotive_threats: int
    active_watchlist_matches: int


# ── Feed Status ──────────────────────────────────────────────────────────────

class FeedStatusDetail(BaseModel):
    id: str
    name: str
    status: str
    last_success: datetime | None = None
    last_failure: datetime | None = None
    records_imported: int = 0
    last_run_duration: float | None = None
    average_run_duration: float | None = None
    total_runs: int = 0
    failed_runs: int = 0
    
    model_config = ConfigDict(from_attributes=True)


class DashboardFeedStatusResponse(BaseModel):
    feeds: list[FeedStatusDetail]


# ── Recent Intelligence ──────────────────────────────────────────────────────

class DashboardRecentIntelligenceResponse(BaseModel):
    indicators: list[IndicatorSummary]
    campaigns: list[EntitySummary]
    malware: list[EntitySummary]
    threat_actors: list[EntitySummary]
    vulnerabilities: list[EntitySummary]
