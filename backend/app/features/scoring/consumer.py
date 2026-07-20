import logging
from sqlalchemy.orm import Session
from sqlalchemy import update

from app.features.indicators.models import Indicator

logger = logging.getLogger(__name__)

class ScoringConsumerService:
    @staticmethod
    def handle_relationships_updated(db: Session, indicator_id: str) -> None:
        """Mark an indicator as needing scoring after relationships are updated."""
        
        # Use a targeted update statement for efficiency rather than ORM load/save
        stmt = (
            update(Indicator)
            .where(Indicator.id == indicator_id)
            .values(needs_scoring=True)
        )
        result = db.execute(stmt)
        if result.rowcount > 0:
            logger.info("[scoring_consumer] Marked indicator=%s needs_scoring=True", indicator_id)
            db.commit()
        else:
            logger.warning("[scoring_consumer] Indicator=%s not found to mark for scoring", indicator_id)
            db.rollback()
