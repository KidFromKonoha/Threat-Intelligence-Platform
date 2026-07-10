"""ThreatFoxCollector — production collector for the ThreatFox API.

ThreatFox (https://threatfox.abuse.ch) is a community-driven threat
intelligence platform operated by abuse.ch.  It publishes indicators of
compromise (IOCs) covering malware C2 infrastructure, payload delivery URLs,
and file hashes, all associated with known malware families.

API reference: https://threatfox.abuse.ch/api/

────────────────────────────────────────────────────────────────────────────
Collector responsibilities (ONLY what differs from the framework):
  - Build the POST request to the ThreatFox API.
  - Parse and return the raw JSON response body.
  - Validate individual IOC records (field presence, type support).
  - Map ThreatFox fields → platform's RawIndicator schema.

Framework responsibilities (NOT duplicated here):
  - Retrying full execution on catastrophic failure
  - Celery hard/soft execution bounds
  - ValidationPipeline (None-record filtering)
  - StoragePipeline (upsert + dedup)
  - FeedRun DB record + metrics     (FeedRunner)
  - Logging of run start/end/errors (FeedRunner)

────────────────────────────────────────────────────────────────────────────
Database setup (run once):

    INSERT INTO feeds (name, description, type, enabled, status, schedule, authentication)
    VALUES (
        'threatfox',
        'ThreatFox IOC feed by abuse.ch',
        'open_source',
        true,
        'active',
        '0 */6 * * *',
        '{"api_key": "YOUR_THREATFOX_API_KEY"}'::json
    );

The api_key is read from Feed.authentication at runtime.
If no api_key is configured, the collector falls back to the anonymous
endpoint (reduced rate limits apply).

────────────────────────────────────────────────────────────────────────────
Manual run (inside backend container):

    python -c "
    import app.db
    from app.features.feeds.runner import FeedRunner
    m = FeedRunner('threatfox').run()
    print(m)
    "
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

from app.db.enums import IndicatorType, Severity
from app.features.feeds.base_collector import BaseCollector
from app.features.feeds.registry import registry
from app.features.feeds.schemas import RawIndicator

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────

_API_URL = "https://threatfox-api.abuse.ch/api/v1/"

# Number of days of IOCs to request per run.  1 day is the right default for
# a feed that runs every 6 hours — it provides a small overlap buffer so no
# IOC is missed due to clock skew between the ThreatFox server and the
# scheduler.  Operators may override this via Feed.authentication["days"].
_DEFAULT_DAYS = 1

# ThreatFox ioc_type → platform IndicatorType.
# Types absent from this map are silently dropped in validate().
_IOC_TYPE_MAP: dict[str, IndicatorType] = {
    "url": IndicatorType.URL,
    "domain": IndicatorType.DOMAIN,
    "ip:port": IndicatorType.IPV4,   # value normalised to bare IP below
    "md5_hash": IndicatorType.MD5,
    "sha1_hash": IndicatorType.SHA1,
    "sha256_hash": IndicatorType.SHA256,
}

# ThreatFox threat_type → platform Severity.
# Botnet C2 / payload delivery are high-confidence active threats.
_THREAT_TYPE_SEVERITY: dict[str, Severity] = {
    "botnet_cc": Severity.HIGH,
    "payload_delivery": Severity.HIGH,
    "payload_url": Severity.HIGH,
    "dropper_url": Severity.MEDIUM,
    "malware_sample": Severity.MEDIUM,
}

# ThreatFox timestamp format: "2023-07-01 12:00:00 UTC"
_TS_FORMAT = "%Y-%m-%d %H:%M:%S UTC"


# ── Collector ─────────────────────────────────────────────────────────────────


@registry.register
class ThreatFoxCollector(BaseCollector):
    """Fetches recent IOCs from the ThreatFox community API.

    fetch()     → POSTs to the ThreatFox API and returns the raw response dict.
    validate()  → Drops records with missing/unsupported fields.
    normalize() → Converts validated records to RawIndicator objects.

    The framework (FeedRunner) handles storage, metrics, and execution limits.
    The collector enforces per-request timeouts.
    """

    feed_name = "threatfox"

    # ── fetch ──────────────────────────────────────────────────────────────────

    def fetch(self) -> dict[str, Any]:
        """POST to the ThreatFox API and return the parsed JSON response.

        This method enforces a per-request socket timeout using config.timeout.

        Returns:
            The full parsed API response dict:
            {
                "query_status": "ok",
                "data": [ {ioc record}, ... ]
            }

        Raises:
            RuntimeError: if the HTTP request fails or the API returns an
                          unexpected status.
        """
        api_key: str = self.config.authentication.get("api_key", "")
        days: int = int(self.config.authentication.get("days", _DEFAULT_DAYS))

        payload = json.dumps({"query": "get_iocs", "days": days}).encode()

        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "User-Agent": "ThreatIntelPlatform/1.0",
        }
        if api_key:
            headers["Auth-Key"] = api_key

        logger.info(
            "[%s] Requesting IOCs from ThreatFox API (days=%d, auth=%s)",
            self.feed_name,
            days,
            "yes" if api_key else "anonymous",
        )

        req = urllib.request.Request(
            url=_API_URL,
            data=payload,
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout) as resp:
                body = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            raise RuntimeError(
                f"ThreatFox API returned HTTP {exc.code}: {exc.reason}"
            ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"ThreatFox API network error: {exc.reason}"
            ) from exc

        try:
            data = json.loads(body)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"ThreatFox API returned non-JSON response: {body[:200]!r}"
            ) from exc

        query_status = data.get("query_status", "")
        if query_status not in ("ok", "no_results"):
            raise RuntimeError(
                f"ThreatFox API returned unexpected query_status={query_status!r}. "
                f"Full response: {body[:500]!r}"
            )

        ioc_count = len(data.get("data") or [])
        logger.info(
            "[%s] ThreatFox API responded: status=%s records=%d",
            self.feed_name,
            query_status,
            ioc_count,
        )
        return data

    # ── validate ───────────────────────────────────────────────────────────────

    def validate(self, raw: dict[str, Any]) -> list[dict[str, Any]]:
        """Filter the raw API response down to actionable, supported IOC records.

        Drops records that:
        - Are not dicts.
        - Are missing the ``ioc`` or ``ioc_type`` field.
        - Have an ``ioc_type`` not supported by the platform.
        - Have an empty/null IOC value.

        ``last_seen`` being null is allowed (many ThreatFox records have no
        re-observation timestamp; we default to ``first_seen`` during normalization).

        Returns:
            List of raw record dicts that passed all checks.
        """
        records: list[dict[str, Any]] = raw.get("data") or []
        valid: list[dict[str, Any]] = []
        skipped = 0

        for record in records:
            if not isinstance(record, dict):
                skipped += 1
                continue

            ioc_value = (record.get("ioc") or "").strip()
            ioc_type = (record.get("ioc_type") or "").strip().lower()

            if not ioc_value:
                skipped += 1
                logger.debug(
                    "[%s] Dropped record with empty ioc value (id=%s)",
                    self.feed_name,
                    record.get("id"),
                )
                continue

            if ioc_type not in _IOC_TYPE_MAP:
                skipped += 1
                logger.debug(
                    "[%s] Dropped unsupported ioc_type=%r (id=%s)",
                    self.feed_name,
                    ioc_type,
                    record.get("id"),
                )
                continue

            valid.append(record)

        if skipped:
            logger.info(
                "[%s] Validation: %d records passed, %d dropped (unsupported/malformed)",
                self.feed_name,
                len(valid),
                skipped,
            )

        return valid

    # ── normalize ──────────────────────────────────────────────────────────────

    def normalize(self, records: list[dict[str, Any]]) -> list[RawIndicator]:
        """Convert validated ThreatFox records into platform RawIndicator objects.

        Field mapping:
            ioc              → value  (normalised for dedup key)
            ioc_type         → type   (via _IOC_TYPE_MAP)
            confidence_level → confidence (int 0–100)
            threat_type      → severity   (via _THREAT_TYPE_SEVERITY)
            first_seen       → first_seen (UTC datetime)
            last_seen        → last_seen  (UTC datetime; fallback: first_seen)
            tags             → tags (list[str]; malware_printable appended)
            malware_printable → prepended to tags as "malware:<family>"

        ip:port normalisation:
            ThreatFox represents C2 servers as "1.2.3.4:4444".  The platform
            stores the bare IPv4 address and records the port in the raw payload
            for forensic use.  The port is NOT stripped from the ``value`` field
            because ``value`` is what analysts search; instead, ``normalized_value``
            (the dedup key) uses only the bare IP so that the same C2 IP appearing
            on different ports does not create duplicate indicators.

        Returns:
            List of RawIndicator objects ready for the StoragePipeline.
        """
        normalized: list[RawIndicator] = []

        for record in records:
            try:
                indicator = self._normalize_one(record)
                if indicator is not None:
                    normalized.append(indicator)
            except Exception as exc:
                logger.warning(
                    "[%s] Failed to normalize record id=%s: %s",
                    self.feed_name,
                    record.get("id"),
                    exc,
                )

        logger.info(
            "[%s] Normalization: %d/%d records converted to RawIndicator",
            self.feed_name,
            len(normalized),
            len(records),
        )
        return normalized

    # ── Private helpers ────────────────────────────────────────────────────────

    def _normalize_one(self, record: dict[str, Any]) -> RawIndicator | None:
        """Normalize a single validated ThreatFox record."""
        ioc_type_str = record["ioc_type"].strip().lower()
        indicator_type = _IOC_TYPE_MAP[ioc_type_str]

        raw_value: str = record["ioc"].strip()

        # ── Value + normalized_value ───────────────────────────────────────────
        # For ip:port (C2 servers), keep the full "ip:port" as the display
        # value so analysts see the port.  Use only the bare IP as the
        # normalized_value (dedup key) so that 1.2.3.4:80 and 1.2.3.4:443 do
        # not create two separate Indicator rows.
        if ioc_type_str == "ip:port" and ":" in raw_value:
            bare_ip = raw_value.split(":")[0]
            normalized_value = bare_ip.lower()
        else:
            normalized_value = raw_value.strip().lower()

        # ── Confidence ────────────────────────────────────────────────────────
        try:
            confidence = max(0, min(100, int(record.get("confidence_level") or 50)))
        except (TypeError, ValueError):
            confidence = 50

        # ── Severity ─────────────────────────────────────────────────────────
        threat_type = (record.get("threat_type") or "").lower()
        severity = _THREAT_TYPE_SEVERITY.get(threat_type, Severity.MEDIUM)

        # ── Timestamps ────────────────────────────────────────────────────────
        first_seen = _parse_timestamp(record.get("first_seen"))
        last_seen_raw = record.get("last_seen")
        last_seen = _parse_timestamp(last_seen_raw) if last_seen_raw else first_seen

        # ── Tags ─────────────────────────────────────────────────────────────
        tags: list[str] = ["threatfox"]

        malware_printable = record.get("malware_printable")
        if malware_printable:
            tags.append(f"malware:{malware_printable.lower()}")

        malware_id = record.get("malware")
        if malware_id:
            tags.append(f"malware_id:{malware_id.lower()}")

        threat_type_tag = record.get("threat_type")
        if threat_type_tag:
            tags.append(f"threat_type:{threat_type_tag.lower()}")

        api_tags: list[str] | None = record.get("tags")
        if isinstance(api_tags, list):
            for t in api_tags:
                if isinstance(t, str) and t:
                    tags.append(t.lower())

        # Deduplicate tags while preserving insertion order.
        seen: set[str] = set()
        deduped_tags: list[str] = []
        for t in tags:
            if t not in seen:
                seen.add(t)
                deduped_tags.append(t)

        return RawIndicator(
            type=indicator_type,
            value=raw_value,
            normalized_value=normalized_value,
            confidence=confidence,
            severity=severity,
            risk_score=0,   # Risk scoring is a future enrichment step.
            first_seen=first_seen,
            last_seen=last_seen,
            tags=deduped_tags,
            raw={
                "source": "threatfox",
                "id": record.get("id"),
                "ioc_type": record.get("ioc_type"),
                "threat_type": record.get("threat_type"),
                "threat_type_desc": record.get("threat_type_desc"),
                "malware": record.get("malware"),
                "malware_printable": record.get("malware_printable"),
                "malware_alias": record.get("malware_alias"),
                "malware_malpedia": record.get("malware_malpedia"),
                "confidence_level": record.get("confidence_level"),
                "reporter": record.get("reporter"),
            },
        )


# ── Module-level helpers ──────────────────────────────────────────────────────


def _parse_timestamp(value: str | None) -> datetime:
    """Parse a ThreatFox timestamp string into a UTC-aware datetime.

    ThreatFox format: "2023-07-01 12:00:00 UTC"

    Falls back to ``datetime.now(UTC)`` on any parse error so that a bad
    timestamp in one record never blocks the rest of the batch.
    """
    if not value:
        return datetime.now(tz=timezone.utc)
    try:
        return datetime.strptime(value, _TS_FORMAT).replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        logger.debug("Could not parse ThreatFox timestamp %r; using now()", value)
        return datetime.now(tz=timezone.utc)
