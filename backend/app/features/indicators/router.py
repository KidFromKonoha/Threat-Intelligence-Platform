"""Indicators API router.

Endpoints:
  GET /indicators        — filtered, sorted, paginated indicator search
  GET /indicators/{id}   — full indicator detail with all related entities

Routers are thin: all logic lives in IndicatorSearchService.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.features.indicators.schemas import (
    IndicatorDetailResponse,
    IndicatorFilters,
    IndicatorSortField,
    PaginatedIndicators,
    SortOrder,
)
from app.features.indicators.service import IndicatorSearchService

router = APIRouter(prefix="/indicators", tags=["Indicators"])


@router.get("", response_model=PaginatedIndicators)
def search_indicators(
    filters: IndicatorFilters = Depends(IndicatorFilters),
    sort_by: IndicatorSortField = Query(
        IndicatorSortField.created_at,
        description="Field to sort results by",
    ),
    sort_order: SortOrder = Query(SortOrder.desc, description="Sort direction"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(20, ge=1, le=500, description="Results per page (max 500)"),
    db: Session = Depends(get_db),
) -> PaginatedIndicators:
    """Search indicators with optional filters, sorting and pagination."""
    return IndicatorSearchService.search(
        db=db,
        filters=filters,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )



