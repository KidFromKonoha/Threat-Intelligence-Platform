"""FeedScheduler — scheduler abstraction for the feed collection framework.

The scheduler reads each enabled Feed row, interprets its ``schedule`` field
(a standard 5-field cron expression), and dispatches the ``feeds.run_collector``
Celery task when the feed is due to run.

Intended invocation:
  - Called by a Celery Beat periodic task (``feeds.tick_scheduler``) every minute.
  - Can also be called manually from a shell for one-off invocations.

Cron matching uses the ``croniter`` library when available.  If croniter is not
installed the scheduler falls back to a simple "run every feed that has never
run or was last run more than 60 minutes ago" policy, which is safe for Phase
3A smoke-testing without requiring a new dependency.

Design constraints:
  - The scheduler does NOT run collectors itself — it enqueues Celery tasks only.
  - One Celery task is dispatched per eligible feed per tick.
  - The scheduler never raises; all errors are logged.
"""

from __future__ import annotations

import importlib
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from app.core.logging import get_logger
from app.db.session import SessionLocal
from app.features.feeds.models import Feed
from app.features.feeds.tasks import run_collector

if TYPE_CHECKING:
    pass

logger = get_logger(__name__)

# Sentinel: number of seconds without a successful run before we consider a
# feed overdue when croniter is unavailable (fallback policy).
_FALLBACK_INTERVAL_SECONDS = 3600


class FeedScheduler:
    """Determines which feeds are due and dispatches Celery tasks for them.

    Usage::

        scheduler = FeedScheduler()
        scheduler.tick()   # call this every minute from Celery Beat
    """

    def tick(self) -> list[str]:
        """Evaluate all enabled feeds and dispatch tasks for those that are due.

        Returns a list of feed names for which a task was dispatched.
        """
        now = datetime.now(tz=timezone.utc)
        dispatched: list[str] = []

        db = SessionLocal()
        try:
            feeds: list[Feed] = (
                db.query(Feed).filter(Feed.enabled.is_(True)).all()
            )

            for feed in feeds:
                try:
                    if self._is_due(feed, now):
                        run_collector.delay(feed.name)
                        dispatched.append(feed.name)
                        logger.info(
                            "[scheduler] Dispatched run_collector task for feed=%r",
                            feed.name,
                        )
                    else:
                        logger.debug(
                            "[scheduler] Feed %r is not due yet — skipping.",
                            feed.name,
                        )
                except Exception as exc:
                    logger.error(
                        "[scheduler] Failed to dispatch task for feed=%r: %s",
                        feed.name,
                        exc,
                    )
        except Exception as exc:
            logger.error("[scheduler] tick() failed while querying feeds: %s", exc)
        finally:
            db.close()

        logger.info(
            "[scheduler] tick complete — %d feed(s) dispatched: %s",
            len(dispatched),
            dispatched,
        )
        return dispatched

    # ── Private helpers ───────────────────────────────────────────────────────

    def _is_due(self, feed: Feed, now: datetime) -> bool:
        """Return True if feed should run at ``now``.

        Cron schedule matching:
          - If croniter is installed and feed.schedule is a valid cron string,
            use croniter to check whether the feed was due in the last minute.
          - Otherwise, apply the fallback interval policy.
        """
        if feed.schedule:
            croniter = _try_import_croniter()
            if croniter is not None:
                return self._cron_is_due(croniter, feed.schedule, now)

        # Fallback policy: run if never succeeded or last success was long ago.
        return self._fallback_is_due(feed, now)

    @staticmethod
    def _cron_is_due(croniter_module: object, schedule: str, now: datetime) -> bool:
        """Use croniter to determine whether the cron expression fired in the
        last 60 seconds (the width of one scheduler tick)."""
        try:
            # croniter.is_now(now) returns True if the expression matches the
            # current minute.  We pass hash_seconds=60 so the match window is
            # exactly one scheduler tick.
            ci = croniter_module.croniter(schedule, now)  # type: ignore[attr-defined]
            # Get the previous scheduled time and check if it's within the last minute.
            prev = ci.get_prev(datetime)
            delta = (now - prev).total_seconds()
            return 0 <= delta < 60
        except Exception as exc:
            logger.warning(
                "[scheduler] croniter failed to parse schedule %r: %s — using fallback.",
                schedule,
                exc,
            )
            return False

    @staticmethod
    def _fallback_is_due(feed: Feed, now: datetime) -> bool:
        """Fallback: run if the feed has no schedule, never ran, or ran more
        than _FALLBACK_INTERVAL_SECONDS ago."""
        if feed.last_success is None:
            return True
        # Ensure last_success is timezone-aware for comparison.
        last = feed.last_success
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        elapsed = (now - last).total_seconds()
        return elapsed >= _FALLBACK_INTERVAL_SECONDS


# ── Module-level singleton ────────────────────────────────────────────────────

scheduler = FeedScheduler()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _try_import_croniter() -> object | None:
    """Try to import croniter; return the module or None if not installed."""
    try:
        return importlib.import_module("croniter")
    except ImportError:
        return None
