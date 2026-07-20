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


# ── Snapshot ─────────────────────────────────────────────────────────────────

class TrendMetric(BaseModel):
    count: int
    trend: str  # 'up', 'down', 'flat'

class DashboardIntelligenceSnapshotResponse(BaseModel):
    new_indicators: TrendMetric
    new_threat_actors: TrendMetric
    new_malware: TrendMetric
    new_campaigns: TrendMetric
    new_reports: TrendMetric
    open_investigations: TrendMetric


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

class RecentIntelligenceItem(BaseModel):
    id: str
    type: str
    value: str
    severity: str
    confidence: int
    risk_score: int = 0
    source: str | None = None
    created_at: datetime
    tags: list[str] = []

class DashboardRecentIntelligenceResponse(BaseModel):
    items: list[RecentIntelligenceItem]
    total_count: int
    page: int
    has_next_page: bool

# ── High Severity Intelligence ───────────────────────────────────────────────

class DashboardHighSeverityIntelligenceResponse(BaseModel):
    indicators: list[IndicatorSummary]

# ── IOC Distribution ─────────────────────────────────────────────────────────

class IocDistribution(BaseModel):
    type: str
    count: int

class DashboardIocDistributionResponse(BaseModel):
    distribution: list[IocDistribution]

# ── Feed Contribution ────────────────────────────────────────────────────────

class FeedContribution(BaseModel):
    feed_name: str
    count: int

class DashboardFeedContributionResponse(BaseModel):
    contribution: list[FeedContribution]

# ── Investigation Summary ────────────────────────────────────────────────────

class DashboardInvestigationSummaryResponse(BaseModel):
    open: int
    high_priority: int
    closed: int
    recently_updated: int

# ── Intelligence Highlights ──────────────────────────────────────────────────

class Insight(BaseModel):
    id: str
    type: str  # e.g., 'spike', 'new_assignment', 'watchlist_hit'
    title: str
    description: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    metric: int | None = None
    trend: str | None = None  # 'up', 'down', 'flat'
    entity_type: str | None = None
    entity_id: str | None = None
    timestamp: datetime

class DashboardIntelligenceHighlightsResponse(BaseModel):
    insights: list[Insight]

# ── Priority Queue ───────────────────────────────────────────────────────────

class PriorityQueueItem(BaseModel):
    id: str
    icon: str  # e.g., 'alert-triangle', 'eye', 'shield'
    item_type: str  # e.g., 'investigation', 'watchlist_match', 'indicator'
    title: str
    subtitle: str
    priority: str  # 'high', 'critical'
    action: str  # e.g., 'Investigate', 'Acknowledge', 'Triage'
    timestamp: datetime
    reference_id: str | None = None

class DashboardPriorityQueueResponse(BaseModel):
    items: list[PriorityQueueItem]

# ── Investigation Health (Operations) ────────────────────────────────────────

class DashboardInvestigationHealthResponse(BaseModel):
    open: int
    high_priority: int
    overdue: int
    updated_today: int

# ── Watchlist Activity ───────────────────────────────────────────────────────

class WatchlistActivity(BaseModel):
    watchlist_id: str
    watchlist_name: str
    hits_today: int

class DashboardWatchlistActivityResponse(BaseModel):
    activities: list[WatchlistActivity]


# ── Geospatial & Supply Chain (Phase 1) ──────────────────────────────────────────

class GeospatialCountryCount(BaseModel):
    country: str
    count: int

class DashboardGeospatialResponse(BaseModel):
    countries: list[GeospatialCountryCount]

class SupplierThreatCount(BaseModel):
    supplier_id: str
    supplier_name: str
    threat_count: int

class DashboardSupplyChainResponse(BaseModel):
    suppliers: list[SupplierThreatCount]
