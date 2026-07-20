"""Watchlists API router."""

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.features.watchlists.schemas import (
    WatchlistCreate,
    WatchlistUpdate,
    WatchlistResponse,
    WatchlistAlertResponse,
    WatchlistMetricsResponse
)
from app.features.watchlists.service import WatchlistService, WatchlistAlertService
from app.features.auth.dependencies import require_analyst
from app.features.users.models import User

router = APIRouter(prefix="/watchlists", tags=["Watchlists"])


@router.get("", response_model=list[WatchlistResponse])
def list_watchlists(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List all watchlists."""
    return WatchlistService.get_all(db, skip=skip, limit=limit)


@router.post("", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED)
def create_watchlist(
    data: WatchlistCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst)
):
    """Create a new watchlist."""
    return WatchlistService.create(db, data)


@router.get("/metrics", response_model=WatchlistMetricsResponse)
def get_metrics(db: Session = Depends(get_db)):
    """Get watchlist metrics."""
    return WatchlistAlertService.get_metrics(db)


@router.get("/alerts", response_model=list[WatchlistAlertResponse])
def list_alerts(
    indicator_id: str | None = None,
    status: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List all watchlist alerts."""
    return WatchlistAlertService.get_all(db, indicator_id=indicator_id, status=status, skip=skip, limit=limit)


@router.get("/alerts/{alert_id}", response_model=WatchlistAlertResponse)
def get_alert(alert_id: str, db: Session = Depends(get_db)):
    """Get a specific watchlist alert."""
    return WatchlistAlertService.get_by_id(db, alert_id)


@router.put("/alerts/{alert_id}/acknowledge", response_model=WatchlistAlertResponse)
def acknowledge_alert(
    alert_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst)
):
    """Acknowledge a watchlist alert."""
    return WatchlistAlertService.acknowledge(db, alert_id, current_user.id)


@router.get("/{watchlist_id}", response_model=WatchlistResponse)
def get_watchlist(watchlist_id: str, db: Session = Depends(get_db)):
    """Get a watchlist by ID."""
    return WatchlistService.get_by_id(db, watchlist_id)


@router.put("/{watchlist_id}", response_model=WatchlistResponse)
def update_watchlist(
    watchlist_id: str, 
    data: WatchlistUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst)
):
    """Update a watchlist."""
    return WatchlistService.update(db, watchlist_id, data)


@router.delete("/{watchlist_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_watchlist(
    watchlist_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst)
):
    """Delete a watchlist."""
    WatchlistService.delete(db, watchlist_id)
    return None
