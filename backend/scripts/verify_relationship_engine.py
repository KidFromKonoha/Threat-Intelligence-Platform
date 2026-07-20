import sys
from pathlib import Path
import logging
import uuid
import time

backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.core.logging import configure_logging
from app.db.session import SessionLocal
from app.features.threat_actors.models import ThreatActor
from app.features.indicators.models import Indicator
from app.features.feeds.models import Feed
from app.features.feeds.pipeline import StoragePipeline

logger = logging.getLogger(__name__)

def main():
    configure_logging()
    db = SessionLocal()
    
    # 1. Ensure Threat Actor exists
    ta_name = "test_apt_" + str(uuid.uuid4())[:8]
    ta = ThreatActor(name=ta_name, country="RU", motivation="Espionage")
    db.add(ta)
    
    # Ensure Feed exists
    feed = db.query(Feed).first()
    if not feed:
        feed = Feed(name="Test Feed")
        db.add(feed)
    db.commit()
    
    from app.features.feeds.schemas import RawIndicator, CollectorMetrics
    
    ind_value = f"198.51.100.{uuid.uuid4().time_low % 255}"
    raw = RawIndicator(
        type="ipv4",
        value=ind_value,
        normalized_value=ind_value,
        confidence=90,
        severity="medium",
        tags=["phishing", ta_name],
        first_seen=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        last_seen=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        status="active"
    )
    
    logger.info(f"Ingesting indicator {ind_value} with tag {ta_name}")
    pipeline = StoragePipeline()
    metrics = CollectorMetrics(feed_name="Test Feed", records_fetched=1)
    
    pipeline.run(db, feed.id, [raw], metrics)
    
    indicator_id = None
    ind = db.query(Indicator).filter(Indicator.value == ind_value).first()
    if ind:
        indicator_id = ind.id
        logger.info(f"Indicator persisted with ID: {indicator_id}")
    else:
        logger.error("Indicator not inserted")
        return
        
    # Fire event manually
    from app.core.events.bus import RedisEventBus
    from app.core.events.schema import EventEnvelope, IndicatorEnrichedPayload
    bus = RedisEventBus()
    
    env = EventEnvelope(
        producer="test_script",
        payload=IndicatorEnrichedPayload(indicator_id=str(indicator_id))
    )
    bus.publish("tip.events.indicator.enriched", env)
    logger.info("Fired tip.events.indicator.enriched event manually.")
    
    logger.info("Waiting 3 seconds for worker to process...")
    time.sleep(3)
    
    # Verify the edge was created
    db.expire_all()
    ind = db.query(Indicator).filter(Indicator.id == indicator_id).first()
    
    assert ind, "Indicator not found"
    
    # Coerce since Mapped[list] without parameterization might return scalar or None
    ta_rels = ind.threat_actors
    if ta_rels is None:
        ta_rels = []
    elif not isinstance(ta_rels, list):
        ta_rels = [ta_rels]
        
    linked_actors = [a.name for a in ta_rels]
    
    if ta_name in linked_actors:
        logger.info(f"SUCCESS: Indicator is linked to Threat Actor {ta_name}!")
    else:
        logger.error(f"FAILURE: Indicator is NOT linked to Threat Actor {ta_name}. Found: {linked_actors}")

if __name__ == "__main__":
    main()
