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
    def run_enrichment_sync(db: Session, indicator_id: str) -> None:
        """Run all applicable enrichment providers synchronously for an indicator.
        
        Typically called from a Celery worker.
        """
        enrichment_registry.autodiscover()
        
        indicator = db.query(Indicator).filter(Indicator.id == indicator_id).first()
        if not indicator:
            logger.warning("[enrichment] Indicator %s not found. Aborting.", indicator_id)
            return

        providers = enrichment_registry.get_all()
        logger.info("[enrichment] Starting enrichment for indicator=%s (type=%s) with %d registered providers", 
                    indicator_id, indicator.type, len(providers))

        for provider_cls in providers:
            if indicator.type not in provider_cls.supported_indicator_types:
                continue

            provider_name = provider_cls.provider_name
            logger.info("[enrichment] Running provider=%s for indicator=%s", provider_name, indicator_id)
            
            provider = provider_cls()
            t0 = time.monotonic()
            
            # Create a pending result record first
            result_record = EnrichmentResult(
                indicator_id=indicator_id,
                provider=provider_name,
                execution_status=EnrichmentStatus.PENDING.value
            )
            db.add(result_record)
            db.commit()
            
            try:
                # Execute the provider
                result_data = provider.enrich(indicator)
                
                duration = time.monotonic() - t0
                result_record.execution_status = EnrichmentStatus.SUCCESS.value
                result_record.execution_duration = duration
                result_record.raw_response = result_data.raw_response
                result_record.extracted_attributes = result_data.extracted_attributes
                
                logger.info("[enrichment] Provider=%s succeeded for indicator=%s in %.3fs", 
                            provider_name, indicator_id, duration)
                            
            except Exception as e:
                duration = time.monotonic() - t0
                logger.exception("[enrichment] Provider=%s failed for indicator=%s: %s", 
                                 provider_name, indicator_id, str(e))
                                 
                result_record.execution_status = EnrichmentStatus.FAILED.value
                result_record.execution_duration = duration
                # Do not re-raise! Isolate provider failures.
                
            finally:
                db.add(result_record)
                db.commit()

        logger.info("[enrichment] Enrichment complete for indicator=%s", indicator_id)
