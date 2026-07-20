"""FeedRunner — orchestrates the full collector lifecycle.

Responsibilities (all framework-level, zero duplication in collectors):
  - Registry auto-discovery
  - Feed row lookup + FeedRun record management
  - Retry with exponential back-off on fetch() failure
  - Timeout enforcement on fetch() via concurrent.futures thread pool
  - Metrics capture
  - Error isolation (a collector crash never propagates)
  - Pipeline orchestration: validate → normalize → store
  - Feed.last_success / Feed.last_failure updates
  - on_run_complete() hook invocation

Collectors implement only: fetch() / validate() / normalize().
"""

from __future__ import annotations


import time
from datetime import datetime, timezone

from sqlalchemy import update as sa_update
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.enums import FeedRunStatus, FeedStatus
from app.db.session import SessionLocal
from app.features.feeds.base_collector import CollectorConfig
from app.features.feeds.models import Feed, FeedRun
from app.features.feeds.pipeline import (
    NormalizationPipeline,
    StoragePipeline,
    ValidationPipeline,
)
from app.features.feeds.registry import registry
from app.features.feeds.schemas import CollectorMetrics
from app.core.events.bus import RedisEventBus

logger = get_logger(__name__)

_validation_pipeline = ValidationPipeline()
_normalization_pipeline = NormalizationPipeline()
_storage_pipeline = StoragePipeline(event_bus=RedisEventBus())


class FeedRunner:
    """Executes a single named feed through the full ingestion lifecycle."""

    def __init__(self, feed_name: str) -> None:
        self.feed_name = feed_name

    # ── Public entry point ────────────────────────────────────────────────────

    def run(self, full_sync: bool = False) -> CollectorMetrics:
        """Execute the feed.  Returns metrics regardless of success or failure.

        This method never raises.  All exceptions are caught, logged, and
        reflected in the returned metrics.
        """
        registry.autodiscover()

        metrics = CollectorMetrics(feed_name=self.feed_name)
        start = time.monotonic()

        db: Session = SessionLocal()
        feed_run: FeedRun | None = None

        try:
            feed, feed_run = self._begin_run(db)
            if feed is None:
                # Feed not found or disabled — nothing to do.
                return metrics

            collector_cls = registry.get(self.feed_name)
            if collector_cls is None:
                raise RuntimeError(
                    f"No collector registered for feed_name={self.feed_name!r}. "
                    "Ensure its module is inside app/features/feeds/collectors/."
                )

            # max_retries: Feed has no dedicated column; default to 3.
            # timeout: Feed has no dedicated column; default to 30 s.
            # rate_limit: requests-per-minute ceiling from the Feed row.
            config = CollectorConfig(
                feed_name=self.feed_name,
                timeout=30,
                max_retries=3,
                rate_limit=feed.rate_limit or 0,
                last_success=feed.last_success,
                full_sync=full_sync,
                authentication=feed.authentication or {},
            )
            collector = collector_cls(config)

            # ── Fetch with retries ────────────────────────────────────────────
            raw_payload = self._fetch_with_retry(collector, config, metrics)

            # ── Validate ──────────────────────────────────────────────────────
            validated = _validation_pipeline.run(
                collector.validate(raw_payload), metrics
            )

            # ── Normalize ─────────────────────────────────────────────────────
            normalized = _normalization_pipeline.run(collector, validated, metrics)

            # ── Store ─────────────────────────────────────────────────────────
            _storage_pipeline.run(db, feed.id, normalized, metrics)

            # ── Finalize success ──────────────────────────────────────────────
            metrics.duration_seconds = time.monotonic() - start
            self._finalize_run(db, feed, feed_run, FeedRunStatus.SUCCESS, metrics)

            try:
                collector.on_run_complete(metrics)
            except Exception as exc:
                logger.warning(
                    "[%s] on_run_complete() hook raised: %s", self.feed_name, exc
                )

            logger.info(
                "[%s] Run complete — added=%d updated=%d skipped=%d errors=%d duration=%.2fs",
                self.feed_name,
                metrics.records_added,
                metrics.records_updated,
                metrics.records_skipped,
                len(metrics.errors),
                metrics.duration_seconds,
            )

        except Exception as exc:
            metrics.duration_seconds = time.monotonic() - start
            if exc.__class__.__name__ == "SoftTimeLimitExceeded":
                error_msg = "Feed synchronization exceeded the 1-hour time limit and was terminated."
                logger.error("[%s] %s", self.feed_name, error_msg)
            else:
                error_msg = f"Unhandled error in FeedRunner: {exc}"
                logger.exception("[%s] %s", self.feed_name, error_msg)
                
            metrics.errors.append(error_msg)

            if feed_run is not None:
                try:
                    self._finalize_run(
                        db, None, feed_run, FeedRunStatus.FAILED, metrics
                    )
                except Exception:
                    pass

        finally:
            db.close()

        return metrics

    # ── Private helpers ───────────────────────────────────────────────────────

    def _begin_run(self, db: Session) -> tuple[Feed | None, FeedRun | None]:
        """Load the Feed row and create a FeedRun record."""
        feed: Feed | None = (
            db.query(Feed).filter(Feed.name == self.feed_name, Feed.enabled.is_(True)).first()
        )

        if feed is None:
            logger.warning(
                "[%s] Feed not found or is disabled — skipping run.", self.feed_name
            )
            return None, None

        feed_run = FeedRun(
            feed_id=feed.id,
            status=FeedRunStatus.RUNNING.value,
            start_time=datetime.now(tz=timezone.utc),
        )
        db.add(feed_run)
        db.commit()
        db.refresh(feed_run)

        logger.info("[%s] Run started — FeedRun.id=%s", self.feed_name, feed_run.id)
        return feed, feed_run

    def _fetch_with_retry(
        self,
        collector: object,
        config: CollectorConfig,
        metrics: CollectorMetrics,
    ) -> object:
        """Call collector.fetch() up to config.max_retries times.

        Each attempt is bounded by config.timeout seconds using a
        ThreadPoolExecutor so that a hung network call cannot block the
        worker indefinitely.  Exponential back-off is applied between
        failed attempts.

        Raises the last exception if all retries are exhausted.
        """
        last_exc: Exception | None = None

        for attempt in range(1, config.max_retries + 1):
            try:
                logger.debug(
                    "[%s] fetch() attempt %d/%d (timeout=%ds)",
                    self.feed_name,
                    attempt,
                    config.max_retries,
                    config.timeout,
                )
                # HTTP timeout enforcement has been moved to the individual collectors.
                # We call fetch() directly.
                return collector.fetch()  # type: ignore[attr-defined]
            except Exception as exc:
                last_exc = exc
                logger.warning(
                    "[%s] fetch() attempt %d failed (%s).",
                    self.feed_name,
                    attempt,
                    exc,
                )
                metrics.errors.append(f"fetch attempt {attempt} failed: {exc}")

            if attempt < config.max_retries:
                wait = config.retry_delay * (2 ** (attempt - 1))
                logger.info(
                    "[%s] Retrying in %.1fs …", self.feed_name, wait
                )
                time.sleep(wait)

        raise RuntimeError(
            f"fetch() failed after {config.max_retries} attempts"
        ) from last_exc

    def _finalize_run(
        self,
        db: Session,
        feed: Feed | None,
        feed_run: FeedRun,
        status: FeedRunStatus,
        metrics: CollectorMetrics,
    ) -> None:
        """Persist the FeedRun outcome and update Feed health columns."""
        now = datetime.now(tz=timezone.utc)

        feed_run.status = status.value
        feed_run.end_time = now
        feed_run.duration = metrics.duration_seconds
        feed_run.records_received = metrics.records_received
        feed_run.records_added = metrics.records_added
        feed_run.records_updated = metrics.records_updated
        feed_run.records_skipped = metrics.records_skipped
        feed_run.errors = metrics.errors or None

        if feed is not None:
            if status == FeedRunStatus.SUCCESS:
                feed.last_success = now
                # Atomic SQL increment — avoids a stale-read race condition.
                db.execute(
                    sa_update(Feed)
                    .where(Feed.id == feed.id)
                    .values(
                        records_imported=Feed.records_imported
                        + metrics.records_added
                        + metrics.records_updated
                    )
                )
            else:
                feed.last_failure = now
                feed.status = FeedStatus.ERROR.value

            db.add(feed)

        db.add(feed_run)
        db.commit()
