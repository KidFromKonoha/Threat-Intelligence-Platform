"""Celery tasks for the Scoring Engine.

This task is designed to be executed after Stage B (Enrichment) and 
Stage C (Graph Engine) complete, ensuring that the risk score includes
all newly built relationships and context.
"""

from celery import shared_task
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.features.scoring.engine import ScoringEngine
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def bulk_score_indicators_task(self) -> None:
    """Compute and update risk_scores for a chunk of pending indicators."""
    db: Session = SessionLocal()
    try:
        batch_size = settings.SCORING_BATCH_SIZE
        scoring_version = settings.SCORING_VERSION
        
        mappings = ScoringEngine.bulk_calculate_risk_scores(
            db, batch_size=batch_size, scoring_version=scoring_version
        )
        
        scored_count = len(mappings)
        if scored_count > 0:
            logger.info("Bulk scored %d indicators", scored_count)
            
            # Publish events for successful scores
            try:
                from app.core.events.bus import RedisEventBus
                from app.core.events.schema import EventEnvelope, RiskScoreCalculatedPayload
                bus = RedisEventBus()
                for mapping in mappings:
                    if not mapping.get("scoring_failed", False):
                        payload = RiskScoreCalculatedPayload(
                            indicator_id=mapping["id"],
                            risk_score=mapping["risk_score"],
                            risk_score_version=mapping["risk_score_version"]
                        )
                        envelope = EventEnvelope(
                            producer="ScoringEngine",
                            payload=payload
                        )
                        bus.publish("tip.events.risk_score.calculated", envelope)
                        
                        # The Audit Logger consumer will capture RiskScoreCalculated 
                        # and insert the EntityEvent asynchronously.
                
                db.commit()
            except Exception as exc:
                logger.error("Failed to publish risk_score.calculated events: %s", exc)
            
        # If we hit the limit, there might be more backlog. Trigger immediately.
        if scored_count == batch_size:
            logger.info("Batch limit reached (%d), scheduling another chunk immediately", batch_size)
            self.apply_async()
            
    except Exception as exc:
        db.rollback()
        logger.error("Error in bulk scoring: %s", exc)
        self.retry(exc=exc)
    finally:
        db.close()
