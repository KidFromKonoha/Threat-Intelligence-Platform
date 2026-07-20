import logging
from typing import Callable, Dict, List, Any

logger = logging.getLogger(__name__)

class EventRegistry:
    """A transport-agnostic registry that dispatches deserialized events to registered handlers."""
    
    def __init__(self):
        # event_name (e.g., 'tip.events.indicator.persisted') -> list of handler functions
        self.handlers: Dict[str, List[Callable[[dict[str, Any]], None]]] = {}

    def register(self, event_name: str, handler: Callable[[dict[str, Any]], None]) -> None:
        """Register a handler for a specific event type."""
        if event_name not in self.handlers:
            self.handlers[event_name] = []
        self.handlers[event_name].append(handler)
        logger.info("Registered handler %s for event %s", handler.__name__, event_name)

    def dispatch(self, event_name: str, event_data: dict[str, Any]) -> None:
        """Dispatch a deserialized event payload to all registered handlers."""
        if event_name not in self.handlers:
            logger.warning("No handlers registered for event %s", event_name)
            return
        
        for handler in self.handlers[event_name]:
            try:
                handler(event_data)
            except Exception as exc:
                logger.error(
                    "Handler %s failed for event %s: %s", 
                    handler.__name__, 
                    event_name, 
                    exc, 
                    exc_info=True
                )
