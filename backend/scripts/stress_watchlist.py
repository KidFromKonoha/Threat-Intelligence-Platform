import sys
import time
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.core.events.bus import RedisEventBus
from app.core.events.schema import EventEnvelope
from app.db.session import SessionLocal
from app.features.indicators.models import Indicator

def main():
    db = SessionLocal()
    bus = RedisEventBus()

    # Get a dummy indicator
    indicator = db.query(Indicator).first()
    if not indicator:
        print("No indicator found. Run verify_watchlist.py first.")
        return
        
    indicator_id = indicator.id
    db.close()
    
    print(f"Starting stress test for indicator {indicator_id}...")
    start = time.time()
    
    for i in range(10000):
        bus.publish(
            "tip.events.risk_score.calculated",
            EventEnvelope(
                topic="tip.events.risk_score.calculated",
                producer="stress_script",
                payload={
                    "indicator_id": indicator_id,
                    "risk_score": 90 + (i % 10)
                }
            )
        )
        
    duration = time.time() - start
    print(f"Published 10,000 events in {duration:.2f} seconds ({10000/duration:.2f} events/sec).")
    print("Wait a moment and check Prometheus metrics at http://localhost:8001/metrics")

if __name__ == "__main__":
    main()
