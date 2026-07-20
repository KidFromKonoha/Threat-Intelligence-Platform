"""Watchlist Engine.

Evaluates indicators against watchlist rules and generates alerts.
"""

from __future__ import annotations

from typing import Any
import json
import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert

from app.features.watchlists.models import Watchlist, WatchlistRule, WatchlistAlert
from app.features.watchlists.schemas import RuleOperator
from app.features.indicators.models import Indicator
from app.core.events.bus import RedisEventBus

logger = logging.getLogger(__name__)


class RuleEvaluator:
    """Evaluates a WatchlistRule against an Indicator."""

    @staticmethod
    def evaluate(rule: WatchlistRule, indicator: Indicator) -> bool:
        # Resolve target value from indicator based on rule_type
        target_value = RuleEvaluator._get_target_value(rule.rule_type, indicator)
        if target_value is None:
            return False

        # Compare using operator
        try:
            return RuleEvaluator._compare(rule.operator, target_value, rule.value)
        except Exception as e:
            logger.error(f"Rule evaluation error: {e}")
            return False

    @staticmethod
    def _get_target_value(rule_type: str, indicator: Indicator) -> Any:
        if rule_type == "risk_score":
            return indicator.risk_score
        elif rule_type == "indicator_type":
            return indicator.type
        elif rule_type == "threat_actor":
            return [ta.name for ta in indicator.threat_actors]
        elif rule_type == "campaign":
            return [c.name for c in indicator.campaigns]
        elif rule_type == "malware":
            return [m.name for m in indicator.malware]
        elif rule_type == "mitre_technique":
            return [t.name for t in indicator.techniques]
        elif rule_type == "tag":
            return indicator.tags or []
        elif rule_type == "asn":
            # Just an example of how you could extract from tags/attributes
            return indicator.attributes.get("asn") if indicator.attributes else None
        else:
            return None

    @staticmethod
    def _compare(operator: str, target: Any, value: Any) -> bool:
        # If target is a list (like threat_actors), we check if ANY item matches the condition
        if isinstance(target, list):
            if operator == RuleOperator.IN:
                # E.g. "any threat actor IN ['APT29', 'APT28']"
                if not isinstance(value, list):
                    value = [value]
                return any(t in value for t in target)
            elif operator == RuleOperator.CONTAINS:
                # E.g. "any threat actor CONTAINS 'APT'"
                return any(str(value).lower() in str(t).lower() for t in target)
            else:
                # For EQ, NE, etc. applied to lists, we assume 'any item matches'
                if operator == RuleOperator.EQ:
                    return any(t == value for t in target)
                elif operator == RuleOperator.NE:
                    return all(t != value for t in target)
                return False

        # For scalar targets (e.g. risk_score)
        if operator == RuleOperator.EQ:
            return target == value
        elif operator == RuleOperator.NE:
            return target != value
        elif operator == RuleOperator.GT:
            return float(target) > float(value)
        elif operator == RuleOperator.GTE:
            return float(target) >= float(value)
        elif operator == RuleOperator.LT:
            return float(target) < float(value)
        elif operator == RuleOperator.LTE:
            return float(target) <= float(value)
        elif operator == RuleOperator.IN:
            if not isinstance(value, list):
                value = [value]
            return target in value
        elif operator == RuleOperator.CONTAINS:
            return str(value).lower() in str(target).lower()

        return False


class AlertGenerator:
    """Generates alerts using ON CONFLICT DO UPDATE."""

    @staticmethod
    def generate_alerts(db: Session, indicator: Indicator, matches: list[tuple[Watchlist, WatchlistRule]]) -> int:
        if not matches:
            return 0

        bus = RedisEventBus()
        alerts_created_or_updated = 0

        for watchlist, rule in matches:
            # Prepare values for upsert
            rule_json = json.dumps({
                "rule_type": rule.rule_type,
                "operator": rule.operator,
                "value": rule.value
            })
            matched_val = str(RuleEvaluator._get_target_value(rule.rule_type, indicator))

            stmt = insert(WatchlistAlert).values(
                watchlist_id=watchlist.id,
                indicator_id=indicator.id,
                severity="high" if (indicator.risk_score or 0) > 80 else "medium",
                status="NEW",
                risk_score_snapshot=indicator.risk_score,
                matched_rule=rule_json,
                matched_value=matched_val,
                created_at=func.now(),
                updated_at=func.now()
            )

            # ON CONFLICT DO UPDATE
            # Updates the snapshot and timestamp if it fires again
            stmt = stmt.on_conflict_do_update(
                index_elements=["watchlist_id", "indicator_id"],
                set_={
                    "risk_score_snapshot": stmt.excluded.risk_score_snapshot,
                    "matched_rule": stmt.excluded.matched_rule,
                    "matched_value": stmt.excluded.matched_value,
                    "updated_at": func.now()
                }
            ).returning(WatchlistAlert.id)

            result = db.execute(stmt)
            alert_id = result.scalar()
            alerts_created_or_updated += 1
            
            # Emit WatchlistAlertCreated event
            from app.core.events.schema import EventEnvelope
            bus.publish(
                "tip.events.watchlist.alert_created",
                EventEnvelope(
                    topic="tip.events.watchlist.alert_created",
                    producer="watchlist_engine",
                    payload={
                        "alert_id": alert_id,
                        "watchlist_id": watchlist.id,
                        "indicator_id": indicator.id,
                        "risk_score": indicator.risk_score,
                        "rule": rule_json
                    }
                )
            )

        db.commit()
        return alerts_created_or_updated


class WatchlistEngineService:
    @staticmethod
    def evaluate_indicator(db: Session, indicator: Indicator) -> int:
        """Evaluates an indicator against all enabled watchlists."""
        
        from sqlalchemy.orm import selectinload
        watchlists = db.query(Watchlist).options(selectinload(Watchlist.rules)).filter(Watchlist.enabled == True).all()
        if not watchlists:
            return 0

        matches = []
        for w in watchlists:
            # A watchlist matches if ANY of its rules match (OR logic)
            # You could implement AND logic, but we'll default to OR for simplicity
            for rule in w.rules:
                if RuleEvaluator.evaluate(rule, indicator):
                    matches.append((w, rule))
                    break # Stop evaluating rules for this watchlist once one matches

        if matches:
            return AlertGenerator.generate_alerts(db, indicator, matches)
            
        return 0
