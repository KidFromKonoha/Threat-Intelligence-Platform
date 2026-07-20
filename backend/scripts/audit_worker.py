import sys
import logging
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.core.events.bus import RedisEventBus
from app.db.session import SessionLocal
from app.features.investigation.models import EntityEvent

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def map_event_to_entity_event(event: dict) -> EntityEvent | None:
    topic = event.get("topic", "")
    payload = event.get("payload", {})
    
    if "indicator_id" not in payload:
        return None
        
    entity_id = payload["indicator_id"]
    event_type = topic.split(".")[-1].replace("_", " ").title() # e.g. "calculated" -> "Calculated", "alert_created" -> "Alert Created"
    
    # Standardize the event names visually
    if topic == "tip.events.indicator.persisted":
        event_type = "Indicator Persisted"
    elif topic == "tip.events.indicator.enriched":
        event_type = "Indicator Enriched"
    elif topic == "tip.events.relationships.updated":
        event_type = "Relationships Updated"
    elif topic == "tip.events.risk_score.calculated":
        event_type = "Risk Score Calculated"
    elif topic == "tip.events.watchlist.alert_created":
        event_type = "Watchlist Alert Created"

    return EntityEvent(
        entity_type="indicator",
        entity_id=entity_id,
        event_type=event_type,
        payload=payload
    )

def process_event(event: dict) -> None:
    entity_event = map_event_to_entity_event(event)
    if not entity_event:
        return
        
    db = SessionLocal()
    try:
        db.add(entity_event)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error persisting audit event: {e}")
    finally:
        db.close()

def main():
    logger.info("Starting Audit Logger Worker...")
    from app.core.events.registry import EventRegistry
    from app.core.events.subscriber import ConsumerGroupSubscriber
    
    registry = EventRegistry()
    
    topics = [
        "tip.events.indicator.persisted",
        "tip.events.indicator.enriched",
        "tip.events.relationships.updated",
        "tip.events.risk_score.calculated",
        "tip.events.watchlist.alert_created"
    ]
    
    for topic in topics:
        registry.register(topic, process_event)
        
    subscriber = ConsumerGroupSubscriber(
        registry=registry,
        group_name="audit_logger_group",
        consumer_name="audit_worker_1"
    )
    
    logger.info(f"Subscribing to {topics}...")
    subscriber.consume(topics)

if __name__ == "__main__":
    main()
