"""CollectorRegistry — maps feed names to collector classes.

Registration is done via a class decorator:

    @registry.register
    class MyCollector(BaseCollector):
        feed_name = "my_feed"

Auto-discovery imports every module inside app/features/feeds/collectors/
at startup, which triggers the decorators and populates the registry.

Design constraints:
- Registering a collector must not require editing any framework file.
- A feed_name collision raises immediately at import time, not at runtime.
"""

from __future__ import annotations

import importlib
import pkgutil
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.features.feeds.base_collector import BaseCollector


class _CollectorRegistry:
    """Singleton registry mapping feed_name → collector class."""

    def __init__(self) -> None:
        self._map: dict[str, type[BaseCollector]] = {}

    # ── Registration ──────────────────────────────────────────────────────────

    def register(self, cls: type[BaseCollector]) -> type[BaseCollector]:
        """Class decorator that registers a BaseCollector subclass.

        Usage:
            @registry.register
            class MyCollector(BaseCollector):
                feed_name = "my_feed"
        """
        name = getattr(cls, "feed_name", None)
        if not name:
            raise ValueError(
                f"{cls.__name__} must declare a non-empty `feed_name` class attribute."
            )
        if name in self._map:
            raise ValueError(
                f"feed_name {name!r} is already registered by {self._map[name].__name__}. "
                "Each collector must have a unique feed_name."
            )
        self._map[name] = cls
        return cls

    # ── Lookup ────────────────────────────────────────────────────────────────

    def get(self, feed_name: str) -> type[BaseCollector] | None:
        """Return the collector class for feed_name, or None if not found."""
        return self._map.get(feed_name)

    def all_names(self) -> list[str]:
        """Return all registered feed names."""
        return list(self._map.keys())

    # ── Auto-discovery ────────────────────────────────────────────────────────

    def autodiscover(self) -> None:
        """Import every module inside app.features.feeds.collectors.

        This triggers all @registry.register decorators so that the registry
        is fully populated before the runner executes any task.

        Called once at application startup or the first time a Celery worker
        picks up a task.
        """
        import app.features.feeds.collectors as collectors_pkg  # noqa: PLC0415

        for module_info in pkgutil.iter_modules(collectors_pkg.__path__):
            importlib.import_module(
                f"app.features.feeds.collectors.{module_info.name}"
            )


# Module-level singleton — import this everywhere.
registry = _CollectorRegistry()
