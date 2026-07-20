import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.db.session import SessionLocal
from app.features.watchlists.service import WatchlistService, WatchlistAlertService
from app.features.watchlists.schemas import WatchlistCreate, WatchlistRuleCreate, RuleOperator
from app.features.indicators.models import Indicator
from app.core.events.bus import RedisEventBus

def main():
    db = SessionLocal()
    bus = RedisEventBus()

    # 1. Create a watchlist
    print("[1] Creating Watchlist: Risk Score >= 80...")
    watchlist = WatchlistService.create(db, WatchlistCreate(
        name="High Risk Indicators",
        description="Any indicator with risk score >= 80",
        rules=[
            WatchlistRuleCreate(
                rule_type="risk_score",
                operator=RuleOperator.GTE,
                value=80
            )
        ]
    ))
    print(f"Created Watchlist ID: {watchlist.id}")

    # Create dummy indicator
    indicator = db.query(Indicator).filter(Indicator.normalized_value == "malicious-watchlist-test.com").first()
    if not indicator:
        indicator = Indicator(
            type="domain",
            value="malicious-watchlist-test.com",
            normalized_value="malicious-watchlist-test.com",
            risk_score=95,
            confidence=90,
            severity="high"
        )
        db.add(indicator)
    else:
        indicator.risk_score = 95
        
    db.commit()
    db.refresh(indicator)

    # 2. Trigger event
    from app.core.events.schema import EventEnvelope
    
    # Direct Test
    from app.features.watchlists.engine import WatchlistEngineService, RuleEvaluator
    print("\n--- Direct Evaluation Test ---")
    w = WatchlistService.get_by_id(db, watchlist.id)
    print(f"Watchlist: {w.name}, Enabled: {w.enabled}")
    for r in w.rules:
        target = RuleEvaluator._get_target_value(r.rule_type, indicator)
        matched = RuleEvaluator._compare(r.operator, target, r.value)
        print(f"Rule: {r.rule_type} {r.operator} {r.value} -> Target: {target} -> Match: {matched}")
    
    alerts_gen = WatchlistEngineService.evaluate_indicator(db, indicator)
    print(f"Generated directly: {alerts_gen}")
    print("------------------------------\n")

    print(f"[2] Triggering RiskScoreCalculated event for Indicator ID {indicator.id}...")
    bus.publish(
        "tip.events.risk_score.calculated",
        EventEnvelope(
            topic="tip.events.risk_score.calculated",
            producer="verify_script",
            payload={
                "indicator_id": indicator.id,
                "risk_score": 95
            }
        )
    )
    
    print("Events published. The workers should pick them up.")
    print("Checking database for alerts... (Note: in a real async environment this might take a second)")
    
    import time
    time.sleep(2)
    
    # Check Alerts
    alerts = WatchlistAlertService.get_all(db, indicator_id=indicator.id)
    print(f"[2] Found {len(alerts)} alerts.")
    if alerts:
        alert = alerts[0]
        print(f"Alert ID: {alert.id}, Status: {alert.status}, Severity: {alert.severity}")
        
        # 3. Duplicate event test
        print("[3] Triggering duplicate event...")
        bus.publish(
            "tip.events.risk_score.calculated",
            EventEnvelope(
                topic="tip.events.risk_score.calculated",
                producer="verify_script",
                payload={
                    "indicator_id": indicator.id,
                    "risk_score": 98
                }
            )
        )
        time.sleep(2)
        
        # Ensure it updated, not duplicated
        alerts_after = WatchlistAlertService.get_all(db, indicator_id=indicator.id)
        print(f"[3] Found {len(alerts_after)} alerts after duplicate event.")
        
        # 4. Acknowledge Alert
        print("[4] Acknowledging Alert...")
        ack_alert = WatchlistAlertService.acknowledge(db, alert.id, user_id="system_test")
        print(f"[4] Alert status is now: {ack_alert.status} by {ack_alert.acknowledged_by}")

    # 5. Dashboard Metrics
    metrics = WatchlistAlertService.get_metrics(db)
    print(f"[5] Metrics: {metrics.model_dump()}")
    
    # 9. Prometheus metrics - can test via curl http://localhost:8001/metrics from within backend container
    print("[9] To verify Prometheus metrics, run `curl http://localhost:8001/metrics` in backend container.")

if __name__ == "__main__":
    main()
