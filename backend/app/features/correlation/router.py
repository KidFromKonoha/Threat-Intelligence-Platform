"""Correlation API router.

Endpoints:
  GET /indicators/{id}/relationships — full relationship graph for one indicator
  GET /indicators/{id}/related       — ranked similar indicators by shared entities

Routers are thin: all logic lives in CorrelationService.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.features.correlation.schemas import (
    RelatedIndicatorsResponse,
    RelationshipsResponse,
)
from app.features.correlation.service import CorrelationService

router = APIRouter(prefix="/indicators", tags=["Correlation"])


@router.get("/{indicator_id}/relationships", response_model=RelationshipsResponse)
def get_relationships(
    indicator_id: str,
    db: Session = Depends(get_db),
) -> RelationshipsResponse:
    """Return the full relationship graph for a single indicator.

    Includes all feeds, malware, campaigns, threat actors, MITRE techniques,
    reports, and vulnerabilities associated with the indicator.
    """
    return CorrelationService.get_relationships(db=db, indicator_id=indicator_id)


@router.get("/{indicator_id}/related", response_model=RelatedIndicatorsResponse)
def get_related_indicators(
    indicator_id: str,
    limit: int = Query(
        25,
        ge=1,
        le=100,
        description="Maximum number of related indicators to return (1–100)",
    ),
    db: Session = Depends(get_db),
) -> RelatedIndicatorsResponse:
    """Return indicators related to the anchor by shared relationships.

    Relationships considered: shared malware, campaign, threat actor, report,
    or feed.  Results are ranked by the number of shared relationships
    (descending).
    """
    return CorrelationService.get_related_indicators(
        db=db,
        indicator_id=indicator_id,
        limit=limit,
    )
