"""Abstract base class for enrichment providers.

Every enrichment provider must:
  1. Subclass BaseEnrichmentProvider.
  2. Define `provider_name`.
  3. Define `supported_indicator_types` (a list of IndicatorType enum strings).
  4. Implement `enrich()`.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Any

from app.features.indicators.models import Indicator


@dataclass
class EnrichmentResultData:
    """The structured result returned by an enrichment provider.

    Attributes:
        raw_response: The complete, unmodified payload from the external service.
                      Stored as JSON to allow future extraction.
        extracted_attributes: A dictionary of key/value pairs that the provider
                              deemed important enough to highlight.
    """

    raw_response: dict[str, Any]
    extracted_attributes: dict[str, Any]


class BaseEnrichmentProvider(abc.ABC):
    """Abstract base class for all enrichment providers."""

    provider_name: str
    supported_indicator_types: list[str]

    @abc.abstractmethod
    def enrich(self, indicator: Indicator) -> EnrichmentResultData:
        """Fetch enrichment data for the given indicator.

        Args:
            indicator: The indicator to enrich.

        Returns:
            An EnrichmentResultData containing both the raw payload and
            any extracted attributes.

        Raises:
            Exception: If the external service fails or times out. The
                       framework catches this and isolates the failure.
        """
