"""Celery tasks for the feeds feature.

Two tasks are defined here:

1. ``feeds.run_collector`` (feed_name: str) — Executes a single named feed
   collector end-to-end.  Called by the scheduler and can be enqueued manually.

2. ``feeds.tick_scheduler`` — Called by Celery Beat every minute.  Delegates to
   FeedScheduler.tick() which decides which feeds are due based on their
   ``schedule`` cron expression and dispatches ``run_collector`` tasks.

Celery autodiscovery (configured in app/core/celery_app.py) picks up this
module automatically — no registration elsewhere is required.
"""

from __future__ import annotations

from app.core.celery_app import celery_app
from app.core.logging import get_logger
from app.features.feeds.runner import FeedRunner

logger = get_logger(__name__)


@celery_app.task(
    name="feeds.run_collector",
    bind=True,
    max_retries=0,          # Retries are handled inside FeedRunner, not Celery.
    acks_late=True,         # Acknowledge only after task completes.
    reject_on_worker_lost=True,
)
def run_collector(self: object, feed_name: str) -> dict:
    """Execute a single feed collector by name.

    Args:
        feed_name: The collector's feed_name, which must match a Feed.name
                   row in the database and a registered collector class.

    Returns:
        A dict summary of CollectorMetrics — serializable for Celery result backend.
    """
    logger.info("Celery task feeds.run_collector started for feed=%r", feed_name)
    runner = FeedRunner(feed_name=feed_name)
    metrics = runner.run()
    logger.info(
        "Celery task feeds.run_collector finished for feed=%r — added=%d errors=%d",
        feed_name,
        metrics.records_added,
        len(metrics.errors),
    )
    return metrics.model_dump()


@celery_app.task(
    name="feeds.tick_scheduler",
    bind=True,
    max_retries=0,
    acks_late=True,
)
def tick_scheduler(self: object) -> dict:
    """Evaluate all enabled feeds and dispatch run_collector tasks for those due.

    Intended to be called by Celery Beat every minute via the beat_schedule in
    app/core/celery_app.py.

    Returns:
        A dict with ``dispatched`` (list of feed names that were enqueued).
    """
    from app.features.feeds.scheduler import scheduler  # noqa: PLC0415 (lazy import to avoid circular deps at module load)

    logger.info("Celery task feeds.tick_scheduler running.")
    dispatched = scheduler.tick()
    logger.info(
        "Celery task feeds.tick_scheduler done — dispatched=%d feeds.", len(dispatched)
    )
    return {"dispatched": dispatched}
