"""Global Search API router.

Endpoints:
  GET /search — cross-entity keyword search

Router is thin: all logic lives in GlobalSearchService.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.features.search.schemas import GlobalSearchResult
from app.features.search.service import GlobalSearchService

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("", response_model=GlobalSearchResult)
def global_search(
    q: str = Query(..., min_length=1, max_length=200, description="Search term"),
    limit: int = Query(
        10,
        ge=1,
        le=50,
        description="Max results per entity type",
    ),
    db: Session = Depends(get_db),
) -> GlobalSearchResult:
    """Search across all entity types (indicators, malware, threat actors, etc.)."""
    return GlobalSearchService.search(db=db, q=q, limit=limit)
