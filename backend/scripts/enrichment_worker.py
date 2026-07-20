import sys
from pathlib import Path

# Add the backend directory to sys.path so we can import 'app'
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

import logging
from typing import Any

from app.core.events.registry import EventRegistry
from app.core.events.subscriber import ConsumerGroupSubscriber
from app.core.events.bus import RedisEventBus
from app.core.logging import configure_logging
from app.db.session import SessionLocal
from app.features.enrichment.service import EnrichmentService

logger = logging.getLogger(__name__)

def handle_indicator_persisted(event_data: dict[str, Any]) -> None:
    """Handle the indicator persisted event by triggering enrichment."""
    payload = event_data.get("payload", {})
    indicator_id = payload.get("indicator_id")
    
    correlation_id = event_data.get("correlation_id")
    
    if not indicator_id:
        logger.error("Missing indicator_id in payload.")
        return
        
    logger.info("Received IndicatorPersisted event for %s", indicator_id)
    
    db = SessionLocal()
    event_bus = RedisEventBus()
    
    try:
        EnrichmentService.run_enrichment_sync(db, indicator_id, event_bus, correlation_id)
    except Exception as exc:
        logger.exception("Failed to run enrichment for %s", indicator_id)
        raise
    finally:
        db.close()


def main():
    import socket
    import os
    configure_logging()
    
    consumer_name = f"{socket.gethostname()}-{os.getpid()}"
    group_name = "cg:enrichment_engine"
    
    logger.info("Starting Enrichment Worker (Group: %s, Consumer: %s)...", group_name, consumer_name)

    registry = EventRegistry()
    registry.register("tip.events.indicator.persisted", handle_indicator_persisted)

    subscriber = ConsumerGroupSubscriber(registry, group_name=group_name, consumer_name=consumer_name)
    
    try:
        # Will block and listen for new events
        subscriber.consume(["tip.events.indicator.persisted"])
    except KeyboardInterrupt:
        logger.info("Enrichment Worker stopped by user.")

if __name__ == "__main__":
    main()
