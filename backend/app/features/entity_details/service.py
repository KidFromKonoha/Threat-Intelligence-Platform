"""Entity Detail Service.

Aggregates full context for all intelligence entities.
"""

from __future__ import annotations
from typing import Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

from app.features.indicators.models import Indicator
from app.features.threat_actors.models import ThreatActor
from app.features.malware.models import Malware
from app.features.campaigns.models import Campaign
from app.features.vulnerabilities.models import Vulnerability
from app.features.enrichment.models import EnrichmentResult

from app.features.correlation.service import CorrelationService
from app.features.entity_details.schemas import (
    IndicatorFullDetailResponse,
    ThreatActorDetailResponse,
    MalwareDetailResponse,
    CampaignDetailResponse,
    VulnerabilityDetailResponse,
    TimelineEvent,
    EnrichmentData
)
from app.features.search.schemas import EntitySummary, IndicatorSummary


def _coerce(value: Any) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


class EntityDetailService:
    @staticmethod
    def get_indicator(db: Session, indicator_id: str) -> IndicatorFullDetailResponse:
        # We reuse CorrelationService to get the anchor and primary relationships.
        # But we also need assets, comments, and enrichments, so we load the anchor manually with extra selectinloads.
        indicator = (
            db.query(Indicator)
            .options(
                selectinload(Indicator.feeds),
                selectinload(Indicator.malware),
                selectinload(Indicator.campaigns),
                selectinload(Indicator.threat_actors),
                selectinload(Indicator.techniques),
                selectinload(Indicator.reports),
                selectinload(Indicator.assets),
            )
            .filter(Indicator.id == indicator_id)
            .first()
        )
        if not indicator:
            raise HTTPException(status_code=404, detail="Indicator not found")

        # Reuse CorrelationService to get vulnerabilities (campaign -> vulnerabilities)
        # and related indicators.
        rel_resp = CorrelationService.get_relationships(db, indicator_id)
        related_indicators_resp = CorrelationService.get_related_indicators(db, indicator_id, limit=10)

        # Fetch Enrichments
        enrichment_rows = db.query(EnrichmentResult).filter(EnrichmentResult.indicator_id == indicator_id).all()
        enrichments = [
            EnrichmentData(
                provider=e.provider,
                status=e.execution_status,
                data=e.extracted_attributes or e.raw_response,
                timestamp=e.created_at
            ) for e in enrichment_rows
        ]

        timeline: list[TimelineEvent] = []
        timeline.append(TimelineEvent(event_type="indicator_created", description="Indicator created", timestamp=indicator.created_at))
        for e in enrichment_rows:
            timeline.append(TimelineEvent(event_type="enrichment_executed", description=f"Enrichment via {e.provider}", timestamp=e.created_at))
        for c in _coerce(indicator.campaigns):
            timeline.append(TimelineEvent(event_type="campaign_linked", description=f"Linked to campaign {c.name}", timestamp=c.created_at))
        for ta in _coerce(indicator.threat_actors):
            timeline.append(TimelineEvent(event_type="threat_actor_linked", description=f"Linked to threat actor {ta.name}", timestamp=ta.created_at))
        timeline.sort(key=lambda x: x.timestamp, reverse=True)

        return IndicatorFullDetailResponse(
            id=indicator.id,
            type=indicator.type,
            value=indicator.value,
            confidence=indicator.confidence,
            severity=indicator.severity,
            risk_score=indicator.risk_score,
            status=indicator.status,
            first_seen=indicator.first_seen,
            last_seen=indicator.last_seen,
            tags=indicator.tags,
            created_at=indicator.created_at,
            updated_at=indicator.updated_at,
            feed_sources=[EntitySummary(id=f.id, name=f.name, entity_type="feed") for f in _coerce(indicator.feeds)],
            related_indicators=[IndicatorSummary(id=i.id, type=i.type, value=i.value, confidence=i.confidence, severity=i.severity) for i in related_indicators_resp.related],
            threat_actors=[EntitySummary(id=t.id, name=t.name, entity_type="threat_actor") for t in _coerce(indicator.threat_actors)],
            malware=[EntitySummary(id=m.id, name=m.name, entity_type="malware") for m in _coerce(indicator.malware)],
            campaigns=[EntitySummary(id=c.id, name=c.name, entity_type="campaign") for c in _coerce(indicator.campaigns)],
            vulnerabilities=[EntitySummary(id=v.id, name=v.cve, entity_type="vulnerability") for v in rel_resp.vulnerabilities],
            assets=[EntitySummary(id=a.id, name=a.name, entity_type="asset") for a in _coerce(indicator.assets)],
            mitre_techniques=[EntitySummary(id=t.id, name=t.name, entity_type="mitre_technique") for t in _coerce(indicator.techniques)],
            whois=indicator.whois,
            passive_dns=indicator.passive_dns,
            enrichments=enrichments,
            timeline=timeline,
            comments=[] # Comments not implemented in this phase
        )

    @staticmethod
    def get_threat_actor(db: Session, actor_id: str) -> ThreatActorDetailResponse:
        ta = (
            db.query(ThreatActor)
            .options(
                selectinload(ThreatActor.campaigns),
                selectinload(ThreatActor.malware),
                selectinload(ThreatActor.indicators),
                selectinload(ThreatActor.techniques),
            )
            .filter(ThreatActor.id == actor_id)
            .first()
        )
        if not ta:
            raise HTTPException(status_code=404, detail="Threat actor not found")

        timeline: list[TimelineEvent] = []
        timeline.append(TimelineEvent(event_type="threat_actor_created", description="Threat actor created", timestamp=ta.created_at))
        for c in _coerce(ta.campaigns):
            timeline.append(TimelineEvent(event_type="campaign_linked", description=f"Linked to campaign {c.name}", timestamp=c.created_at))
        timeline.sort(key=lambda x: x.timestamp, reverse=True)

        return ThreatActorDetailResponse(
            id=ta.id,
            name=ta.name,
            aliases=ta.aliases,
            description=ta.description,
            motivation=ta.motivation,
            country=ta.country,
            sophistication=ta.sophistication,
            first_seen=ta.first_seen,
            last_seen=ta.last_seen,
            created_at=ta.created_at,
            updated_at=ta.updated_at,
            references=ta.references,
            campaigns=[EntitySummary(id=c.id, name=c.name, entity_type="campaign") for c in _coerce(ta.campaigns)],
            malware=[EntitySummary(id=m.id, name=m.name, entity_type="malware") for m in _coerce(ta.malware)],
            indicators=[IndicatorSummary(id=i.id, type=i.type, value=i.value, confidence=i.confidence, severity=i.severity) for i in _coerce(ta.indicators)],
            mitre_techniques=[EntitySummary(id=t.id, name=t.name, entity_type="mitre_technique") for t in _coerce(ta.techniques)],
            timeline=timeline
        )

    @staticmethod
    def get_malware(db: Session, malware_id: str) -> MalwareDetailResponse:
        m = (
            db.query(Malware)
            .options(
                selectinload(Malware.campaigns),
                selectinload(Malware.threat_actors),
                selectinload(Malware.indicators),
                selectinload(Malware.techniques),
            )
            .filter(Malware.id == malware_id)
            .first()
        )
        if not m:
            raise HTTPException(status_code=404, detail="Malware not found")

        timeline: list[TimelineEvent] = []
        timeline.append(TimelineEvent(event_type="malware_created", description="Malware created", timestamp=m.created_at))
        timeline.sort(key=lambda x: x.timestamp, reverse=True)

        return MalwareDetailResponse(
            id=m.id,
            name=m.name,
            aliases=m.aliases,
            family=m.family,
            category=m.category,
            description=m.description,
            capabilities=m.capabilities,
            persistence=m.persistence,
            communication=m.communication,
            created_at=m.created_at,
            updated_at=m.updated_at,
            campaigns=[EntitySummary(id=c.id, name=c.name, entity_type="campaign") for c in _coerce(m.campaigns)],
            threat_actors=[EntitySummary(id=t.id, name=t.name, entity_type="threat_actor") for t in _coerce(m.threat_actors)],
            indicators=[IndicatorSummary(id=i.id, type=i.type, value=i.value, confidence=i.confidence, severity=i.severity) for i in _coerce(m.indicators)],
            mitre_techniques=[EntitySummary(id=t.id, name=t.name, entity_type="mitre_technique") for t in _coerce(m.techniques)],
            timeline=timeline
        )

    @staticmethod
    def get_campaign(db: Session, campaign_id: str) -> CampaignDetailResponse:
        c = (
            db.query(Campaign)
            .options(
                selectinload(Campaign.threat_actors),
                selectinload(Campaign.malware),
                selectinload(Campaign.indicators),
                selectinload(Campaign.reports),
            )
            .filter(Campaign.id == campaign_id)
            .first()
        )
        if not c:
            raise HTTPException(status_code=404, detail="Campaign not found")

        timeline: list[TimelineEvent] = []
        timeline.append(TimelineEvent(event_type="campaign_created", description="Campaign created", timestamp=c.created_at))
        timeline.sort(key=lambda x: x.timestamp, reverse=True)

        return CampaignDetailResponse(
            id=c.id,
            name=c.name,
            description=c.description,
            first_seen=c.first_seen,
            last_seen=c.last_seen,
            created_at=c.created_at,
            updated_at=c.updated_at,
            references=c.references,
            threat_actors=[EntitySummary(id=t.id, name=t.name, entity_type="threat_actor") for t in _coerce(c.threat_actors)],
            malware=[EntitySummary(id=m.id, name=m.name, entity_type="malware") for m in _coerce(c.malware)],
            indicators=[IndicatorSummary(id=i.id, type=i.type, value=i.value, confidence=i.confidence, severity=i.severity) for i in _coerce(c.indicators)],
            reports=[EntitySummary(id=r.id, name=r.title, entity_type="report") for r in _coerce(c.reports)],
            timeline=timeline
        )

    @staticmethod
    def get_vulnerability(db: Session, vuln_id: str) -> VulnerabilityDetailResponse:
        v = (
            db.query(Vulnerability)
            .options(
                selectinload(Vulnerability.threat_actors),
                selectinload(Vulnerability.campaigns),
                selectinload(Vulnerability.malware),
            )
            .filter(Vulnerability.id == vuln_id)
            .first()
        )
        if not v:
            raise HTTPException(status_code=404, detail="Vulnerability not found")
            
        timeline: list[TimelineEvent] = []
        timeline.append(TimelineEvent(event_type="vulnerability_created", description="Vulnerability created", timestamp=v.created_at))
        timeline.sort(key=lambda x: x.timestamp, reverse=True)

        # Malwares aren't directly on vulnerability by default? Let's check model.
        # Actually I can just return an empty list for malware if there isn't a direct link in the model, or I can skip it if the model doesn't have it.
        # Let's see if Vulnerability has malware.
        malwares = getattr(v, "malware", [])

        return VulnerabilityDetailResponse(
            id=v.id,
            cve=v.cve,
            description=v.description,
            cvss=v.cvss,
            epss=v.epss,
            kev=v.kev,
            exploited=v.exploited,
            patch_available=v.patch_available,
            created_at=v.created_at,
            updated_at=v.updated_at,
            references=v.references,
            threat_actors=[EntitySummary(id=t.id, name=t.name, entity_type="threat_actor") for t in _coerce(v.threat_actors)],
            campaigns=[EntitySummary(id=c.id, name=c.name, entity_type="campaign") for c in _coerce(v.campaigns)],
            malware=[EntitySummary(id=m.id, name=m.name, entity_type="malware") for m in _coerce(v.malware)],
            timeline=timeline
        )
