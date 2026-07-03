"""Watchlists API router."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.features.watchlists.schemas import (
    WatchlistCreate,
    WatchlistUpdate,
    WatchlistResponse,
    WatchlistMatchResponse,
)
from app.features.watchlists.service import WatchlistService

router = APIRouter(prefix="/watchlists", tags=["Watchlists"])


@router.get("", response_model=list[WatchlistResponse])
def list_watchlists(db: Session = Depends(get_db)):
    """List all watchlists."""
    return WatchlistService.get_all(db)


from app.features.auth.dependencies import require_analyst
from app.features.users.models import User

@router.post("", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED)
def create_watchlist(
    data: WatchlistCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst)
):
    """Create a new watchlist."""
    return WatchlistService.create(db, data)


@router.get("/matches", response_model=list[WatchlistMatchResponse])
def list_matches(db: Session = Depends(get_db)):
    """List all watchlist matches."""
    return WatchlistService.get_matches(db)


@router.get("/matches/{match_id}", response_model=WatchlistMatchResponse)
def get_match(match_id: str, db: Session = Depends(get_db)):
    """Get a specific watchlist match."""
    return WatchlistService.get_match_by_id(db, match_id)


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


@router.post("/{watchlist_id}/evaluate", response_model=list[WatchlistMatchResponse])
def evaluate_watchlist(
    watchlist_id: str, 
    indicator_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst)
):
    """Evaluate a specific indicator against the watchlists."""
    # Note: Although the endpoint implies evaluating a single watchlist, 
    # it's usually better to evaluate an indicator against all active watchlists.
    # The requirement is to evaluate, so we use the generic evaluate_indicator method.
    return WatchlistService.evaluate_indicator(db, indicator_id)
