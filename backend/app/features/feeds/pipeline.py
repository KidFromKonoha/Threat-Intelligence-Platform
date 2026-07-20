"""Feed ingestion pipelines: validation, normalization, and storage.

Each pipeline is a single-responsibility class that the FeedRunner calls
in sequence.  Collectors never interact with these directly.

Pipelines:
- ValidationPipeline  : filters out records that fail Pydantic validation.
- NormalizationPipeline: delegates to the collector's normalize() method.
- StoragePipeline     : upserts RawIndicator objects into the database.

The StoragePipeline implements deduplication using the unique constraint
(type, normalized_value) on the indicators table.  On conflict it updates
last_seen, confidence, and source_count rather than creating a duplicate.
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import ValidationError
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.features.feeds.schemas import CollectorMetrics, RawIndicator

logger = logging.getLogger(__name__)


class ValidationPipeline:
    """Drops records that cannot be coerced into valid RawIndicator objects.

    Invalid records are counted as skipped in metrics — they never reach
    the normalization or storage steps.
    """

    def run(
        self,
        raw_records: list[Any],
        metrics: CollectorMetrics,
    ) -> list[Any]:
        """Return only records that pass a basic non-empty / non-None check.

        Structural validation happens in NormalizationPipeline when the
        collector's normalize() produces RawIndicator objects, which Pydantic
        validates at construction time.
        """
        valid: list[Any] = []
        for record in raw_records:
            if record is None:
                metrics.records_skipped += 1
                logger.debug("[%s] Skipped None record", metrics.feed_name)
                continue
            valid.append(record)
        return valid


class NormalizationPipeline:
    """Delegates to the collector's normalize() method and validates output."""

    def run(
        self,
        collector: Any,  # BaseCollector
        validated_records: list[Any],
        metrics: CollectorMetrics,
    ) -> list[RawIndicator]:
        """Call collector.normalize() and filter out any invalid results."""
        normalized: list[RawIndicator] = []

        try:
            candidates = collector.normalize(validated_records)
        except Exception as exc:
            error_msg = f"normalize() raised an unexpected error: {exc}"
            logger.error("[%s] %s", metrics.feed_name, error_msg)
            metrics.errors.append(error_msg)
            return normalized

        for candidate in candidates:
            if isinstance(candidate, RawIndicator):
                normalized.append(candidate)
            else:
                # Collector returned something unexpected — try to coerce.
                try:
                    normalized.append(RawIndicator.model_validate(candidate))
                except ValidationError as exc:
                    metrics.records_skipped += 1
                    logger.warning(
                        "[%s] Normalization produced an invalid record, skipping: %s",
                        metrics.feed_name,
                        exc,
                    )

        return normalized


class StoragePipeline:
    """Upserts RawIndicator objects into the indicators table.

    Deduplication strategy:
    - The unique index (type, normalized_value) is the conflict target.
    - On conflict: update last_seen, confidence, source_count, updated_at.
    - New records: full insert.

    This pipeline also links the stored indicator to its Feed row.
    """
    
    def __init__(self, event_bus: 'EventBus' = None):
        self.event_bus = event_bus

    def run(
        self,
        db: Session,
        feed_id: str,
        indicators: list[RawIndicator],
        metrics: CollectorMetrics,
    ) -> None:
        """Upsert all indicators and update metrics in-place."""
        from datetime import datetime, timezone
        from sqlalchemy import select, text
        from app.db.associations import indicator_feed
        from app.features.indicators.models import Indicator
        from app.core.events.schema import EventEnvelope, IndicatorPersistedPayload
        import uuid

        events_to_publish = []
        now = datetime.now(tz=timezone.utc)
        
        # Prepare values
        values_list = []
        for raw in indicators:
            metrics.records_received += 1
            values_list.append({
                "id": str(uuid.uuid4()),
                "type": raw.type,
                "value": raw.value,
                "normalized_value": raw.normalized_value,
                "confidence": raw.confidence,
                "severity": raw.severity,
                "risk_score": raw.risk_score,
                "status": raw.status,
                "first_seen": raw.first_seen,
                "last_seen": raw.last_seen,
                "country": raw.country,
                "asn": raw.asn,
                "tags": raw.tags,
                "source_count": 1,
                "created_at": now,
                "updated_at": now,
            })
            
        if not values_list:
            return

        try:
            stmt = pg_insert(Indicator)
            stmt = stmt.on_conflict_do_update(
                index_elements=["type", "normalized_value"],
                set_={
                    "last_seen": stmt.excluded.last_seen,
                    "confidence": Indicator.confidence,
                    "source_count": Indicator.source_count + 1,
                    "updated_at": now,
                    "needs_scoring": True,
                },
            ).returning(Indicator.id, Indicator.created_at, Indicator.updated_at)

            results = db.execute(stmt, values_list).fetchall()
            
            feed_links = []
            for row in results:
                indicator_id = row[0]
                was_inserted = row[1] == row[2]

                if was_inserted:
                    metrics.records_added += 1
                    if self.event_bus:
                        payload = IndicatorPersistedPayload(
                            indicator_id=str(indicator_id),
                            feed_id=feed_id
                        )
                        envelope = EventEnvelope(
                            producer="StoragePipeline",
                            payload=payload
                        )
                        events_to_publish.append(envelope)
                else:
                    metrics.records_updated += 1
                    
                feed_links.append({"indicator_id": indicator_id, "feed_id": feed_id})

            if feed_links:
                db.execute(
                    pg_insert(indicator_feed)
                    .on_conflict_do_nothing(),
                    feed_links
                )

        except Exception as exc:
            error_msg = f"Failed bulk indicator upsert: {exc}"
            logger.error("[%s] %s", metrics.feed_name, error_msg)
            metrics.errors.append(error_msg)
            db.rollback()
            return

        # Only publish events if the entire batch commits successfully
        db.commit()
        
        if self.event_bus:
            for event in events_to_publish:
                self.event_bus.publish("tip.events.indicator.persisted", event)
