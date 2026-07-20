import abc
import logging

from app.core.redis import get_redis_client
from app.core.events.registry import EventRegistry
from app.core.events.serializer import EventSerializer

logger = logging.getLogger(__name__)

class EventSubscriber(abc.ABC):
    """Abstract interface for consuming events."""
    
    @abc.abstractmethod
    def consume(self, stream_names: list[str]) -> None:
        """Consume events from the specified streams."""
        pass


class SimpleRedisSubscriber(EventSubscriber):
    """A simplified Redis XREAD subscriber (Proof of Concept).
    
    This does not use Consumer Groups and will read new messages that 
    arrive after it starts listening. Designed for operational verification.
    """
    def __init__(self, registry: EventRegistry):
        self.redis = get_redis_client()
        self.registry = registry

    def consume(self, stream_names: list[str]) -> None:
        # Start reading from current latest for all streams
        streams = {stream: "$" for stream in stream_names}
        
        logger.info("Listening on streams: %s", stream_names)
        while True:
            try:
                # Block for 5000ms waiting for messages
                messages = self.redis.xread(streams, count=10, block=5000)
                if not messages:
                    continue

                for stream_name, msg_list in messages:
                    for message_id, message_data in msg_list:
                        try:
                            event_json = message_data.get("event")
                            if not event_json:
                                continue
                            
                            # Deserialize via EventSerializer
                            event_data = EventSerializer.deserialize(event_json)
                            
                            # Dispatch to transport-agnostic registry
                            self.registry.dispatch(stream_name, event_data)
                            
                        finally:
                            # Update the last read ID for this stream
                            streams[stream_name] = message_id
            except Exception as exc:
                logger.error("Error consuming from Redis Stream: %s", exc)
                import time
                time.sleep(1)


class ConsumerGroupSubscriber(EventSubscriber):
    """A production-grade Redis Consumer Group subscriber.
    
    Implements reliable at-least-once delivery, horizontal scaling,
    and automatic recovery of pending messages (PEL) via XAUTOCLAIM.
    """
    def __init__(self, registry: EventRegistry, group_name: str, consumer_name: str):
        from app.core.config import settings
        self.redis = get_redis_client()
        self.registry = registry
        self.group_name = group_name
        self.consumer_name = consumer_name
        self.max_retries = settings.EVENT_MAX_RETRIES

    def consume(self, stream_names: list[str]) -> None:
        import time
        # 1. Initialize groups for all streams
        for stream in stream_names:
            try:
                self.redis.xgroup_create(stream, self.group_name, id='0', mkstream=True)
            except Exception as e:
                if "BUSYGROUP" not in str(e):
                    raise

        # 2. Consume loop
        streams = {stream: ">" for stream in stream_names}
        logger.info("Consumer %s (Group %s) listening on %s", self.consumer_name, self.group_name, stream_names)
        
        while True:
            try:
                # Recover orphaned/pending messages first
                for stream in stream_names:
                    self._recover_pending(stream)
                    
                # Read new messages, blocking for 5s
                messages = self.redis.xreadgroup(self.group_name, self.consumer_name, streams, count=10, block=5000)
                if messages:
                    for stream_name, msg_list in messages:
                        self._process_messages(stream_name, msg_list)
            except Exception as exc:
                logger.error("Error in consumer loop: %s", exc)
                time.sleep(1)

    def _recover_pending(self, stream_name: str) -> None:
        try:
            # 5 mins min_idle_time (300000ms)
            result = self.redis.xautoclaim(stream_name, self.group_name, self.consumer_name, 300000, '0-0', count=10)
            if result and len(result) >= 2:
                messages = result[1]
                if messages:
                    logger.info("Recovered %d pending messages from %s", len(messages), stream_name)
                    self._process_messages(stream_name, messages)
        except Exception as exc:
            logger.error("Error recovering pending messages from %s: %s", stream_name, exc)

    def _process_messages(self, stream_name: str, messages: list) -> None:
        for message_id, message_data in messages:
            try:
                # Convert message_id to string if it's bytes
                if isinstance(message_id, bytes):
                    message_id = message_id.decode('utf-8')
                    
                # Check delivery count for DLQ
                pending_info = self.redis.xpending_range(stream_name, self.group_name, min=message_id, max=message_id, count=1)
                delivery_count = 1
                if pending_info:
                    delivery_count = pending_info[0].get('times_delivered', 1)

                if delivery_count > self.max_retries:
                    logger.critical("Poison message %s in %s exceeded max retries (%d). Moving to DLQ.", message_id, stream_name, self.max_retries)
                    # Move to DLQ
                    self.redis.xadd("tip.events.dlq", message_data)
                    self.redis.xack(stream_name, self.group_name, message_id)
                    continue

                event_json = message_data.get(b"event") or message_data.get("event")
                if not event_json:
                    self.redis.xack(stream_name, self.group_name, message_id)
                    continue
                
                # Deserialize via EventSerializer
                event_data = EventSerializer.deserialize(event_json)
                
                # Dispatch to transport-agnostic registry
                self.registry.dispatch(stream_name, event_data)
                
                # Acknowledge success
                self.redis.xack(stream_name, self.group_name, message_id)
                
            except Exception as exc:
                logger.error("Error processing message %s from %s: %s", message_id, stream_name, exc)
                # Do NOT xack. It will remain in PEL and be retried later.
