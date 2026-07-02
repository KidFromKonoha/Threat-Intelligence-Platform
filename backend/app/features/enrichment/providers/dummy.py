"""Dummy enrichment provider for testing the framework."""

from __future__ import annotations

import time

from app.db.enums import IndicatorType
from app.features.enrichment.provider_base import BaseEnrichmentProvider, EnrichmentResultData
from app.features.enrichment.registry import enrichment_registry
from app.features.indicators.models import Indicator


@enrichment_registry.register
class DummyEnrichmentProvider(BaseEnrichmentProvider):
    """A dummy provider that returns deterministic data for all indicator types."""

    provider_name = "dummy_enrichment"
    # Support all types to make testing easy
    supported_indicator_types = [t.value for t in IndicatorType]

    def enrich(self, indicator: Indicator) -> EnrichmentResultData:
        """Simulate an external API call and return deterministic data."""
        
        # Simulate network latency (0.5s)
        time.sleep(0.5)
        
        # Deterministic dummy data based on indicator ID
        score = sum(ord(c) for c in indicator.id) % 100
        
        raw_response = {
            "dummy_api_version": "1.0.0",
            "queried_value": indicator.value,
            "queried_type": indicator.type,
            "internal_score": score,
            "tags": ["dummy", "test_framework"],
            "metadata": {
                "generated_at": time.time(),
                "node": "dummy-server-01"
            }
        }
        
        extracted_attributes = {
            "reputation_score": score,
            "provider_tags": ["dummy", "test_framework"]
        }
        
        # Add a mock country if it's an IP
        if indicator.type in (IndicatorType.IPV4.value, IndicatorType.IPV6.value):
            extracted_attributes["country_code"] = "CH"
            raw_response["geo"] = {"country": "CH", "city": "Zurich"}
            
        return EnrichmentResultData(
            raw_response=raw_response,
            extracted_attributes=extracted_attributes
        )
