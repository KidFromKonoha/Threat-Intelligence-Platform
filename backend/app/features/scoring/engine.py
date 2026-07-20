"""Operational Scoring Engine (Stage D).

This engine isolates scoring logic from ingestion and enrichment. It computes a
final `risk_score` for an Indicator based on its confidence, severity, type,
and relevance (e.g. Automotive sector context).
"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.enums import Severity
from app.features.indicators.models import Indicator


class ScoringEngine:
    """Calculates operational priority scores for Indicators."""
    
    # Severity base weights
    SEVERITY_WEIGHTS = {
        Severity.CRITICAL.value: 40,
        Severity.HIGH.value: 30,
        Severity.MEDIUM.value: 20,
        Severity.LOW.value: 10,
        Severity.INFO.value: 0,
    }
    
    # Automotive relevance tags (example subset)
    AUTOMOTIVE_TAGS = {"automotive", "supplier", "oem", "manufacturing", "logistics"}

    @classmethod
    def calculate_risk_score(cls, indicator: Indicator) -> int:
        """Calculate the overall risk score (0-100) for an indicator.
        
        The score is derived from:
        1. Confidence (0-100) scaled.
        2. Severity base weight.
        3. Automotive relevance (bonus points).
        """
        base_score = 0
        
        # 1. Severity contribution (up to 40 points)
        base_score += cls.SEVERITY_WEIGHTS.get(indicator.severity, 10)
        
        # 2. Confidence contribution (up to 40 points)
        # Scaled: confidence 100 -> 40 points, confidence 50 -> 20 points
        confidence_points = int((indicator.confidence / 100.0) * 40)
        base_score += confidence_points
        
        # 3. Automotive Relevance (up to 20 points)
        relevance_points = 0
        if indicator.tags:
            for tag in indicator.tags:
                if tag.lower() in cls.AUTOMOTIVE_TAGS:
                    relevance_points = 20
                    break
                    
        total_score = base_score + relevance_points
        
        # Cap at 100
        return min(max(total_score, 0), 100)

    @classmethod
    def bulk_calculate_risk_scores(
        cls, db: Session, batch_size: int = 500, scoring_version: int = 1
    ) -> list[dict]:
        """Processes a chunk of indicators that need scoring using SKIP LOCKED concurrency.
        
        Returns the list of mappings updated.
        """
        import logging
        logger = logging.getLogger(__name__)

        # 1. Select a chunk of indicators requiring scoring, locking them
        stmt = (
            select(Indicator)
            .where(Indicator.needs_scoring == True)
            .limit(batch_size)
            .with_for_update(skip_locked=True)
        )
        indicators = db.scalars(stmt).all()
        
        if not indicators:
            return []
            
        # 2. Calculate new scores
        mappings = []
        now = datetime.now(timezone.utc)
        for ind in indicators:
            try:
                new_score = cls.calculate_risk_score(ind)
                mappings.append({
                    "id": ind.id,
                    "risk_score": new_score,
                    "risk_score_version": scoring_version,
                    "needs_scoring": False,
                    "scored_at": now,
                    "scoring_failed": False,
                    "last_scoring_error": None,
                    "last_scoring_attempt_at": now
                })
            except Exception as exc:
                exc_type = type(exc).__name__
                exc_msg = str(exc)
                feed_ids = [f.id for f in getattr(ind, "feeds", [])]
                
                logger.error(
                    "Poison pill indicator failed scoring.",
                    extra={
                        "indicator_id": ind.id,
                        "feed_ids": feed_ids,
                        "indicator_type": ind.type,
                        "exception_type": exc_type,
                        "exception_message": exc_msg
                    },
                    exc_info=True
                )
                # Clear needs_scoring to prevent infinite loop
                mappings.append({
                    "id": ind.id,
                    "needs_scoring": False,
                    "scoring_failed": True,
                    "last_scoring_error": f"{exc_type}: {exc_msg}",
                    "last_scoring_attempt_at": now
                })
            
        # 3. Bulk update
        db.bulk_update_mappings(Indicator, mappings)
        db.commit()
        
        return mappings
