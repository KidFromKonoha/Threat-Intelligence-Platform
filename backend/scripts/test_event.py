import sys
from pathlib import Path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.core.events.schema import EventEnvelope
e = EventEnvelope(topic="test", producer="watchlist_engine", payload={"alert_id": 1})
print(e.correlation_id)
