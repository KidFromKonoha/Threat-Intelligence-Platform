"""DummyCollector — an example feed collector for framework validation.

This collector generates synthetic threat indicators without making any
external network calls.  It serves two purposes:

1. Proves that the framework (registry → runner → pipelines) works end-to-end.
2. Documents the minimum implementation contract for real collectors.

To run it manually inside the backend container:
    python -c "
    from app.features.feeds.runner import FeedRunner
    m = FeedRunner('dummy').run()
    print(m)
    "

To trigger via Celery:
    from app.features.feeds.tasks import run_collector
    run_collector.delay('dummy')

The corresponding Feed row must exist in the database first:
    INSERT INTO feeds (id, name, type, enabled, status)
    VALUES (gen_random_uuid()::text, 'dummy', 'open_source', true, 'active');
"""

from __future__ import annotations

import random
from datetime import datetime, timezone
from typing import Any

from app.db.enums import IndicatorType, Severity
from app.features.feeds.base_collector import BaseCollector, CollectorConfig
from app.features.feeds.registry import registry
from app.features.feeds.schemas import RawIndicator


# Synthetic data pools — deterministic enough for consistent testing.
_FAKE_IPS = [
    "192.0.2.1",
    "192.0.2.42",
    "198.51.100.7",
    "203.0.113.99",
    "10.0.0.1",
]
_FAKE_DOMAINS = [
    "malicious-example.com",
    "badactor-c2.net",
    "phishing-target.org",
    "exploit-kit.ru",
    "dropper-domain.io",
]
_FAKE_HASHES = [
    "d41d8cd98f00b204e9800998ecf8427e",
    "da39a3ee5e6b4b0d3255bfef95601890afd80709",
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
]


@registry.register
class DummyCollector(BaseCollector):
    """Generates synthetic indicators for framework smoke-testing.

    fetch()     → returns a list of raw dicts (simulating a real API response).
    validate()  → drops records missing required keys.
    normalize() → converts raw dicts into RawIndicator objects.
    """

    feed_name = "dummy"

    def fetch(self) -> list[dict[str, Any]]:
        """Produce a small batch of synthetic raw records."""
        now_iso = datetime.now(tz=timezone.utc).isoformat()
        records: list[dict[str, Any]] = []

        for ip in _FAKE_IPS:
            records.append(
                {
                    "ioc_type": "ipv4",
                    "ioc_value": ip,
                    "confidence": random.randint(50, 95),
                    "severity": random.choice(["low", "medium", "high"]),
                    "first_seen": now_iso,
                    "last_seen": now_iso,
                    "tags": ["synthetic", "dummy"],
                }
            )

        for domain in _FAKE_DOMAINS:
            records.append(
                {
                    "ioc_type": "domain",
                    "ioc_value": domain,
                    "confidence": random.randint(40, 90),
                    "severity": random.choice(["medium", "high", "critical"]),
                    "first_seen": now_iso,
                    "last_seen": now_iso,
                    "tags": ["synthetic", "dummy", "phishing"],
                }
            )

        for h in _FAKE_HASHES:
            ioc_type = "md5" if len(h) == 32 else ("sha1" if len(h) == 40 else "sha256")
            records.append(
                {
                    "ioc_type": ioc_type,
                    "ioc_value": h,
                    "confidence": random.randint(70, 100),
                    "severity": "high",
                    "first_seen": now_iso,
                    "last_seen": now_iso,
                    "tags": ["synthetic", "dummy", "malware"],
                }
            )

        # Include one deliberately invalid record to exercise validation.
        records.append(None)  # type: ignore[arg-type]

        return records

    def validate(self, raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Drop records missing required keys."""
        valid: list[dict[str, Any]] = []
        for record in raw:
            if not isinstance(record, dict):
                continue
            if not record.get("ioc_type") or not record.get("ioc_value"):
                continue
            valid.append(record)
        return valid

    def normalize(self, records: list[dict[str, Any]]) -> list[RawIndicator]:
        """Convert validated raw dicts into RawIndicator objects."""
        normalized: list[RawIndicator] = []

        _type_map: dict[str, IndicatorType] = {
            "ipv4": IndicatorType.IPV4,
            "ipv6": IndicatorType.IPV6,
            "domain": IndicatorType.DOMAIN,
            "url": IndicatorType.URL,
            "md5": IndicatorType.MD5,
            "sha1": IndicatorType.SHA1,
            "sha256": IndicatorType.SHA256,
        }
        _severity_map: dict[str, Severity] = {
            "info": Severity.INFO,
            "low": Severity.LOW,
            "medium": Severity.MEDIUM,
            "high": Severity.HIGH,
            "critical": Severity.CRITICAL,
        }

        for record in records:
            indicator_type = _type_map.get(record["ioc_type"])
            if indicator_type is None:
                continue  # Unknown type — skip silently.

            severity = _severity_map.get(record.get("severity", "medium"), Severity.MEDIUM)

            normalized.append(
                RawIndicator(
                    type=indicator_type,
                    value=record["ioc_value"],
                    normalized_value=record["ioc_value"].strip().lower(),
                    confidence=int(record.get("confidence", 50)),
                    severity=severity,
                    risk_score=0,
                    tags=record.get("tags"),
                    first_seen=datetime.fromisoformat(record["first_seen"]),
                    last_seen=datetime.fromisoformat(record["last_seen"]),
                    raw=record,
                )
            )

        return normalized
