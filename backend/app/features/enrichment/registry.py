"""EnrichmentProviderRegistry — maps provider names to provider classes.

Registration is done via a class decorator:

    @enrichment_registry.register
    class MyProvider(BaseEnrichmentProvider):
        provider_name = "my_provider"
        supported_indicator_types = ["ipv4", "domain"]

Auto-discovery imports every module inside app.features.enrichment.providers.
"""

from __future__ import annotations

import importlib
import pkgutil
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.features.enrichment.provider_base import BaseEnrichmentProvider


class _EnrichmentProviderRegistry:
    """Singleton registry mapping provider_name → provider class."""

    def __init__(self) -> None:
        self._map: dict[str, type[BaseEnrichmentProvider]] = {}

    def register(self, cls: type[BaseEnrichmentProvider]) -> type[BaseEnrichmentProvider]:
        """Class decorator that registers a BaseEnrichmentProvider subclass."""
        name = getattr(cls, "provider_name", None)
        if not name:
            raise ValueError(
                f"{cls.__name__} must declare a non-empty `provider_name` class attribute."
            )
        if name in self._map:
            raise ValueError(
                f"provider_name {name!r} is already registered by {self._map[name].__name__}."
            )
        
        supported = getattr(cls, "supported_indicator_types", None)
        if supported is None or not isinstance(supported, list):
            raise ValueError(
                f"{cls.__name__} must declare a list of `supported_indicator_types`."
            )

        self._map[name] = cls
        return cls

    def get_all(self) -> list[type[BaseEnrichmentProvider]]:
        """Return all registered provider classes."""
        return list(self._map.values())
        
    def get(self, provider_name: str) -> type[BaseEnrichmentProvider] | None:
        """Return a specific provider class by name."""
        return self._map.get(provider_name)

    def autodiscover(self) -> None:
        """Import every module inside app.features.enrichment.providers."""
        import app.features.enrichment.providers as providers_pkg  # noqa: PLC0415

        for module_info in pkgutil.iter_modules(providers_pkg.__path__):
            importlib.import_module(
                f"app.features.enrichment.providers.{module_info.name}"
            )


# Module-level singleton
enrichment_registry = _EnrichmentProviderRegistry()
