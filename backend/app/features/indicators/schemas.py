"""Pydantic schemas and dataclasses for the Indicators API.

Covers:
  - IndicatorFilters: query parameter model for GET /indicators
  - IndicatorSortField / SortOrder: validated sort enums
  - IndicatorResponse: list-level indicator representation
  - IndicatorDetailResponse: full indicator with all related entities
  - PaginatedIndicators: paginated response envelope
  - Nested summary schemas for related entities

NOTE on IndicatorFilters
────────────────────────
FastAPI renders a Pydantic BaseModel used with Depends() as a *request body*
on GET endpoints — which browsers reject (GET cannot have a body).  The fix
is a standard Python dataclass whose field defaults are FastAPI Query()
objects.  FastAPI recognises this pattern and exposes each field as an
individual query parameter in both OpenAPI / Swagger and actual routing.
"""


import enum
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from fastapi import Query
from pydantic import BaseModel, Field

from app.db.enums import IndicatorStatus, IndicatorType, Severity
from app.db.text_match import MatchMode



# ── Sort parameters ────────────────────────────────────────────────────────────

class IndicatorSortField(str, enum.Enum):
    created_at   = "created_at"
    updated_at   = "updated_at"
    confidence   = "confidence"
    first_seen   = "first_seen"
    last_seen    = "last_seen"
    source_count = "source_count"


class SortOrder(str, enum.Enum):
    asc  = "asc"
    desc = "desc"


# ── Filter parameter model ─────────────────────────────────────────────────────

@dataclass
class IndicatorFilters:
    """Query parameters for GET /indicators.

    Implemented as a Python dataclass (not a Pydantic BaseModel) so that
    FastAPI Depends() exposes each field as a URL query parameter rather
    than generating a request body.  FastAPI natively resolves dataclass
    Depends() into query parameters in routing and OpenAPI output.

    Cross-field validation (confidence_min ≤ confidence_max) is applied in
    __post_init__; FastAPI converts any ValueError raised there to a 422.
    """

    # ── Text filters ──────────────────────────────────────────────────────────
    value: str | None = Query(
        default=None, description="Filter by IOC value (text match)"
    )
    value_match: MatchMode = Query(
        default=MatchMode.CONTAINS,
        description="Match mode for value / relational text filters: exact | prefix | contains",
    )
    normalized_value: str | None = Query(
        default=None, description="Filter by normalized value (text match)"
    )
    normalized_value_match: MatchMode = Query(
        default=MatchMode.CONTAINS, description="Match mode for normalized_value"
    )

    # ── Categorical filters (multi-value → IN clause) ─────────────────────────
    type: list[IndicatorType] | None = Query(
        default=None, description="Indicator type(s) — repeat for multiple (e.g. ?type=ipv4&type=domain)"
    )
    severity: list[Severity] | None = Query(
        default=None, description="Severity level(s)"
    )
    status: list[IndicatorStatus] | None = Query(
        default=None, description="Indicator status(es)"
    )

    # ── Confidence range ──────────────────────────────────────────────────────
    confidence_min: int | None = Query(
        default=None, ge=0, le=100, description="Minimum confidence score (0–100)"
    )
    confidence_max: int | None = Query(
        default=None, ge=0, le=100, description="Maximum confidence score (0–100)"
    )

    # ── Array overlap filter (PostgreSQL &&) ──────────────────────────────────
    tags: list[str] | None = Query(
        default=None, description="Filter by tag(s) — any match (PostgreSQL array overlap)"
    )

    # ── Relational text filters (resolved via EXISTS subqueries) ──────────────
    feed: str | None = Query(
        default=None, description="Filter by linked feed name (text match)"
    )
    malware: str | None = Query(
        default=None, description="Filter by linked malware name (text match)"
    )
    threat_actor: str | None = Query(
        default=None, description="Filter by linked threat actor name (text match)"
    )
    campaign: str | None = Query(
        default=None, description="Filter by linked campaign name (text match)"
    )

    # ── Timestamp range filters ───────────────────────────────────────────────
    first_seen_from: datetime | None = Query(
        default=None, description="Filter: first_seen ≥ this datetime (ISO 8601)"
    )
    first_seen_to: datetime | None = Query(
        default=None, description="Filter: first_seen ≤ this datetime (ISO 8601)"
    )
    last_seen_from: datetime | None = Query(
        default=None, description="Filter: last_seen ≥ this datetime"
    )
    last_seen_to: datetime | None = Query(
        default=None, description="Filter: last_seen ≤ this datetime"
    )
    created_at_from: datetime | None = Query(
        default=None, description="Filter: created_at ≥ this datetime"
    )
    created_at_to: datetime | None = Query(
        default=None, description="Filter: created_at ≤ this datetime"
    )

    def __post_init__(self) -> None:
        """Cross-field validation — FastAPI converts ValueError → 422.

        Guard: when the class is instantiated directly (e.g. in tests) without
        FastAPI dependency injection, field values may still be Query FieldInfo
        objects (the declared defaults).  Skip validation in that case — the
        check is only meaningful once FastAPI has resolved the actual values.
        """
        from fastapi.params import Depends as _Depends  # avoid circular
        from fastapi import params as _fp

        # If confidence fields are still raw Query objects (not injected), skip.
        if isinstance(self.confidence_min, _fp.Query) or isinstance(self.confidence_max, _fp.Query):
            return

        if (
            self.confidence_min is not None
            and self.confidence_max is not None
            and self.confidence_min > self.confidence_max
        ):
            raise ValueError("confidence_min must be ≤ confidence_max")





# ── Related-entity summary schemas ────────────────────────────────────────────

class FeedSummary(BaseModel):
    id: str
    name: str
    type: str

    model_config = {"from_attributes": True}


class MalwareSummary(BaseModel):
    id: str
    name: str
    category: str | None = None

    model_config = {"from_attributes": True}


class ThreatActorSummary(BaseModel):
    id: str
    name: str
    country: str | None = None

    model_config = {"from_attributes": True}


class CampaignSummary(BaseModel):
    id: str
    name: str

    model_config = {"from_attributes": True}


class TechniqueSummary(BaseModel):
    id: str
    technique_id: str
    name: str
    tactic: str

    model_config = {"from_attributes": True}


class ReportSummary(BaseModel):
    id: str
    title: str
    author: str | None = None

    model_config = {"from_attributes": True}


# ── Indicator response schemas ─────────────────────────────────────────────────

class IndicatorResponse(BaseModel):
    """Indicator representation used in list responses.

    Omits heavy relationship collections to keep list payloads small.
    """

    id: str
    type: str
    value: str
    normalized_value: str
    confidence: int
    severity: str
    risk_score: int
    status: str
    first_seen: datetime
    last_seen: datetime
    source_count: int
    country: str | None = None
    asn: str | None = None
    tlp: str | None = None
    tags: list[str] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IndicatorDetailResponse(IndicatorResponse):
    """Full indicator representation with all related entities.

    Used only by GET /indicators/{id}. Relations are loaded via selectinload
    in the service layer to avoid N+1 queries.
    """

    feeds:         list[FeedSummary]         = []
    malware:       list[MalwareSummary]      = []
    threat_actors: list[ThreatActorSummary]  = []
    campaigns:     list[CampaignSummary]     = []
    techniques:    list[TechniqueSummary]    = []
    reports:       list[ReportSummary]       = []

    model_config = {"from_attributes": True}


# ── Pagination envelope ────────────────────────────────────────────────────────

class PaginatedIndicators(BaseModel):
    data:          list[IndicatorResponse]
    total_records: int
    total_pages:   int
    current_page:  int
    page_size:     int
