from datetime import datetime, timezone
from typing import Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

from app.db.associations import investigation_indicator
from app.features.investigations.models import Investigation
from app.features.investigations.schemas import (
    InvestigationCreate,
    InvestigationUpdate,
    InvestigationSummaryResponse,
    InvestigationTimelineEvent,
)
from app.features.indicators.models import Indicator
from app.features.correlation.service import CorrelationService
from app.features.search.schemas import EntitySummary, IndicatorSummary
from app.features.enrichment.models import EnrichmentResult


class InvestigationService:
    @staticmethod
    def get_investigations(db: Session, skip: int = 0, limit: int = 100) -> list[Investigation]:
        return db.query(Investigation).order_by(Investigation.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_investigation(db: Session, investigation_id: str) -> Investigation:
        inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
        if not inv:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation not found")
        return inv

    @staticmethod
    def create_investigation(db: Session, inv_in: InvestigationCreate) -> Investigation:
        inv = Investigation(**inv_in.model_dump(exclude_unset=True))
        db.add(inv)
        db.commit()
        db.refresh(inv)
        return inv

    @staticmethod
    def update_investigation(db: Session, investigation_id: str, inv_in: InvestigationUpdate) -> Investigation:
        inv = InvestigationService.get_investigation(db, investigation_id)
        update_data = inv_in.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(inv, key, value)
            
        if inv_in.status == "closed" and not inv.closed_at:
            inv.closed_at = datetime.now(timezone.utc)
        elif inv_in.status != "closed":
            inv.closed_at = None
            
        db.commit()
        db.refresh(inv)
        return inv

    @staticmethod
    def delete_investigation(db: Session, investigation_id: str) -> None:
        inv = InvestigationService.get_investigation(db, investigation_id)
        db.delete(inv)
        db.commit()

    @staticmethod
    def add_indicator(db: Session, investigation_id: str, indicator_id: str) -> None:
        inv = InvestigationService.get_investigation(db, investigation_id)
        ind = db.query(Indicator).filter(Indicator.id == indicator_id).first()
        if not ind:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indicator not found")
            
        # Check if already linked using a query to avoid loading all indicators
        stmt = select(investigation_indicator).where(
            investigation_indicator.c.investigation_id == investigation_id,
            investigation_indicator.c.indicator_id == indicator_id
        )
        if db.execute(stmt).first():
            return  # Already linked
            
        inv.indicators.append(ind)
        db.commit()

    @staticmethod
    def remove_indicator(db: Session, investigation_id: str, indicator_id: str) -> None:
        inv = InvestigationService.get_investigation(db, investigation_id)
        ind = db.query(Indicator).filter(Indicator.id == indicator_id).first()
        if not ind:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indicator not found")
            
        if ind in inv.indicators:
            inv.indicators.remove(ind)
            db.commit()

    @staticmethod
    def get_summary(db: Session, investigation_id: str) -> InvestigationSummaryResponse:
        inv = db.query(Investigation).options(
            selectinload(Investigation.indicators)
        ).filter(Investigation.id == investigation_id).first()
        
        if not inv:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation not found")
            
        # Aggregate relationships for all linked indicators using CorrelationService
        indicators = []
        malware = {}
        campaigns = {}
        threat_actors = {}
        reports = {}
        mitre_techniques = {}
        vulnerabilities = {}
        
        for ind in inv.indicators:
            indicators.append(IndicatorSummary(
                id=ind.id,
                type=ind.type,
                value=ind.value,
                confidence=ind.confidence,
                severity=ind.severity
            ))
            
            # Fetch relationships
            rels = CorrelationService.get_relationships(db, ind.id)
            
            for m in rels.malware:
                malware[m.id] = EntitySummary(id=m.id, name=m.name, entity_type="malware", description=m.description)
            for c in rels.campaigns:
                campaigns[c.id] = EntitySummary(id=c.id, name=c.name, entity_type="campaign", description=c.description)
            for ta in rels.threat_actors:
                threat_actors[ta.id] = EntitySummary(id=ta.id, name=ta.name, entity_type="threat_actor", description=ta.description)
            for r in rels.reports:
                reports[r.id] = EntitySummary(id=r.id, name=r.title, entity_type="report", description=r.summary)
            for t in rels.mitre_techniques:
                mitre_techniques[t.id] = EntitySummary(id=t.id, name=t.name, entity_type="mitre_technique", description=t.description)
            for v in rels.vulnerabilities:
                vulnerabilities[v.id] = EntitySummary(id=v.id, name=v.cve, entity_type="vulnerability", description=v.description)
                
        return InvestigationSummaryResponse(
            investigation=inv,
            indicators=indicators,
            malware=list(malware.values()),
            threat_actors=list(threat_actors.values()),
            campaigns=list(campaigns.values()),
            reports=list(reports.values()),
            mitre_techniques=list(mitre_techniques.values()),
            vulnerabilities=list(vulnerabilities.values())
        )

    @staticmethod
    def get_timeline(db: Session, investigation_id: str) -> list[InvestigationTimelineEvent]:
        inv = db.query(Investigation).filter(Investigation.id == investigation_id).first()
        if not inv:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investigation not found")
            
        events = []
        
        # 1. Investigation created
        events.append(InvestigationTimelineEvent(
            event_type="investigation_created",
            timestamp=inv.created_at,
            description="Investigation created",
            details={"title": inv.title, "priority": inv.priority}
        ))
        
        # 2. Investigation closed
        if inv.closed_at:
            events.append(InvestigationTimelineEvent(
                event_type="investigation_closed",
                timestamp=inv.closed_at,
                description="Investigation closed",
                details={}
            ))
            
        # 3. Indicators added
        stmt = select(investigation_indicator).where(
            investigation_indicator.c.investigation_id == investigation_id
        )
        assoc_rows = db.execute(stmt).all()
        ind_ids = []
        for row in assoc_rows:
            ind_ids.append(row.indicator_id)
            ind = db.query(Indicator).filter(Indicator.id == row.indicator_id).first()
            if ind:
                events.append(InvestigationTimelineEvent(
                    event_type="indicator_added",
                    timestamp=row.created_at,
                    description=f"Indicator added: {ind.value}",
                    details={"indicator_id": ind.id, "value": ind.value, "type": ind.type}
                ))
                
                # 4. Feed updates affecting linked indicators (Indicator.updated_at != created_at)
                if ind.updated_at and ind.updated_at > ind.created_at:
                    events.append(InvestigationTimelineEvent(
                        event_type="feed_update",
                        timestamp=ind.updated_at,
                        description=f"Feed update affected indicator: {ind.value}",
                        details={"indicator_id": ind.id, "value": ind.value}
                    ))
                    
        # 5. Enrichment executed
        if ind_ids:
            enrichments = db.query(EnrichmentResult).filter(EnrichmentResult.indicator_id.in_(ind_ids)).all()
            for e in enrichments:
                ind = db.query(Indicator).filter(Indicator.id == e.indicator_id).first()
                events.append(InvestigationTimelineEvent(
                    event_type="enrichment_executed",
                    timestamp=e.created_at,
                    description=f"Enrichment executed via {e.provider} on {ind.value if ind else e.indicator_id}",
                    details={"indicator_id": e.indicator_id, "provider": e.provider, "status": e.execution_status}
                ))
                
        # Sort newest first
        events.sort(key=lambda x: x.timestamp, reverse=True)
        return events
