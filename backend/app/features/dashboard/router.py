"""Dashboard API Router."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.features.dashboard.schemas import (
    DashboardOverviewResponse,
    DashboardThreatActivityResponse,
    DashboardOrganizationResponse,
    DashboardFeedStatusResponse,
    DashboardRecentIntelligenceResponse,
)
from app.features.dashboard.service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/overview", response_model=DashboardOverviewResponse)
def get_overview(db: Session = Depends(get_db)):
    """Get high-level dashboard metrics and overview."""
    return DashboardService.get_overview(db)


@router.get("/threat-activity", response_model=DashboardThreatActivityResponse)
def get_threat_activity(db: Session = Depends(get_db)):
    """Get aggregate threat activity statistics."""
    return DashboardService.get_threat_activity(db)


@router.get("/organization", response_model=DashboardOrganizationResponse)
def get_organization(db: Session = Depends(get_db)):
    """Get organization-specific threat metrics."""
    return DashboardService.get_organization(db)


@router.get("/feed-status", response_model=DashboardFeedStatusResponse)
def get_feed_status(db: Session = Depends(get_db)):
    """Get operational status and metrics for all feeds."""
    return DashboardService.get_feed_status(db)


@router.get("/recent-intelligence", response_model=DashboardRecentIntelligenceResponse)
def get_recent_intelligence(db: Session = Depends(get_db)):
    """Get recently added intelligence artifacts."""
    return DashboardService.get_recent_intelligence(db)
