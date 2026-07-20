import sys
from pathlib import Path
import logging
import socket
import os
from typing import Any

# Add the backend directory to sys.path so we can import 'app'
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.core.events.registry import EventRegistry
from app.core.events.subscriber import ConsumerGroupSubscriber
from app.core.logging import configure_logging
from app.db.session import SessionLocal
from app.features.relationship_engine.service import RelationshipEngineService

logger = logging.getLogger(__name__)

def handle_indicator_enriched(event_data: dict[str, Any]) -> None:
    """Handle the indicator enriched event by triggering relationship extraction."""
    payload = event_data.get("payload", {})
    indicator_id = payload.get("indicator_id")
    
    if not indicator_id:
        logger.error("Missing indicator_id in payload.")
        return
        
    logger.info("Received IndicatorEnriched event for %s", indicator_id)
    
    from app.core.events.bus import RedisEventBus
    db = SessionLocal()
    event_bus = RedisEventBus()
    
    try:
        RelationshipEngineService.run_engine_sync(db, indicator_id, event_bus=event_bus)
    except Exception as exc:
        logger.exception("Failed to run relationship engine for %s", indicator_id)
        raise
    finally:
        db.close()


def main():
    configure_logging()
    
    consumer_name = f"{socket.gethostname()}-{os.getpid()}"
    group_name = "cg:relationship_engine"
    
    logger.info("Starting Relationship Engine Worker (Group: %s, Consumer: %s)...", group_name, consumer_name)

    registry = EventRegistry()
    registry.register("tip.events.indicator.enriched", handle_indicator_enriched)

    subscriber = ConsumerGroupSubscriber(registry, group_name=group_name, consumer_name=consumer_name)
    
    try:
        # Will block and listen for new events
        subscriber.consume(["tip.events.indicator.enriched"])
    except KeyboardInterrupt:
        logger.info("Relationship Engine Worker stopped by user.")

if __name__ == "__main__":
    main()
