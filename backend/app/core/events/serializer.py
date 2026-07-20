import json
from typing import Any

from pydantic import BaseModel

from app.core.events.schema import EventEnvelope

class EventSerializer:
    """Handles serialization and deserialization of EventEnvelopes."""
    
    @staticmethod
    def serialize(envelope: EventEnvelope) -> str:
        """Serialize an EventEnvelope to a JSON string."""
        return json.dumps(envelope.model_dump(mode="json"))

    @staticmethod
    def deserialize(payload_str: str) -> dict[str, Any]:
        """Deserialize a JSON string to a raw dictionary.
        
        The registry will handle coercing the payload back into the specific Pydantic model.
        """
        return json.loads(payload_str)
