"""Celery tasks for enrichment."""

from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.features.enrichment.service import EnrichmentService


@celery_app.task(name="app.features.enrichment.tasks.run_enrichment")
def run_enrichment(indicator_id: str) -> str:
    """Asynchronously execute enrichment for an indicator."""
    db = SessionLocal()
    try:
        EnrichmentService.run_enrichment_sync(db, indicator_id)
        return f"Enrichment completed for {indicator_id}"
    finally:
        db.close()
