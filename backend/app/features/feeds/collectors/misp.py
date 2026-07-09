"""MispCollector — production collector for MISP instances."""

import json
import logging
import ssl
import urllib.request
import urllib.error
import urllib.parse
from typing import Any
from datetime import datetime, timezone

from app.features.feeds.base_collector import BaseCollector, CollectorConfig
from app.features.feeds.registry import registry
from app.features.feeds.schemas import RawIndicator
from app.db.enums import IndicatorType, Severity

logger = logging.getLogger(__name__)

# DO NOT hardcode supported MISP types.
# Use TYPE_MAPPING so adding new MISP attribute types later requires only updating one mapping.
TYPE_MAPPING: dict[str, IndicatorType] = {
    "ip-src": IndicatorType.IPV4,
    "ip-dst": IndicatorType.IPV4,
    "domain": IndicatorType.DOMAIN,
    "url": IndicatorType.URL,
    "md5": IndicatorType.MD5,
    "sha1": IndicatorType.SHA1,
    "sha256": IndicatorType.SHA256,
}

@registry.register
class MispCollector(BaseCollector):
    """Fetches incremental attributes from a MISP instance."""

    feed_name = "misp"

    def fetch(self) -> list[dict[str, Any]]:
        """POST to the MISP API and return the parsed JSON attributes."""
        # Store both base_url and api_key inside the feed authentication/configuration.
        base_url = self.config.authentication.get("base_url", "").rstrip("/")
        api_key = self.config.authentication.get("api_key", "")

        if not base_url or not api_key:
            raise RuntimeError(
                f"[{self.feed_name}] requires 'base_url' and 'api_key' in authentication config."
            )

        endpoint = f"{base_url}/attributes/restSearch"

        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": api_key,
            "User-Agent": "ThreatIntelPlatform/1.0",
        }

        # Handle MISP pagination.
        limit = 1000
        page = 1
        all_attributes: list[dict[str, Any]] = []

        while True:
            payload_dict: dict[str, Any] = {
                "returnFormat": "json",
                "limit": limit,
                "page": page,
                "type": list(TYPE_MAPPING.keys()),
            }
            
            # Incremental polling (default to 7 days if not specified in config)
            timestamp_filter = self.config.authentication.get("timestamp", "7d")
            if timestamp_filter:
                payload_dict["timestamp"] = timestamp_filter

            payload = json.dumps(payload_dict).encode("utf-8")

            logger.info(
                "[%s] Requesting MISP attributes (page=%d, limit=%d) from %s",
                self.feed_name,
                page,
                limit,
                endpoint,
            )

            req = urllib.request.Request(
                url=endpoint,
                data=payload,
                headers=headers,
                method="POST",
            )

            # Safely disable SSL verification ONLY for local development hosts
            context = None
            parsed_url = urllib.parse.urlparse(base_url)
            if parsed_url.hostname in ("localhost", "127.0.0.1", "host.docker.internal"):
                context = ssl._create_unverified_context()

            try:
                with urllib.request.urlopen(req, context=context) as resp:
                    body = resp.read().decode("utf-8")
            except urllib.error.HTTPError as exc:
                raise RuntimeError(
                    f"MISP API returned HTTP {exc.code}: {exc.reason}"
                ) from exc
            except urllib.error.URLError as exc:
                raise RuntimeError(
                    f"MISP API network error: {exc.reason}"
                ) from exc

            try:
                data = json.loads(body)
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    f"MISP API returned non-JSON response: {body[:200]!r}"
                ) from exc

            # MISP /attributes/restSearch can return {"response": {"Attribute": [...]}}
            # or a direct array depending on the instance version and returnFormat.
            response_data = data.get("response", data)
            if isinstance(response_data, dict):
                attributes = response_data.get("Attribute", [])
            else:
                attributes = response_data if isinstance(response_data, list) else []

            if not attributes:
                break

            all_attributes.extend(attributes)

            # If the number of returned attributes is less than our limit, we have reached the last page.
            if len(attributes) < limit:
                break

            page += 1

        logger.info(
            "[%s] MISP API responded: fetched %d total attributes",
            self.feed_name,
            len(all_attributes),
        )
        return all_attributes

    def validate(self, raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Filter the raw API response down to actionable, supported MISP attributes."""
        valid: list[dict[str, Any]] = []
        skipped = 0

        for record in raw:
            if not isinstance(record, dict):
                skipped += 1
                continue

            attr_type = record.get("type")
            value = (record.get("value") or "").strip()

            if not value:
                skipped += 1
                logger.debug(
                    "[%s] Dropped record with empty value (id=%s)",
                    self.feed_name,
                    record.get("id"),
                )
                continue

            if attr_type not in TYPE_MAPPING:
                skipped += 1
                logger.debug(
                    "[%s] Dropped unsupported type=%r (id=%s)",
                    self.feed_name,
                    attr_type,
                    record.get("id"),
                )
                continue

            valid.append(record)

        if skipped > 0:
            logger.debug("[%s] validate() skipped %d invalid records", self.feed_name, skipped)

        return valid

    def normalize(self, records: list[dict[str, Any]]) -> list[RawIndicator]:
        """Convert validated MISP attributes into platform RawIndicator objects."""
        normalized: list[RawIndicator] = []

        for record in records:
            attr_type = record.get("type")
            value = record.get("value", "").strip()
            timestamp_str = record.get("timestamp")

            indicator_type = TYPE_MAPPING[str(attr_type)]
            
            tags: list[str] = []
            
            # Preserve the originating MISP Event ID as optional metadata for future provenance
            event_id = record.get("event_id")
            if event_id:
                tags.append(f"misp_event_id:{event_id}")

            category = record.get("category")
            if category:
                tags.append(f"misp_category:{category}")

            last_seen = datetime.now(tz=timezone.utc)
            if timestamp_str:
                try:
                    # MISP timestamp is typical Unix epoch string
                    last_seen = datetime.fromtimestamp(int(timestamp_str), tz=timezone.utc)
                except (ValueError, TypeError):
                    logger.debug("[%s] Invalid timestamp %r", self.feed_name, timestamp_str)

            indicator = RawIndicator(
                type=indicator_type,
                value=value,
                normalized_value=value,
                confidence=50,  # Default confidence
                severity=Severity.MEDIUM,
                last_seen=last_seen,
                tags=tags if tags else None,
                raw=record  # Raw source payload preserved for auditing
            )
            normalized.append(indicator)

        return normalized
