from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select, or_, func

from app.features.indicators.models import Indicator
from app.features.threat_actors.models import ThreatActor
from app.features.campaigns.models import Campaign
from app.features.malware.models import Malware
from app.features.mitre.models import MITRETechnique
from app.features.assets.models import Asset
from app.features.enrichment.models import EnrichmentResult
from app.features.investigation.models import EntityEvent

class IndicatorBundleBuilder:
    @staticmethod
    def build(db: Session, indicator_id: str) -> dict:
        indicator = db.query(Indicator).options(
            selectinload(Indicator.threat_actors),
            selectinload(Indicator.campaigns),
            selectinload(Indicator.malware),
            selectinload(Indicator.techniques),
            selectinload(Indicator.assets)
        ).filter(Indicator.id == indicator_id).first()
        
        if not indicator:
            return None
            
        enrichments = db.query(EnrichmentResult).filter(EnrichmentResult.indicator_id == indicator_id).all()
        timeline = TimelineService.get_timeline(db, "indicator", indicator_id)
        
        # Convert ORM to dict to avoid detached instance issues, or just rely on Pydantic's from_attributes
        def to_dict(obj):
            if not obj: return {}
            return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
            
        return {
            "indicator": to_dict(indicator),
            "risk_score": indicator.risk_score,
            "enrichment": [to_dict(e) for e in enrichments],
            "threat_actors": [to_dict(ta) for ta in (indicator.threat_actors or [])],
            "campaigns": [to_dict(c) for c in (indicator.campaigns or [])],
            "malware": [to_dict(m) for m in (indicator.malware or [])],
            "mitre_techniques": [to_dict(t) for t in (indicator.techniques or [])],
            "assets": [to_dict(a) for a in (indicator.assets or [])],
            "timeline": [to_dict(t) for t in (timeline or [])]
        }

class ThreatActorBundleBuilder:
    @staticmethod
    def build(db: Session, actor_id: str) -> dict:
        actor = db.query(ThreatActor).options(
            selectinload(ThreatActor.indicators),
            selectinload(ThreatActor.campaigns),
            selectinload(ThreatActor.malware),
            selectinload(ThreatActor.techniques)
        ).filter(ThreatActor.id == actor_id).first()
        
        if not actor:
            return None
            
        def to_dict(obj):
            return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
            
        return {
            "threat_actor": to_dict(actor),
            "indicators": [to_dict(i) for i in (actor.indicators or [])],
            "campaigns": [to_dict(c) for c in (actor.campaigns or [])],
            "malware": [to_dict(m) for m in (actor.malware or [])],
            "mitre_techniques": [to_dict(t) for t in (actor.techniques or [])]
        }

class CampaignBundleBuilder:
    @staticmethod
    def build(db: Session, campaign_id: str) -> dict:
        campaign = db.query(Campaign).options(
            selectinload(Campaign.threat_actors),
            selectinload(Campaign.indicators),
            selectinload(Campaign.malware),
            selectinload(Campaign.techniques)
        ).filter(Campaign.id == campaign_id).first()
        
        if not campaign:
            return None
            
        def to_dict(obj):
            return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
            
        return {
            "campaign": to_dict(campaign),
            "threat_actors": [to_dict(ta) for ta in (campaign.threat_actors or [])],
            "indicators": [to_dict(i) for i in (campaign.indicators or [])],
            "malware": [to_dict(m) for m in (campaign.malware or [])],
            "mitre_techniques": [to_dict(t) for t in (campaign.techniques or [])]
        }

class TimelineService:
    @staticmethod
    def get_timeline(db: Session, entity_type: str, entity_id: str):
        return db.query(EntityEvent).filter(
            EntityEvent.entity_type == entity_type,
            EntityEvent.entity_id == entity_id
        ).order_by(EntityEvent.created_at).all()

class SearchService:
    @staticmethod
    def search(db: Session, query: str) -> dict:
        search_term = f"%{query}%"
        
        def to_dict(obj):
            return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
            
        indicators = db.query(Indicator).filter(
            or_(Indicator.value.ilike(search_term), Indicator.normalized_value.ilike(search_term))
        ).limit(20).all()
        
        threat_actors = db.query(ThreatActor).filter(ThreatActor.name.ilike(search_term)).limit(10).all()
        
        campaigns = db.query(Campaign).filter(Campaign.name.ilike(search_term)).limit(10).all()
        
        malware = db.query(Malware).filter(Malware.name.ilike(search_term)).limit(10).all()
        
        assets = db.query(Asset).filter(
            or_(Asset.hostname.ilike(search_term), Asset.ip_address.ilike(search_term))
        ).limit(10).all()
        
        return {
            "indicators": [to_dict(i) for i in indicators],
            "threat_actors": [to_dict(t) for t in threat_actors],
            "campaigns": [to_dict(c) for c in campaigns],
            "malware": [to_dict(m) for m in malware],
            "assets": [to_dict(a) for a in assets]
        }
