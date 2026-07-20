import sys
import time
from pathlib import Path
from datetime import datetime, timezone

backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.db.session import SessionLocal
from app.features.feeds.models import Feed
from app.features.feeds.pipeline import StoragePipeline
from app.features.feeds.schemas import CollectorMetrics, RawIndicator
from app.core.events.bus import RedisEventBus
from app.core.logging import configure_logging

def main():
    configure_logging()
    print("--- Full System Benchmark (100k) ---")
    db = SessionLocal()
    bus = RedisEventBus()
    
    # Get or create feed
    feed = db.query(Feed).filter(Feed.name == "Load Test Feed 100k").first()
    if not feed:
        feed = Feed(
            name="Load Test Feed 100k",
            description="Feed for load testing",
            type="open_source",
            enabled=True,
            status="active"
        )
        db.add(feed)
        db.commit()
        db.refresh(feed)
        
    print(f"Using Feed ID: {feed.id}")
    
    pipeline = StoragePipeline(event_bus=bus)
    metrics = CollectorMetrics(feed_name=feed.name)
    
    total = 100000
    batch_size = 10000
    
    start_time = time.time()
    now = datetime.now(timezone.utc)
    
    for i in range(0, total, batch_size):
        indicators = []
        for j in range(batch_size):
            num = i + j
            # We use an IP range so they don't all collide on duplicate normalized_value
            ip_str = f"100.{num // 65536}.{(num // 256) % 256}.{num % 256}"
            indicators.append(
                RawIndicator(
                    type="ipv4",
                    value=ip_str,
                    normalized_value=ip_str,
                    confidence=50,
                    severity="medium",
                    first_seen=now,
                    last_seen=now,
                    tags=["load_test_100k"]
                )
            )
            
        print(f"Submitting batch {i//batch_size + 1}/{total//batch_size} (size={batch_size}) via StoragePipeline...")
        
        batch_start = time.time()
        pipeline.run(db, feed_id=feed.id, indicators=indicators, metrics=metrics)
        batch_duration = time.time() - batch_start
        print(f"Batch inserted in {batch_duration:.2f} seconds.")
        
    duration = time.time() - start_time
    print(f"Finished inserting {total} indicators in {duration:.2f} seconds ({total/duration:.2f} indicators/sec).")
    print(f"Metrics: Added={metrics.records_added}, Updated={metrics.records_updated}, Errors={len(metrics.errors)}")
    print("Monitor downstream background workers and Prometheus metrics.")

if __name__ == "__main__":
    main()
