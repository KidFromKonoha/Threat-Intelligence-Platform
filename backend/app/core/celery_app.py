from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "tip",
    broker=settings.CELERY_BROKER,
    backend=settings.CELERY_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # ── Celery Beat schedule ──────────────────────────────────────────────────
    # tick_scheduler runs every 60 seconds and dispatches run_collector tasks
    # for any feed whose cron schedule (Feed.schedule) is currently due.
    beat_schedule={
        "feeds-tick-every-minute": {
            "task": "feeds.tick_scheduler",
            "schedule": 60.0,   # seconds
        },
    },
)

# Feature task modules are auto-discovered by their feature package path,
# e.g. app.features.<feature>.tasks. None exist yet in Phase 1.
celery_app.autodiscover_tasks(["app.features"], related_name="tasks")

