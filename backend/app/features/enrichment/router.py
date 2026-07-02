"""Enrichment API router.

Endpoints:
  POST /indicators/{id}/enrich    — Trigger async enrichment
  GET /indicators/{id}/enrichment — Get enrichment status and history
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.features.enrichment.schemas import EnrichmentStatusResponse
from app.features.enrichment.service import EnrichmentService
from app.features.enrichment.tasks import run_enrichment

router = APIRouter(prefix="/indicators", tags=["Enrichment"])


@router.post("/{indicator_id}/enrich", status_code=status.HTTP_202_ACCEPTED)
def enrich_indicator(
    indicator_id: str,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Manually trigger asynchronous enrichment for a specific indicator."""
    
    # Check indicator exists before firing task
    from app.features.indicators.models import Indicator
    
    if not db.query(Indicator).filter(Indicator.id == indicator_id).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Indicator '{indicator_id}' not found.",
        )
        
    # Dispatch Celery task
    run_enrichment.delay(indicator_id)
    
    return {"status": "accepted", "message": "Enrichment dispatched asynchronously."}


@router.get(
    "/{indicator_id}/enrichment", 
    response_model=EnrichmentStatusResponse,
    responses={404: {"description": "Indicator not found"}}
)
def get_enrichment_status(
    indicator_id: str,
    db: Session = Depends(get_db),
) -> EnrichmentStatusResponse:
    """Get the enrichment execution history and status for an indicator."""
    response = EnrichmentService.get_status(db=db, indicator_id=indicator_id)
    
    if response is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Indicator '{indicator_id}' not found.",
        )
        
    return response
