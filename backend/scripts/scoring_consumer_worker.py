import sys
from pathlib import Path
import logging
import socket
import os
from typing import Any

backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.core.events.registry import EventRegistry
from app.core.events.subscriber import ConsumerGroupSubscriber
from app.core.logging import configure_logging
from app.db.session import SessionLocal
from app.features.scoring.consumer import ScoringConsumerService

logger = logging.getLogger(__name__)

def handle_relationships_updated(event_data: dict[str, Any]) -> None:
    """Handle the relationships updated event."""
    payload = event_data.get("payload", {})
    indicator_id = payload.get("indicator_id")
    
    if not indicator_id:
        logger.error("Missing indicator_id in payload.")
        return
        
    logger.info("Received RelationshipsUpdated event for %s", indicator_id)
    
    db = SessionLocal()
    try:
        ScoringConsumerService.handle_relationships_updated(db, indicator_id)
    except Exception as exc:
        logger.exception("Failed to run scoring consumer for %s", indicator_id)
        raise
    finally:
        db.close()

def main():
    configure_logging()
    
    consumer_name = f"{socket.gethostname()}-{os.getpid()}"
    group_name = "cg:scoring_engine"
    
    logger.info("Starting Scoring Consumer Worker (Group: %s, Consumer: %s)...", group_name, consumer_name)

    registry = EventRegistry()
    registry.register("tip.events.relationships.updated", handle_relationships_updated)

    subscriber = ConsumerGroupSubscriber(registry, group_name=group_name, consumer_name=consumer_name)
    
    try:
        subscriber.consume(["tip.events.relationships.updated"])
    except KeyboardInterrupt:
        logger.info("Scoring Consumer Worker stopped by user.")

if __name__ == "__main__":
    main()
