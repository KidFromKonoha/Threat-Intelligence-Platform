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

logger = logging.getLogger(__name__)

def main():
    configure_logging()
    db = SessionLocal()
    
    # Clean up previous tests? No, just create a unique TA.
    ta_name = "test_e2e_" + str(uuid.uuid4())[:8]
    ta = ThreatActor(name=ta_name, country="RU", motivation="Testing")
    db.add(ta)
    
    feed = db.query(Feed).first()
    if not feed:
        feed = Feed(name="E2E Test Feed")
        db.add(feed)
    db.commit()
    
    logger.info(f"Seeded Threat Actor: {ta_name}")
    
    # Insert T1: Valid indicator
    ind_value_t1 = f"10.0.1.{uuid.uuid4().time_low % 255}"
    raw_t1 = RawIndicator(
        type="ipv4",
        value=ind_value_t1,
        normalized_value=ind_value_t1,
        confidence=90,
        severity="medium",
        tags=["e2e", ta_name], # matches Threat Actor
        first_seen=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        last_seen=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        status="active"
    )
    
    # Insert T3: Unknown tag
    ind_value_t3 = f"10.0.3.{uuid.uuid4().time_low % 255}"
    raw_t3 = RawIndicator(
        type="ipv4",
        value=ind_value_t3,
        normalized_value=ind_value_t3,
        confidence=90,
        severity="medium",
        tags=["e2e", "unknown_tag_12345"],
        first_seen=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        last_seen=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        status="active"
    )
    
    pipeline = StoragePipeline()
    # The storage pipeline doesn't have an event bus configured in the script, so it won't emit IndicatorPersisted automatically
    # Wait, the main app configures it.
    # Let's pass the RedisEventBus to the pipeline so the whole chain triggers natively!
    from app.core.events.bus import RedisEventBus
    bus = RedisEventBus()
    pipeline = StoragePipeline(event_bus=bus)
    
    metrics = CollectorMetrics(feed_name="E2E Test Feed", records_fetched=2)
    pipeline.run(db, feed.id, [raw_t1, raw_t3], metrics)
    
    logger.info("Pipeline executed for Test 1 and Test 3. Event tip.events.indicator.persisted should have been published.")
    
    # Wait a bit
    logger.info("Waiting 5 seconds for background workers to process (Enrichment -> Relationship -> ScoringConsumer)...")
    time.sleep(5)
    
    # Verification T1
    db.expire_all()
    ind_1 = db.query(Indicator).filter(Indicator.value == ind_value_t1).first()
    assert ind_1, "T1 Indicator missing"
    
    # Verification T3
    ind_3 = db.query(Indicator).filter(Indicator.value == ind_value_t3).first()
    assert ind_3, "T3 Indicator missing"
    
    logger.info(f"T1 needs_scoring: {ind_1.needs_scoring}")
    logger.info(f"T3 needs_scoring: {ind_3.needs_scoring}")
    
    # Get relations for T1
    ta_rels_1 = ind_1.threat_actors
    if ta_rels_1 is None:
        ta_rels_1 = []
    elif not isinstance(ta_rels_1, list):
        ta_rels_1 = [ta_rels_1]
    
    if any(a.name == ta_name for a in ta_rels_1):
        logger.info(f"T1 SUCCESS: Indicator is linked to {ta_name}")
    else:
        logger.error(f"T1 FAIL: Indicator NOT linked to {ta_name}")
        
    # Get relations for T3
    ta_rels_3 = ind_3.threat_actors
    if ta_rels_3 is None:
        ta_rels_3 = []
    elif not isinstance(ta_rels_3, list):
        ta_rels_3 = [ta_rels_3]
        
    if len(ta_rels_3) == 0:
        logger.info("T3 SUCCESS: No relationships created for unknown tag.")
    else:
        logger.error("T3 FAIL: Relationships created for unknown tag!")
        
    logger.info(f"T1 Indicator ID for reference: {ind_1.id}")
    
    print(f"\n--- DATA FOR SUBSEQUENT TESTS ---")
    print(f"export T1_INDICATOR_ID={ind_1.id}")
    print(f"export T3_INDICATOR_ID={ind_3.id}")
    print(f"export TA_NAME={ta_name}")

if __name__ == "__main__":
    main()
