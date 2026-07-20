"""Dashboard API Router."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.features.dashboard.schemas import (
    DashboardOverviewResponse,
    DashboardThreatActivityResponse,
    DashboardOrganizationResponse,
    DashboardFeedStatusResponse,
    DashboardRecentIntelligenceResponse,
    DashboardIntelligenceSnapshotResponse,
    DashboardHighSeverityIntelligenceResponse,
    DashboardIocDistributionResponse,
    DashboardFeedContributionResponse,
    DashboardInvestigationSummaryResponse,
    
    # Phase 2.4 schemas
    DashboardIntelligenceHighlightsResponse,
    DashboardPriorityQueueResponse,
    DashboardInvestigationHealthResponse,
    DashboardWatchlistActivityResponse,
    DashboardGeospatialResponse,
    DashboardSupplyChainResponse
)
from app.features.dashboard.service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# ── General Operations ────────────────────────────────────────────────────────

@router.get("/overview", response_model=DashboardOverviewResponse)
def get_overview(db: Session = Depends(get_db)):
    """Get high-level dashboard metrics and overview."""
    return DashboardService.get_overview(db)

@router.get("/organization", response_model=DashboardOrganizationResponse)
def get_organization(db: Session = Depends(get_db)):
    """Get organization-specific threat metrics."""
    return DashboardService.get_organization(db)

@router.get("/feed-status", response_model=DashboardFeedStatusResponse)
def get_feed_status(db: Session = Depends(get_db)):
    """Get operational status and metrics for all feeds."""
    return DashboardService.get_feed_status(db)

@router.get("/feed-contribution", response_model=DashboardFeedContributionResponse)
def get_feed_contribution(db: Session = Depends(get_db)):
    """Get contribution (record count) per feed."""
    return DashboardService.get_feed_contribution(db)

@router.get("/threat-activity", response_model=DashboardThreatActivityResponse)
def get_threat_activity(days: Optional[int] = Query(30, description="Number of days for trend analysis"), db: Session = Depends(get_db)):
    """Get aggregate threat activity statistics."""
    return DashboardService.get_threat_activity(db, days=days)

@router.get("/geospatial", response_model=DashboardGeospatialResponse)
def get_geospatial_threats(days: int = 7, db: Session = Depends(get_db)):
    return DashboardService.get_geospatial_threats(db, days)

@router.get("/supply-chain", response_model=DashboardSupplyChainResponse)
def get_supply_chain_matrix(days: int = 30, db: Session = Depends(get_db)):
    return DashboardService.get_supply_chain_matrix(db, days)


# ── Operations ───────────────────────────────────────────────────────────────

@router.get("/operations/priority-queue", response_model=DashboardPriorityQueueResponse)
def get_priority_queue(db: Session = Depends(get_db)):
    """Get the priority queue of actionable items."""
    return DashboardService.get_priority_queue(db)

@router.get("/operations/health", response_model=DashboardInvestigationHealthResponse)
def get_investigation_health(db: Session = Depends(get_db)):
    """Get investigation health metrics."""
    return DashboardService.get_investigation_health(db)

@router.get("/alerts/priority", response_model=DashboardRecentIntelligenceResponse)
def get_priority_alerts(
    limit: int = Query(5, description="Number of alerts to return"),
    min_score: int = Query(50, description="Minimum risk score"),
    db: Session = Depends(get_db)
):
    """Get priority alerts sorted by risk score."""
    return DashboardService.get_priority_alerts(db, limit=limit, min_score=min_score)


# ── Intelligence ─────────────────────────────────────────────────────────────

@router.get("/intelligence/highlights", response_model=DashboardIntelligenceHighlightsResponse)
def get_intelligence_highlights(db: Session = Depends(get_db)):
    """Get intelligence operational highlights."""
    return DashboardService.get_intelligence_highlights(db)

@router.get("/intelligence/watchlist-activity", response_model=DashboardWatchlistActivityResponse)
def get_watchlist_activity(db: Session = Depends(get_db)):
    """Get today's watchlist activity."""
    return DashboardService.get_watchlist_activity(db)

@router.get("/intelligence/recent", response_model=DashboardRecentIntelligenceResponse)
def get_recent_intelligence(
    skip: int = Query(0, description="Pagination skip"),
    limit: int = Query(10, description="Pagination limit"),
    sort_by: str = Query('created_at', description="Sort column"),
    order: str = Query('desc', description="Sort order"),
    type_filter: Optional[str] = Query(None, description="Indicator type filter"),
    db: Session = Depends(get_db)
):
    """Get recent intelligence artifacts."""
    return DashboardService.get_recent_intelligence(
        db=db, skip=skip, limit=limit, sort_by=sort_by, order=order, type_filter=type_filter
    )

@router.get("/intelligence/ioc-distribution", response_model=DashboardIocDistributionResponse)
def get_ioc_distribution(db: Session = Depends(get_db)):
    """Get distribution of IOC types."""
    return DashboardService.get_ioc_distribution(db)


# ── Deprecated/Phase 2.3 Legacy endpoints ────────────────────────────────────

@router.get("/intelligence-snapshot", response_model=DashboardIntelligenceSnapshotResponse)
def get_intelligence_snapshot(db: Session = Depends(get_db)):
    return DashboardService.get_intelligence_snapshot(db)

@router.get("/high-severity", response_model=DashboardHighSeverityIntelligenceResponse)
def get_high_severity_intelligence(db: Session = Depends(get_db)):
    return DashboardService.get_high_severity_intelligence(db)

@router.get("/investigation-summary", response_model=DashboardInvestigationSummaryResponse)
def get_investigation_summary(db: Session = Depends(get_db)):
    return DashboardService.get_investigation_summary(db)

@router.get("/ioc-distribution", response_model=DashboardIocDistributionResponse)
def get_ioc_distribution_legacy(db: Session = Depends(get_db)):
    return DashboardService.get_ioc_distribution(db)

@router.get("/recent-intelligence", response_model=DashboardRecentIntelligenceResponse)
def get_recent_intelligence_legacy(db: Session = Depends(get_db)):
    return DashboardService.get_recent_intelligence(db)
