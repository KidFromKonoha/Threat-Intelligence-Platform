import abc
import uuid

from app.core.redis import get_redis_client
from app.core.events.schema import EventEnvelope
from app.core.events.serializer import EventSerializer

class EventBus(abc.ABC):
    """Abstract interface for publishing events."""
    
    @abc.abstractmethod
    def publish(self, event_name: str, event: EventEnvelope) -> None:
        """Publish an event to the underlying transport."""
        pass


class RedisEventBus(EventBus):
    """Redis Streams implementation of the EventBus."""
    
    def __init__(self):
        self.redis = get_redis_client()

    def publish(self, event_name: str, event: EventEnvelope) -> None:
        """Publish an event to a Redis Stream named after the event_name."""
        # Automatically populate correlation_id if not present
        if not event.correlation_id:
            event.correlation_id = str(uuid.uuid4())
            
        payload_str = EventSerializer.serialize(event)
        
        # Publish to the stream matching the event name
        self.redis.xadd(event_name, {"event": payload_str})
