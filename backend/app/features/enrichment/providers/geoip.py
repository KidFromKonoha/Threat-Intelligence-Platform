from typing import Any
from app.features.enrichment.provider_base import BaseEnrichmentProvider, EnrichmentResultData
from app.features.enrichment.registry import enrichment_registry
from app.features.indicators.models import Indicator
from app.db.enums import IndicatorType

_MOCK_GEO_DB = {
    "198.51.100.42": {
        "country_iso": "US",
        "city": "Testville",
        "asn": "AS64512",
        "org": "Example Corp",
        "latitude": 37.7749,
        "longitude": -122.4194,
    },
    "203.0.113.1": {
        "country_iso": "GB",
        "city": "London",
        "asn": "AS64513",
        "org": "BritTest Ltd",
        "latitude": 51.5074,
        "longitude": -0.1278,
    }
}

@enrichment_registry.register
class StaticGeoIPProvider(BaseEnrichmentProvider):
    """Deterministic local GeoIP provider using an embedded lookup table."""
    provider_name = "geoip"
    provider_version = "1.0.0"
    supported_indicator_types = [IndicatorType.IPV4, IndicatorType.IPV6]

    def enrich(self, indicator: Indicator) -> EnrichmentResultData:
        # Simulate local DB lookup
        raw_data = _MOCK_GEO_DB.get(indicator.value, {
            "country_iso": "XX",
            "city": "Unknown",
            "asn": "Unknown",
            "org": "Unknown",
            "latitude": 0.0,
            "longitude": 0.0,
        })
        
        # Build raw response as if returned by a MaxMind API or similar DB query
        raw_response = {
            "ip": indicator.value,
            "geo": raw_data,
            "source": "static_mock_db"
        }
        
        # Extract the attributes we care most about for the dashboard/UI
        extracted_attributes = {
            "country": raw_data["country_iso"],
            "asn": raw_data["asn"]
        }
        
        return EnrichmentResultData(
            raw_response=raw_response,
            extracted_attributes=extracted_attributes
        )
