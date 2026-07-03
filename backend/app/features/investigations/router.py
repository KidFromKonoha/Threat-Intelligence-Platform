"""Investigations API Router."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.features.investigations.schemas import (
    InvestigationCreate,
    InvestigationUpdate,
    InvestigationResponse,
    InvestigationSummaryResponse,
    InvestigationTimelineEvent,
)
from app.features.investigations.service import InvestigationService

router = APIRouter(prefix="/investigations", tags=["Investigations"])


@router.get("", response_model=list[InvestigationResponse])
def get_investigations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Retrieve investigations."""
    return InvestigationService.get_investigations(db, skip=skip, limit=limit)


from app.features.auth.dependencies import require_analyst
from app.features.users.models import User

@router.post("", response_model=InvestigationResponse, status_code=status.HTTP_201_CREATED)
def create_investigation(
    inv_in: InvestigationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst)
):
    """Create a new investigation."""
    return InvestigationService.create_investigation(db, inv_in)


@router.get("/{investigation_id}", response_model=InvestigationResponse)
def get_investigation(
    investigation_id: str,
    db: Session = Depends(get_db)
):
    """Retrieve an investigation by ID."""
    return InvestigationService.get_investigation(db, investigation_id)


@router.put("/{investigation_id}", response_model=InvestigationResponse)
def update_investigation(
    investigation_id: str,
    inv_in: InvestigationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst)
):
    """Update an investigation."""
    return InvestigationService.update_investigation(db, investigation_id, inv_in)


@router.delete("/{investigation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_investigation(
    investigation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst)
):
    """Delete an investigation."""
    InvestigationService.delete_investigation(db, investigation_id)


@router.post("/{investigation_id}/indicators/{indicator_id}", status_code=status.HTTP_204_NO_CONTENT)
def add_indicator(
    investigation_id: str,
    indicator_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst)
):
    """Link an indicator to an investigation."""
    InvestigationService.add_indicator(db, investigation_id, indicator_id)


@router.delete("/{investigation_id}/indicators/{indicator_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_indicator(
    investigation_id: str,
    indicator_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst)
):
    """Remove an indicator from an investigation."""
    InvestigationService.remove_indicator(db, investigation_id, indicator_id)


@router.get("/{investigation_id}/summary", response_model=InvestigationSummaryResponse)
def get_summary(
    investigation_id: str,
    db: Session = Depends(get_db)
):
    """Get the full summary of an investigation, computing all related entities."""
    return InvestigationService.get_summary(db, investigation_id)


@router.get("/{investigation_id}/timeline", response_model=list[InvestigationTimelineEvent])
def get_timeline(
    investigation_id: str,
    db: Session = Depends(get_db)
):
    """Get a chronological timeline of events for an investigation."""
    return InvestigationService.get_timeline(db, investigation_id)
