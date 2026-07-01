"""IndicatorSearchService — all query logic for GET /indicators and GET /indicators/{id}.

Design principles:
  - Composable filter pattern: build predicates as a list, apply once.
  - Relational filters use EXISTS subqueries, never JOINs, to prevent row
    multiplication when an indicator has multiple related entities.
  - Relationship loading for the detail endpoint uses selectinload (batch
    SELECT IN queries) — not lazy loading — to avoid N+1 queries.
  - Sorting is validated via IndicatorSortField enum before touching the DB.
  - Pagination uses OFFSET/LIMIT with a separate COUNT(*) on the same filter
    set. The count reuses the identical predicate list — no extra code path.
"""

from __future__ import annotations

import math
import time
from typing import TYPE_CHECKING

from sqlalchemy import exists, select
from sqlalchemy.orm import Session, selectinload

from app.core.logging import get_logger
from app.db.associations import (
    indicator_campaign,
    indicator_feed,
    indicator_malware,
    indicator_threat_actor,
)
from app.db.text_match import apply_text_match
from app.features.campaigns.models import Campaign
from app.features.feeds.models import Feed
from app.features.indicators.models import Indicator
from app.features.indicators.schemas import (
    IndicatorDetailResponse,
    IndicatorFilters,
    IndicatorResponse,
    IndicatorSortField,
    PaginatedIndicators,
    SortOrder,
)
from app.features.malware.models import Malware
from app.features.threat_actors.models import ThreatActor

if TYPE_CHECKING:
    pass

logger = get_logger(__name__)

# Maps IndicatorSortField enum values to ORM column expressions.
_SORT_COLUMNS = {
    IndicatorSortField.created_at:   Indicator.created_at,
    IndicatorSortField.updated_at:   Indicator.updated_at,
    IndicatorSortField.confidence:   Indicator.confidence,
    IndicatorSortField.first_seen:   Indicator.first_seen,
    IndicatorSortField.last_seen:    Indicator.last_seen,
    IndicatorSortField.source_count: Indicator.source_count,
}


class IndicatorSearchService:
    """Handles search and retrieval of Indicator records."""

    @staticmethod
    def search(
        db: Session,
        filters: IndicatorFilters,
        sort_by: IndicatorSortField = IndicatorSortField.created_at,
        sort_order: SortOrder = SortOrder.desc,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedIndicators:
        """Execute a filtered, sorted, paginated search over Indicator rows.

        Args:
            db:         Database session (injected by FastAPI Depends).
            filters:    Validated IndicatorFilters instance.
            sort_by:    Column to sort on.
            sort_order: asc or desc.
            page:       1-based page number.
            page_size:  Rows per page (1–500).

        Returns:
            PaginatedIndicators containing the data slice and pagination metadata.
        """
        t_start = time.monotonic()

        # ── Build predicate list ──────────────────────────────────────────────
        predicates: list = []

        # Text filters
        if filters.value:
            predicates.append(
                apply_text_match(Indicator.value, filters.value, filters.value_match)
            )
        if filters.normalized_value:
            predicates.append(
                apply_text_match(
                    Indicator.normalized_value,
                    filters.normalized_value,
                    filters.normalized_value_match,
                )
            )

        # Categorical IN filters
        if filters.type:
            type_values = [t.value if hasattr(t, "value") else t for t in filters.type]
            predicates.append(Indicator.type.in_(type_values))
        if filters.severity:
            sev_values = [s.value if hasattr(s, "value") else s for s in filters.severity]
            predicates.append(Indicator.severity.in_(sev_values))
        if filters.status:
            stat_values = [s.value if hasattr(s, "value") else s for s in filters.status]
            predicates.append(Indicator.status.in_(stat_values))

        # Confidence range
        if filters.confidence_min is not None:
            predicates.append(Indicator.confidence >= filters.confidence_min)
        if filters.confidence_max is not None:
            predicates.append(Indicator.confidence <= filters.confidence_max)

        # Tags — PostgreSQL array overlap (&&)
        # type_coerce re-types the Mapped[list] column as a dialect-specific
        # ARRAY so .overlap() becomes available without raw SQL.
        if filters.tags:
            from sqlalchemy import Text as SAText, type_coerce
            from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
            predicates.append(
                type_coerce(Indicator.tags, PG_ARRAY(SAText)).overlap(filters.tags)
            )

        # Relational filters via EXISTS subqueries ────────────────────────────
        if filters.feed:
            predicates.append(
                exists(
                    select(indicator_feed.c.indicator_id)
                    .join(Feed, Feed.id == indicator_feed.c.feed_id)
                    .where(
                        indicator_feed.c.indicator_id == Indicator.id,
                        apply_text_match(Feed.name, filters.feed, filters.value_match),
                    )
                )
            )
        if filters.malware:
            predicates.append(
                exists(
                    select(indicator_malware.c.indicator_id)
                    .join(Malware, Malware.id == indicator_malware.c.malware_id)
                    .where(
                        indicator_malware.c.indicator_id == Indicator.id,
                        apply_text_match(Malware.name, filters.malware, filters.value_match),
                    )
                )
            )
        if filters.threat_actor:
            predicates.append(
                exists(
                    select(indicator_threat_actor.c.indicator_id)
                    .join(
                        ThreatActor,
                        ThreatActor.id == indicator_threat_actor.c.threat_actor_id,
                    )
                    .where(
                        indicator_threat_actor.c.indicator_id == Indicator.id,
                        apply_text_match(
                            ThreatActor.name, filters.threat_actor, filters.value_match
                        ),
                    )
                )
            )
        if filters.campaign:
            predicates.append(
                exists(
                    select(indicator_campaign.c.indicator_id)
                    .join(Campaign, Campaign.id == indicator_campaign.c.campaign_id)
                    .where(
                        indicator_campaign.c.indicator_id == Indicator.id,
                        apply_text_match(
                            Campaign.name, filters.campaign, filters.value_match
                        ),
                    )
                )
            )

        # Timestamp range filters
        if filters.first_seen_from:
            predicates.append(Indicator.first_seen >= filters.first_seen_from)
        if filters.first_seen_to:
            predicates.append(Indicator.first_seen <= filters.first_seen_to)
        if filters.last_seen_from:
            predicates.append(Indicator.last_seen >= filters.last_seen_from)
        if filters.last_seen_to:
            predicates.append(Indicator.last_seen <= filters.last_seen_to)
        if filters.created_at_from:
            predicates.append(Indicator.created_at >= filters.created_at_from)
        if filters.created_at_to:
            predicates.append(Indicator.created_at <= filters.created_at_to)

        # ── Apply predicates + count ──────────────────────────────────────────
        base_query = db.query(Indicator).filter(*predicates)
        total_records: int = base_query.count()

        # ── Sort ─────────────────────────────────────────────────────────────
        sort_col = _SORT_COLUMNS[sort_by]
        ordered_query = base_query.order_by(
            sort_col.asc() if sort_order is SortOrder.asc else sort_col.desc()
        )

        # ── Paginate ─────────────────────────────────────────────────────────
        offset = (page - 1) * page_size
        rows = ordered_query.offset(offset).limit(page_size).all()

        total_pages = max(1, math.ceil(total_records / page_size))

        duration = time.monotonic() - t_start
        logger.info(
            "[indicators] search: predicates=%d total=%d page=%d/%d duration=%.3fs",
            len(predicates),
            total_records,
            page,
            total_pages,
            duration,
        )

        return PaginatedIndicators(
            data=[IndicatorResponse.model_validate(r) for r in rows],
            total_records=total_records,
            total_pages=total_pages,
            current_page=page,
            page_size=page_size,
        )

    @staticmethod
    def get_by_id(db: Session, indicator_id: str) -> IndicatorDetailResponse:
        """Return the full indicator including all related entities.

        Uses selectinload to batch-load each relationship in a single extra
        SELECT per relation — never N+1.

        Raises:
            HTTPException 404 if not found.
        """
        from fastapi import HTTPException, status

        row = (
            db.query(Indicator)
            .options(
                selectinload(Indicator.feeds),
                selectinload(Indicator.malware),
                selectinload(Indicator.threat_actors),
                selectinload(Indicator.campaigns),
                selectinload(Indicator.techniques),
                selectinload(Indicator.reports),
            )
            .filter(Indicator.id == indicator_id)
            .first()
        )
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Indicator {indicator_id!r} not found",
            )

        logger.info("[indicators] detail fetch: id=%s", indicator_id)
        return _build_detail_response(row)


def _build_detail_response(row: "Indicator") -> IndicatorDetailResponse:  # noqa: F821
    """Construct IndicatorDetailResponse from a fully-loaded ORM row.

    NOTE: The Phase 2 models use Mapped[list] with secondary= relationships,
    but SQLAlchemy infers uselist=False because the generic `list` type hint
    is used instead of `list[Feed]`. As a result each relationship attribute
    is a scalar ORM object or None — not a collection. _coerce_rel() wraps
    scalar values in a list so the API always returns a proper array.
    """
    from app.features.indicators.schemas import (
        CampaignSummary,
        FeedSummary,
        MalwareSummary,
        ReportSummary,
        TechniqueSummary,
        ThreatActorSummary,
    )

    def _coerce_rel(value: object) -> list:
        """Normalise a relationship value to a list regardless of uselist."""
        if value is None:
            return []
        if isinstance(value, list):
            return value
        # scalar ORM object — wrap it
        return [value]

    return IndicatorDetailResponse(
        id=row.id,
        type=row.type,
        value=row.value,
        normalized_value=row.normalized_value,
        confidence=row.confidence,
        severity=row.severity,
        risk_score=row.risk_score,
        status=row.status,
        first_seen=row.first_seen,
        last_seen=row.last_seen,
        source_count=row.source_count,
        country=row.country,
        asn=row.asn,
        tags=row.tags,
        created_at=row.created_at,
        updated_at=row.updated_at,
        feeds=[FeedSummary.model_validate(f) for f in _coerce_rel(row.feeds)],
        malware=[MalwareSummary.model_validate(m) for m in _coerce_rel(row.malware)],
        threat_actors=[ThreatActorSummary.model_validate(t) for t in _coerce_rel(row.threat_actors)],
        campaigns=[CampaignSummary.model_validate(c) for c in _coerce_rel(row.campaigns)],
        techniques=[TechniqueSummary.model_validate(t) for t in _coerce_rel(row.techniques)],
        reports=[ReportSummary.model_validate(r) for r in _coerce_rel(row.reports)],
    )

