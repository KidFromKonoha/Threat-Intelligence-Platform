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

import pkgutil
import app.features

# Dynamically discover all feature packages (e.g. app.features.feeds, app.features.enrichment)
# so Celery can correctly find their tasks.py modules.
feature_packages = [
    f"app.features.{module_info.name}"
    for module_info in pkgutil.iter_modules(app.features.__path__)
    if module_info.ispkg
]
celery_app.autodiscover_tasks(feature_packages, related_name="tasks")

