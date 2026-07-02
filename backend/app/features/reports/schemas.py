"""Schemas for Reporting Engine."""

from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel


class ReportPlatformOverview(BaseModel):
    total_indicators: int
    new_indicators: int
    active_feeds: int
    feed_health_percentage: float
    open_investigations: int
    active_watchlist_matches: int


class TopEntityStats(BaseModel):
    name: str
    count: int


class ReportThreatIntelligence(BaseModel):
    top_malware: list[TopEntityStats]
    top_threat_actors: list[TopEntityStats]
    top_campaigns: list[TopEntityStats]
    top_mitre_techniques: list[TopEntityStats]
    top_vulnerabilities: list[TopEntityStats]
    most_active_countries: list[TopEntityStats]


class InvestigationStats(BaseModel):
    total: int
    open: int
    closed: int


class InvestigationSummary(BaseModel):
    id: str
    title: str
    status: str
    created_at: datetime
    closed_at: datetime | None


class ReportInvestigations(BaseModel):
    open_investigations: list[InvestigationSummary]
    recently_created: list[InvestigationSummary]
    recently_closed: list[InvestigationSummary]
    statistics: InvestigationStats


class FeedStat(BaseModel):
    name: str
    status: str
    total_imports: int
    failed_runs: int
    average_runtime_seconds: float


class ReportFeedStatistics(BaseModel):
    feeds: list[FeedStat]


class ReportResponse(BaseModel):
    report_type: str
    generated_at: datetime
    platform_overview: ReportPlatformOverview
    threat_intelligence: ReportThreatIntelligence
    investigations: ReportInvestigations
    feed_statistics: ReportFeedStatistics
