import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from datetime import datetime, timezone
from app.db.session import SessionLocal
from app.features.feeds.pipeline import StoragePipeline
from app.features.feeds.schemas import CollectorMetrics, RawIndicator
from app.core.events.bus import RedisEventBus
from app.core.logging import configure_logging

def main():
    configure_logging()
    db = SessionLocal()
    
    from app.features.feeds.models import Feed
    feed = db.query(Feed).first()
    if not feed:
        print("No feeds found in db.")
        return
        
    pipeline = StoragePipeline(event_bus=RedisEventBus())
    metrics = CollectorMetrics(feed_name=feed.name)
    
    indicators = [
        RawIndicator(
            type="ipv4",
            value="198.51.100.42",
            normalized_value="198.51.100.42",
            confidence=90,
            severity="high",
            first_seen=datetime.now(timezone.utc),
            last_seen=datetime.now(timezone.utc),
            tags=["test"]
        )
    ]
    
    pipeline.run(db, feed_id=feed.id, indicators=indicators, metrics=metrics)
    print("StoragePipeline complete.")

if __name__ == "__main__":
    main()
