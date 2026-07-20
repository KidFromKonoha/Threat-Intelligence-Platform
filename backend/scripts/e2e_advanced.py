import sys
from pathlib import Path
import logging
import uuid
import time
from sqlalchemy import text

backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.core.logging import configure_logging
from app.db.session import SessionLocal
from app.features.threat_actors.models import ThreatActor
from app.features.feeds.models import Feed
from app.features.indicators.models import Indicator
from app.features.feeds.pipeline import StoragePipeline
from app.features.feeds.schemas import RawIndicator, CollectorMetrics
from app.core.events.bus import RedisEventBus

logger = logging.getLogger(__name__)

def main():
    configure_logging()
    db = SessionLocal()
    
    ta_name = "test_e2e_concurrency"
    ta = db.query(ThreatActor).filter(ThreatActor.name == ta_name).first()
    if not ta:
        ta = ThreatActor(name=ta_name, country="RU", motivation="Testing")
        db.add(ta)
    
    feed = db.query(Feed).first()
    db.commit()
    
    logger.info("=== Test 11: Concurrency (10 indicators) ===")
    
    pipeline = StoragePipeline(event_bus=RedisEventBus())
    
    raws = []
    for i in range(10):
        ind_value = f"10.0.11.{i}"
        raw = RawIndicator(
            type="ipv4",
            value=ind_value,
            normalized_value=ind_value,
            confidence=90,
            severity="medium",
            tags=["e2e", ta_name],
            first_seen=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            last_seen=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            status="active"
        )
        raws.append(raw)
        
    metrics = CollectorMetrics(feed_name="E2E Concurrency", records_fetched=10)
    pipeline.run(db, feed.id, raws, metrics)
    
    logger.info("Published 10 indicators. Watch the logs to see if work is partitioned between the two workers.")
    time.sleep(10)
    
    count_rels = db.execute(text("SELECT count(*) FROM indicator_threat_actor WHERE threat_actor_id = :ta_id"), {"ta_id": ta.id}).scalar()
    logger.info(f"Relationships created: {count_rels}/10")
    assert count_rels == 10, "Concurrency failed or duplicate/missed edges!"
    logger.info("Test 11 PASSED!")
    
if __name__ == "__main__":
    main()
