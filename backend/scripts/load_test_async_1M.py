import sys
import time
import uuid
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.core.events.bus import RedisEventBus
from app.core.events.schema import EventEnvelope
from app.db.session import SessionLocal
from app.features.indicators.models import Indicator

def main():
    print("--- Worker Throughput Benchmark (500k-1M) ---")
    db = SessionLocal()
    bus = RedisEventBus()

    indicator = db.query(Indicator).first()
    if not indicator:
        print("No indicator found.")
        return
        
    indicator_id = indicator.id
    db.close()
    
    total = 1000000
    print(f"Injecting {total} events into Redis for Watchlist Worker...")
    
    start_time = time.time()
    
    # We pipeline the publish using raw redis pipeline to be extremely fast
    pipeline = bus.redis.pipeline(transaction=False)
    
    for i in range(total):
        # We manually serialize to avoid overhead in the loop for maximum throughput testing
        import json
        payload = {
            "topic": "tip.events.risk_score.calculated",
            "producer": "load_test_1M",
            "correlation_id": str(uuid.uuid4()),
            "timestamp": "2026-07-15T00:00:00Z",
            "payload": {
                "indicator_id": indicator_id,
                "risk_score": 95
            }
        }
        pipeline.xadd("tip.events.risk_score.calculated", {"event": json.dumps(payload)})
        
        if i % 10000 == 0:
            pipeline.execute()
            print(f"Injected {i} events...")
            
    pipeline.execute()
    
    duration = time.time() - start_time
    print(f"Injected {total} events in {duration:.2f} seconds ({total/duration:.2f} msg/sec).")
    print("Monitor Prometheus metrics for worker throughput and lag.")

if __name__ == "__main__":
    main()
