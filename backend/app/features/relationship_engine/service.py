import logging
from sqlalchemy.orm import Session
from sqlalchemy import text, func

from app.features.indicators.models import Indicator
from app.features.threat_actors.models import ThreatActor

logger = logging.getLogger(__name__)

class TagThreatActorExtractor:
    """Extracts relationships between Indicators and ThreatActors based on matching tags."""
    
    @staticmethod
    def extract_and_link(db: Session, indicator: Indicator) -> int:
        if not indicator.tags:
            return 0
            
        tags_lower = [str(t).lower() for t in indicator.tags]
        
        # Find ThreatActors whose name matches one of the tags (case-insensitive)
        matching_actors = db.query(ThreatActor).filter(
            func.lower(ThreatActor.name).in_(tags_lower)
        ).all()
        
        if not matching_actors:
            return 0
            
        linked_count = 0
        for actor in matching_actors:
            # Idempotent insert using native PostgreSQL UPSERT syntax
            stmt = text("""
                INSERT INTO indicator_threat_actor (indicator_id, threat_actor_id)
                VALUES (:ind_id, :ta_id)
                ON CONFLICT DO NOTHING
            """)
            result = db.execute(stmt, {"ind_id": indicator.id, "ta_id": actor.id})
            if result.rowcount > 0:
                linked_count += 1
                logger.info(
                    "[relationship_engine] Linked Indicator=%s to ThreatActor=%s (Matched tag: %s)",
                    indicator.id, actor.id, actor.name
                )
                
        return linked_count


class RelationshipEngineService:
    """Evaluates relationships for a given indicator using registered extractors."""
    
    @staticmethod
    def run_engine_sync(db: Session, indicator_id: str, event_bus=None) -> None:
        """Run the relationship engine synchronously for an indicator."""
        logger.info("[relationship_engine] Starting evaluation for indicator=%s", indicator_id)
        
        indicator = db.query(Indicator).filter(Indicator.id == indicator_id).first()
        if not indicator:
            logger.warning("[relationship_engine] Indicator=%s not found.", indicator_id)
            return
            
        total_links = 0
        
        try:
            # Extractor 1: Tags -> Threat Actor
            links = TagThreatActorExtractor.extract_and_link(db, indicator)
            total_links += links
            
            db.commit()
            logger.info("[relationship_engine] Evaluation complete for indicator=%s. Created %d new edges.", indicator_id, total_links)
            
            if total_links > 0 and event_bus:
                from app.core.events.schema import EventEnvelope, RelationshipsUpdatedPayload
                
                payload = RelationshipsUpdatedPayload(
                    indicator_id=indicator_id,
                    new_edges_count=total_links
                )
                envelope = EventEnvelope(
                    producer="RelationshipEngine",
                    payload=payload
                )
                event_bus.publish("tip.events.relationships.updated", envelope)
                
                # Add audit event
                # Audit event will be handled by audit_worker.py consuming RelationshipsUpdated.
                
        except Exception as exc:
            db.rollback()
            logger.exception("[relationship_engine] Failed to evaluate relationships for indicator=%s", indicator_id)
            raise
