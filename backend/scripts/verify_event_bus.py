import sys
from pathlib import Path

# Add the backend directory to sys.path so we can import 'app'
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

import logging
from typing import Any

from app.core.events.registry import EventRegistry
from app.core.events.subscriber import SimpleRedisSubscriber
from app.core.logging import configure_logging

logger = logging.getLogger(__name__)

def handle_indicator_enriched(event_data: dict[str, Any]) -> None:
    """A dummy handler to prove the event bus works."""
    payload = event_data.get("payload", {})
    logger.info(
        "Proof of Concept Handler Triggered!\n"
        "  Event ID: %s\n"
        "  Producer: %s\n"
        "  Indicator ID: %s",
        event_data.get("event_id"),
        event_data.get("producer"),
        payload.get("indicator_id"),
    )

def main():
    configure_logging()
    logger.info("Starting Event Bus Verification...")

    registry = EventRegistry()
    registry.register("tip.events.indicator.enriched", handle_indicator_enriched)

    subscriber = SimpleRedisSubscriber(registry)
    
    try:
        # Will block and listen for new events
        subscriber.consume(["tip.events.indicator.enriched"])
    except KeyboardInterrupt:
        logger.info("Verification stopped by user.")

if __name__ == "__main__":
    main()
