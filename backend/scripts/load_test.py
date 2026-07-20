import sys
from pathlib import Path
import random
import time
import uuid

# Add the backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from datetime import datetime, timezone
from app.db.session import SessionLocal
from app.features.feeds.pipeline import StoragePipeline
from app.features.feeds.schemas import CollectorMetrics, RawIndicator
from app.core.events.bus import RedisEventBus
from app.core.logging import configure_logging
from app.features.feeds.models import Feed
import logging

logger = logging.getLogger(__name__)

def generate_synthetic_indicators(count: int) -> list[RawIndicator]:
    indicators = []
    base_ip = 100
    for i in range(count):
        # Generate varied IPs
        ip_str = f"10.{base_ip + (i % 150)}.{ (i // 150) % 255 }.{ i % 255 }"
        indicators.append(
            RawIndicator(
                type="ipv4",
                value=ip_str,
                normalized_value=ip_str,
                confidence=random.randint(40, 100),
                severity=random.choice(["low", "medium", "high", "critical"]),
                first_seen=datetime.now(timezone.utc),
                last_seen=datetime.now(timezone.utc),
                tags=["load-test"]
            )
        )
    return indicators

def main():
    configure_logging()
    db = SessionLocal()
    
    feed = db.query(Feed).first()
    if not feed:
        logger.error("No feeds found. Run seed_roles.py or create a feed first.")
        return
        
    num_indicators = 5000
    logger.info("Generating %d synthetic indicators...", num_indicators)
    indicators = generate_synthetic_indicators(num_indicators)
    
    pipeline = StoragePipeline(event_bus=RedisEventBus())
    metrics = CollectorMetrics(feed_name=feed.name)
    
    logger.info("Starting Bulk Import...")
    start_time = time.time()
    
    # We will chunk it to simulate batch processing and prevent massive memory spikes in a single transaction
    chunk_size = 1000
    for i in range(0, len(indicators), chunk_size):
        chunk = indicators[i:i + chunk_size]
        logger.info("Processing chunk %d to %d...", i, i + len(chunk))
        pipeline.run(db, feed_id=feed.id, indicators=chunk, metrics=metrics)
        
    end_time = time.time()
    logger.info("Bulk Import complete in %.2f seconds.", end_time - start_time)
    logger.info("Metrics: Added: %d, Updated: %d, Skipped: %d, Errors: %d", 
                metrics.records_added, metrics.records_updated, 
                metrics.records_skipped, len(metrics.errors))

if __name__ == "__main__":
    main()
