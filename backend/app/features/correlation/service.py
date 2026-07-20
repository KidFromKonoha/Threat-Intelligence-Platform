"""CorrelationService — all logic for Phase 6 correlation endpoints.

Design:
  - get_relationships(): loads the anchor indicator with all relationships via
    selectinload (one SELECT IN per relationship type, never N+1).

  - get_related_indicators(): discovers indicators sharing at least one entity
    with the anchor via a single SQL query using OR'd EXISTS subqueries, then
    ranks them by shared_count in Python. Relationship detail (which entities
    are shared) is resolved in a second batch load — still no N+1.

Out of scope (explicit non-goals):
  - Graph traversal
  - Automatic correlation rules
  - Scoring engine
  - Any modification to previous phase code
"""

from __future__ import annotations

import time
from collections import defaultdict

from fastapi import HTTPException, status
from sqlalchemy import or_, exists, select
from sqlalchemy.orm import Session, selectinload

from app.core.logging import get_logger
from app.db.associations import (
    indicator_campaign,
    indicator_feed,
    indicator_malware,
    indicator_report,
    indicator_threat_actor,
)
from app.features.campaigns.models import Campaign
from app.features.correlation.schemas import (
    CampaignRef,
    FeedRef,
    IndicatorAnchor,
    MalwareRef,
    MitreTechniqueRef,
    RelatedIndicatorResponse,
    RelatedIndicatorsResponse,
    RelationshipsResponse,
    ReportRef,
    SharedContext,
    ThreatActorRef,
    VulnerabilityRef,
)
from app.features.feeds.models import Feed
from app.features.indicators.models import Indicator
from app.features.malware.models import Malware
from app.features.mitre.models import MITRETechnique
from app.features.reports.models import Report
from app.features.threat_actors.models import ThreatActor
from app.features.vulnerabilities.models import Vulnerability

logger = get_logger(__name__)

# Relationships used when searching for related indicators.
# Each entry is a tuple of:
#   (category_name, association_table, association_fk_col)
# where association_fk_col is the non-indicator FK column name.
_RELATED_VIA = [
    ("malware",       indicator_malware,       "malware_id"),
    ("campaigns",     indicator_campaign,      "campaign_id"),
    ("threat_actors", indicator_threat_actor,  "threat_actor_id"),
    ("reports",       indicator_report,        "report_id"),
]


def _load_anchor(db: Session, indicator_id: str) -> Indicator:
    """Fetch the anchor indicator with all relationships loaded in batch."""
    row = (
        db.query(Indicator)
        .options(
            selectinload(Indicator.feeds),
            selectinload(Indicator.malware),
            selectinload(Indicator.campaigns),
            selectinload(Indicator.threat_actors),
            selectinload(Indicator.techniques),
            selectinload(Indicator.reports),
        )
        .filter(Indicator.id == indicator_id)
        .first()
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Indicator '{indicator_id}' not found.",
        )
    return row


def _coerce(value: object) -> list:
    """Normalise a relationship attribute to a list.

    Phase 2 models use Mapped[list] (unparameterised), so SQLAlchemy resolves
    them as uselist=False and returns a scalar or None.  This helper normalises
    the value so the rest of the service code can always iterate.
    """
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


class CorrelationService:
    """Discovers and exposes relationships between stored threat intelligence."""

    # ── GET /indicators/{id}/relationships ────────────────────────────────────

    @staticmethod
    def get_relationships(db: Session, indicator_id: str) -> RelationshipsResponse:
        """Return the full relationship graph for a single indicator.

        All related entity types are loaded in a single pass using selectinload
        (one SELECT IN per type).  Vulnerability relationships are not stored
        directly on Indicator; they are reached via the indicator's campaigns.

        Args:
            db:           Database session.
            indicator_id: Primary key of the anchor indicator.

        Returns:
            RelationshipsResponse containing the anchor and all related entities.
        """
        t0 = time.monotonic()
        anchor = _load_anchor(db, indicator_id)

        # Collect IDs from relationships that exist on Indicator directly.
        feeds         = _coerce(anchor.feeds)
        malware_list  = _coerce(anchor.malware)
        campaigns     = _coerce(anchor.campaigns)
        threat_actors = _coerce(anchor.threat_actors)
        techniques    = _coerce(anchor.techniques)
        reports       = _coerce(anchor.reports)

        # Vulnerabilities: linked via campaigns (campaign → vulnerabilities).
        # Load all campaign vulnerabilities in one batch rather than N queries.
        vulns: list[Vulnerability] = []
        seen_vuln_ids: set[str] = set()
        if campaigns:
            campaign_ids = [c.id for c in campaigns]
            camp_rows = (
                db.query(Campaign)
                .options(selectinload(Campaign.vulnerabilities))
                .filter(Campaign.id.in_(campaign_ids))
                .all()
            )
            for c in camp_rows:
                for v in _coerce(c.vulnerabilities):
                    if v.id not in seen_vuln_ids:
                        seen_vuln_ids.add(v.id)
                        vulns.append(v)

        duration = time.monotonic() - t0
        logger.info(
            "[correlation] relationships: id=%s feeds=%d malware=%d campaigns=%d "
            "threat_actors=%d techniques=%d reports=%d vulns=%d duration=%.3fs",
            indicator_id,
            len(feeds), len(malware_list), len(campaigns),
            len(threat_actors), len(techniques), len(reports), len(vulns),
            duration,
        )

        return RelationshipsResponse(
            indicator=IndicatorAnchor.model_validate(anchor),
            feeds=[FeedRef.model_validate(f) for f in feeds],
            malware=[MalwareRef.model_validate(m) for m in malware_list],
            campaigns=[CampaignRef.model_validate(c) for c in campaigns],
            threat_actors=[ThreatActorRef.model_validate(t) for t in threat_actors],
            mitre_techniques=[MitreTechniqueRef.model_validate(t) for t in techniques],
            reports=[ReportRef.model_validate(r) for r in reports],
            vulnerabilities=[VulnerabilityRef.model_validate(v) for v in vulns],
        )

    # ── GET /indicators/{id}/related ─────────────────────────────────────────

    @staticmethod
    def get_related_indicators(
        db: Session,
        indicator_id: str,
        limit: int = 25,
    ) -> RelatedIndicatorsResponse:
        """Return indicators related to the anchor by shared relationships.

        Strategy (no N+1):
          1. Load anchor with all relationships (selectinload).
          2. Collect entity IDs per category from the anchor.
          3. Build one SQL query: find all other indicators that share ANY entity
             with the anchor using OR'd EXISTS subqueries on association tables.
          4. Batch-load the results' own relationships (one selectinload pass).
          5. Compute shared_count and SharedContext in Python — one pass.
          6. Rank by shared_count descending, return top `limit`.

        Args:
            db:           Database session.
            indicator_id: Primary key of the anchor indicator.
            limit:        Maximum number of related indicators to return (1–100).

        Returns:
            RelatedIndicatorsResponse ranked by number of shared relationships.
        """
        t0 = time.monotonic()
        anchor = _load_anchor(db, indicator_id)

        # Collect entity IDs from anchor per category.
        anchor_ids: dict[str, set[str]] = {
            "malware":       {m.id for m in _coerce(anchor.malware)},
            "campaigns":     {c.id for c in _coerce(anchor.campaigns)},
            "threat_actors": {t.id for t in _coerce(anchor.threat_actors)},
            "reports":       {r.id for r in _coerce(anchor.reports)},
        }

        # If the anchor has no relationships at all, return early.
        all_entity_ids = set().union(*anchor_ids.values())
        if not all_entity_ids:
            logger.info(
                "[correlation] related: id=%s has no relationships — returning empty",
                indicator_id,
            )
            return RelatedIndicatorsResponse(
                indicator=IndicatorAnchor.model_validate(anchor),
                related=[],
                total_found=0,
            )

        # Build OR'd EXISTS subqueries: one per category that has any IDs.
        exists_conditions = []
        for category, assoc_table, fk_col in _RELATED_VIA:
            ids = anchor_ids[category]
            if not ids:
                continue
            exists_conditions.append(
                exists(
                    select(assoc_table.c.indicator_id).where(
                        assoc_table.c.indicator_id == Indicator.id,
                        assoc_table.c[fk_col].in_(ids),
                    )
                )
            )

        if not exists_conditions:
            return RelatedIndicatorsResponse(
                indicator=IndicatorAnchor.model_validate(anchor),
                related=[],
                total_found=0,
            )

        # Single query: all indicators sharing at least one entity, excluding anchor.
        candidates = (
            db.query(Indicator)
            .options(
                selectinload(Indicator.malware),
                selectinload(Indicator.campaigns),
                selectinload(Indicator.threat_actors),
                selectinload(Indicator.reports),
            )
            .filter(
                Indicator.id != indicator_id,
                or_(*exists_conditions),
            )
            .all()
        )

        total_found = len(candidates)

        # Score and build context in Python (one pass — no extra DB queries).
        scored: list[RelatedIndicatorResponse] = []
        for ind in candidates:
            ind_malware_ids      = {m.id for m in _coerce(ind.malware)}
            ind_campaign_ids     = {c.id for c in _coerce(ind.campaigns)}
            ind_threat_actor_ids = {t.id for t in _coerce(ind.threat_actors)}
            ind_report_ids       = {r.id for r in _coerce(ind.reports)}

            shared_malware       = anchor_ids["malware"]       & ind_malware_ids
            shared_campaigns     = anchor_ids["campaigns"]     & ind_campaign_ids
            shared_threat_actors = anchor_ids["threat_actors"] & ind_threat_actor_ids
            shared_reports       = anchor_ids["reports"]       & ind_report_ids

            shared_count = (
                len(shared_malware)
                + len(shared_campaigns)
                + len(shared_threat_actors)
                + len(shared_reports)
            )

            if shared_count == 0:
                # Exists subquery matched but Python-side intersection is empty.
                # This can happen if the in_() list contained the anchor's own
                # entity IDs that don't appear on this candidate in the loaded
                # relationships (uselist=False edge case). Skip silently.
                continue

            # Resolve names for context — data already in memory from selectinload.
            shared_malware_names       = [m.name for m in _coerce(ind.malware)       if m.id in shared_malware]
            shared_campaign_names      = [c.name for c in _coerce(ind.campaigns)     if c.id in shared_campaigns]
            shared_threat_actor_names  = [t.name for t in _coerce(ind.threat_actors) if t.id in shared_threat_actors]
            shared_report_titles       = [r.title for r in _coerce(ind.reports)      if r.id in shared_reports]

            scored.append(
                RelatedIndicatorResponse(
                    id=ind.id,
                    type=ind.type,
                    value=ind.value,
                    confidence=ind.confidence,
                    severity=ind.severity,
                    first_seen=ind.first_seen,
                    last_seen=ind.last_seen,
                    shared_count=shared_count,
                    shared_context=SharedContext(
                        malware=shared_malware_names,
                        campaigns=shared_campaign_names,
                        threat_actors=shared_threat_actor_names,
                        reports=shared_report_titles,
                        feeds=[],
                    ),
                )
            )

        # Rank by shared_count descending, then apply limit.
        scored.sort(key=lambda x: x.shared_count, reverse=True)
        ranked = scored[:limit]

        duration = time.monotonic() - t0
        logger.info(
            "[correlation] related: id=%s candidates=%d returned=%d duration=%.3fs",
            indicator_id,
            total_found,
            len(ranked),
            duration,
        )

        return RelatedIndicatorsResponse(
            indicator=IndicatorAnchor.model_validate(anchor),
            related=ranked,
            total_found=total_found,
        )
