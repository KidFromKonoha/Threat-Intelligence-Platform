"""EnrichmentService — executes providers and orchestrates the enrichment process."""

from __future__ import annotations

import time

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.logging import get_logger
from app.db.enums import EnrichmentStatus
from app.features.enrichment.models import EnrichmentResult
from app.features.enrichment.registry import enrichment_registry
from app.features.enrichment.schemas import EnrichmentStatusResponse, EnrichmentSummary
from app.features.indicators.models import Indicator

logger = get_logger(__name__)


class EnrichmentService:
    """Service layer for indicator enrichment operations."""

    @staticmethod
    def get_status(db: Session, indicator_id: str) -> EnrichmentStatusResponse:
        """Get the enrichment status and history for a given indicator."""
        # Validate indicator exists
        indicator = db.query(Indicator).filter(Indicator.id == indicator_id).first()
        if not indicator:
            return None  # Let router handle 404

        results = (
            db.query(EnrichmentResult)
            .filter(EnrichmentResult.indicator_id == indicator_id)
            .order_by(desc(EnrichmentResult.created_at))
            .all()
        )

        summaries = [EnrichmentSummary.model_validate(r) for r in results]
        
        last_enrichment = None
        if results:
            last_enrichment = max(r.created_at for r in results)

        return EnrichmentStatusResponse(
            indicator_id=indicator_id,
            providers_executed=len(results),
            last_enrichment_at=last_enrichment,
            results=summaries,
        )

    @staticmethod
    def run_enrichment_sync(db: Session, indicator_id: str, event_bus: 'EventBus' = None, correlation_id: str = None) -> None:
        """Run all applicable enrichment providers synchronously for an indicator.
        
        Typically called from the enrichment worker.
        """
        from datetime import datetime, timezone
        import uuid
        from app.core.events.schema import EventEnvelope, IndicatorEnrichedPayload

        enrichment_registry.autodiscover()
        
        indicator = db.query(Indicator).filter(Indicator.id == indicator_id).first()
        if not indicator:
            logger.warning("[enrichment] Indicator %s not found. Aborting.", indicator_id)
            return

        providers = enrichment_registry.get_all()
        logger.info("[enrichment] Starting enrichment for indicator=%s (type=%s) with %d registered providers", 
                    indicator_id, indicator.type, len(providers))

        results_saved = False

        for provider_cls in providers:
            provider_name = provider_cls.provider_name
            
            # Create a pending result record first
            result_record = EnrichmentResult(
                indicator_id=indicator_id,
                provider=provider_name,
                status=EnrichmentStatus.PENDING.value
            )
            db.add(result_record)
            db.commit()

            if indicator.type not in provider_cls.supported_indicator_types:
                logger.info("[enrichment] Skipping provider=%s for indicator=%s (unsupported type)", provider_name, indicator_id)
                result_record.status = EnrichmentStatus.NOT_SUPPORTED.value
                result_record.completed_at = datetime.now(timezone.utc)
                db.add(result_record)
                db.commit()
                continue

            logger.info("[enrichment] Running provider=%s for indicator=%s", provider_name, indicator_id)
            
            provider = provider_cls()
            
            try:
                # Execute the provider
                result_data = provider.enrich(indicator)
                
                result_record.status = EnrichmentStatus.SUCCESS.value
                result_record.raw_response = result_data.raw_response
                result_record.extracted_attributes = result_data.extracted_attributes
                result_record.completed_at = datetime.now(timezone.utc)
                
                # Assume provider_version and expires_at could be part of the result,
                # but for now we leave them as what the base provides (or null).
                if hasattr(provider_cls, 'provider_version'):
                    result_record.provider_version = provider_cls.provider_version
                    
                # We could support an explicit ttl from the provider here in the future
                
                logger.info("[enrichment] Provider=%s succeeded for indicator=%s", 
                            provider_name, indicator_id)
                            
            except Exception as e:
                logger.exception("[enrichment] Provider=%s failed for indicator=%s: %s", 
                                 provider_name, indicator_id, str(e))
                                 
                result_record.status = EnrichmentStatus.FAILED.value
                result_record.error = str(e)
                result_record.completed_at = datetime.now(timezone.utc)
                # Do not re-raise! Isolate provider failures.
                
            finally:
                db.add(result_record)
                db.commit()
                results_saved = True

        logger.info("[enrichment] Enrichment complete for indicator=%s", indicator_id)

        # Publish the IndicatorEnriched event after all providers have run and committed
        if results_saved and event_bus:
            payload = IndicatorEnrichedPayload(indicator_id=indicator_id)
            envelope = EventEnvelope(
                producer="EnrichmentEngine",
                payload=payload,
                correlation_id=correlation_id if correlation_id else str(uuid.uuid4())
            )
            event_bus.publish("tip.events.indicator.enriched", envelope)
            logger.info("[enrichment] Published IndicatorEnriched event for %s", indicator_id)
            
            # Add audit event
            # Audit event will be handled by audit_worker.py consuming IndicatorEnriched.
