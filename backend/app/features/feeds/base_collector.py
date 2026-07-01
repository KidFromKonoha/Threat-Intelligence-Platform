"""Abstract BaseCollector and CollectorConfig.

Every feed collector must:
  1. Subclass BaseCollector.
  2. Set `feed_name` (must match the Feed.name in the database).
  3. Implement fetch(), validate(), and normalize().
     The store() step is handled by the framework pipeline — collectors
     never write to the database directly.

Adding a new feed = one new file in app/features/feeds/collectors/.
No other file needs to change.

SOLID alignment:
  - Single Responsibility: collectors only fetch + validate + normalize.
  - Open/Closed: new feeds extend BaseCollector without modifying the framework.
  - Liskov Substitution: any BaseCollector can be passed to FeedRunner.
  - Interface Segregation: fetch/validate/normalize are the only required methods.
  - Dependency Inversion: FeedRunner depends on BaseCollector, not concrete classes.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any

from app.features.feeds.schemas import RawIndicator


@dataclass
class CollectorConfig:
    """Runtime configuration for a collector.

    Populated by the registry from the Feed row in the database.
    Collectors receive this at instantiation and must treat it as read-only.
    """

    feed_name: str
    # Maximum seconds to wait for a single fetch call.
    timeout: int = 30
    # How many times to retry on transient failure before giving up.
    max_retries: int = 3
    # Base delay in seconds between retries (exponential back-off applied).
    retry_delay: float = 5.0
    # Requests per minute ceiling; 0 = unlimited.
    rate_limit: int = 0
    # Arbitrary key/value pairs from Feed.authentication.
    authentication: dict[str, Any] = field(default_factory=dict)


class BaseCollector(abc.ABC):
    """Abstract base for all feed collectors.

    Subclasses implement fetch(), validate(), and normalize().
    The framework (FeedRunner + pipelines) handles everything else:
    retries, timeouts, DB writes, metrics, and error isolation.
    """

    #: Every subclass MUST declare a unique feed_name.
    feed_name: str

    def __init__(self, config: CollectorConfig) -> None:
        self.config = config

    # ── Required interface ────────────────────────────────────────────────────

    @abc.abstractmethod
    def fetch(self) -> Any:
        """Retrieve raw data from the external source.

        Must respect self.config.timeout.
        Must raise an exception on unrecoverable failure.
        Must return any raw payload (list, dict, bytes, str …).
        """

    @abc.abstractmethod
    def validate(self, raw: Any) -> list[Any]:
        """Validate the raw payload returned by fetch().

        Returns a list of individual raw records that passed validation.
        Invalid records must be dropped here, not silently stored.
        """

    @abc.abstractmethod
    def normalize(self, records: list[Any]) -> list[RawIndicator]:
        """Convert validated raw records into RawIndicator objects.

        Must produce RawIndicator for every record.
        Must not write to the database.
        """

    # ── Optional hook (no-op by default) ─────────────────────────────────────

    def on_run_complete(self, metrics: "CollectorMetrics") -> None:  # type: ignore[name-defined]  # noqa: F821
        """Called by the runner after a successful or failed run.

        Override for feed-specific side effects (e.g. checkpointing a cursor).
        """
