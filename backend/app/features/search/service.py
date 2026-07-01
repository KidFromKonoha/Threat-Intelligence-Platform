"""GlobalSearchService — cross-entity full-text search.

Design:
  - Runs a separate ilike query per entity type. No cross-table JOIN.
  - Each sub-query is capped at `limit` results (default 10, max 50).
  - Uses `or_()` for entities where multiple columns are searchable
    (e.g. Indicator: value OR normalized_value; MITRETechnique: name OR technique_id).
  - Never returns N+1 queries: each entity type = exactly 1 SELECT.
  - Logs query term, per-entity hit counts, and total wall-clock duration.

Out of scope (explicit non-goals):
  - Cross-entity JOIN or graph traversal.
  - Relevance scoring.
  - Elasticsearch / OpenSearch.
"""

from __future__ import annotations

import time

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.features.campaigns.models import Campaign
from app.features.indicators.models import Indicator
from app.features.malware.models import Malware
from app.features.mitre.models import MITRETechnique
from app.features.reports.models import Report
from app.features.search.schemas import (
    EntitySummary,
    GlobalSearchResult,
    IndicatorSummary,
)
from app.features.threat_actors.models import ThreatActor
from app.features.vulnerabilities.models import Vulnerability

logger = get_logger(__name__)


class GlobalSearchService:
    """Executes a multi-entity keyword search using PostgreSQL ilike."""

    @staticmethod
    def search(db: Session, q: str, limit: int = 10) -> GlobalSearchResult:
        """Search all entity types for rows matching the query string.

        Args:
            db:    Database session.
            q:     Search term. Matched as "%q%" against each entity's
                   primary text columns.
            limit: Max results per entity type (1–50).

        Returns:
            GlobalSearchResult with per-entity result lists.
        """
        t_start = time.monotonic()
        pattern = f"%{q}%"

        # ── Indicators ────────────────────────────────────────────────────────
        indicator_rows = (
            db.query(Indicator)
            .filter(
                or_(
                    Indicator.value.ilike(pattern),
                    Indicator.normalized_value.ilike(pattern),
                )
            )
            .limit(limit)
            .all()
        )
        indicators = [
            IndicatorSummary(
                id=r.id,
                type=r.type,
                value=r.value,
                confidence=r.confidence,
                severity=r.severity,
            )
            for r in indicator_rows
        ]

        # ── Malware ───────────────────────────────────────────────────────────
        malware_rows = (
            db.query(Malware)
            .filter(Malware.name.ilike(pattern))
            .limit(limit)
            .all()
        )
        malware = [
            EntitySummary(
                id=r.id,
                name=r.name,
                entity_type="malware",
                description=r.description,
            )
            for r in malware_rows
        ]

        # ── Threat actors ─────────────────────────────────────────────────────
        ta_rows = (
            db.query(ThreatActor)
            .filter(ThreatActor.name.ilike(pattern))
            .limit(limit)
            .all()
        )
        threat_actors = [
            EntitySummary(
                id=r.id,
                name=r.name,
                entity_type="threat_actor",
                description=r.description,
            )
            for r in ta_rows
        ]

        # ── Campaigns ─────────────────────────────────────────────────────────
        campaign_rows = (
            db.query(Campaign)
            .filter(Campaign.name.ilike(pattern))
            .limit(limit)
            .all()
        )
        campaigns = [
            EntitySummary(
                id=r.id,
                name=r.name,
                entity_type="campaign",
                description=r.description,
            )
            for r in campaign_rows
        ]

        # ── Reports ───────────────────────────────────────────────────────────
        report_rows = (
            db.query(Report)
            .filter(Report.title.ilike(pattern))
            .limit(limit)
            .all()
        )
        reports = [
            EntitySummary(
                id=r.id,
                name=r.title,
                entity_type="report",
                description=r.summary,
            )
            for r in report_rows
        ]

        # ── MITRE techniques ──────────────────────────────────────────────────
        technique_rows = (
            db.query(MITRETechnique)
            .filter(
                or_(
                    MITRETechnique.name.ilike(pattern),
                    MITRETechnique.technique_id.ilike(pattern),
                )
            )
            .limit(limit)
            .all()
        )
        techniques = [
            EntitySummary(
                id=r.id,
                name=f"{r.technique_id} — {r.name}",
                entity_type="technique",
                description=r.description,
            )
            for r in technique_rows
        ]

        # ── Vulnerabilities ───────────────────────────────────────────────────
        vuln_rows = (
            db.query(Vulnerability)
            .filter(Vulnerability.cve.ilike(pattern))
            .limit(limit)
            .all()
        )
        vulnerabilities = [
            EntitySummary(
                id=r.id,
                name=r.cve,
                entity_type="vulnerability",
                description=r.description,
            )
            for r in vuln_rows
        ]

        # ── Totals + logging ──────────────────────────────────────────────────
        total_hits = (
            len(indicators)
            + len(malware)
            + len(threat_actors)
            + len(campaigns)
            + len(reports)
            + len(techniques)
            + len(vulnerabilities)
        )

        duration = time.monotonic() - t_start
        logger.info(
            "[search] q=%r limit=%d hits: indicators=%d malware=%d "
            "threat_actors=%d campaigns=%d reports=%d techniques=%d "
            "vulnerabilities=%d total=%d duration=%.3fs",
            q,
            limit,
            len(indicators),
            len(malware),
            len(threat_actors),
            len(campaigns),
            len(reports),
            len(techniques),
            len(vulnerabilities),
            total_hits,
            duration,
        )

        return GlobalSearchResult(
            query=q,
            total_hits=total_hits,
            indicators=indicators,
            malware=malware,
            threat_actors=threat_actors,
            campaigns=campaigns,
            reports=reports,
            techniques=techniques,
            vulnerabilities=vulnerabilities,
        )
