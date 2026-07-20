import sys
from pathlib import Path
import logging
import time
from sqlalchemy import text
import redis

backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.core.logging import configure_logging
from app.db.session import SessionLocal
from app.core.events.bus import RedisEventBus
from app.core.events.schema import EventEnvelope, IndicatorEnrichedPayload

logger = logging.getLogger(__name__)

def run_tests(indicator_id: str, ta_name: str):
    configure_logging()
    db = SessionLocal()
    r = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)
    
    print("=== Test 2: Duplicate Event ===")
    bus = RedisEventBus()
    env = EventEnvelope(
        producer="test_script_duplicate",
        payload=IndicatorEnrichedPayload(indicator_id=indicator_id)
    )
    bus.publish("tip.events.indicator.enriched", env)
    logger.info("Published duplicate IndicatorEnriched event.")
    time.sleep(3)
    
    count_rels = db.execute(text(
        "SELECT count(*) FROM indicator_threat_actor WHERE indicator_id = :id"
    ), {"id": indicator_id}).scalar()
    print(f"Relationships count for indicator {indicator_id}: {count_rels}")
    assert count_rels == 1, "Duplicate relationship created!"
    print("Test 2 PASSED: No duplicate relationships.")
    
    print("\n=== Test 4: RelationshipsUpdated Event ===")
    events = r.xrange("tip.events.relationships.updated", "-", "+")
    found = False
    for event_id, event_data in events:
        if indicator_id in str(event_data):
            print(f"Found event {event_id}: {event_data}")
            found = True
    assert found, "RelationshipsUpdated event not found in Redis!"
    print("Test 4 PASSED: Event exists in Redis.")
    
    print("\n=== Test 6: Bulk Scoring ===")
    from app.features.scoring.tasks import bulk_score_indicators_task
    # Call the celery task synchronously
    bulk_score_indicators_task()
    time.sleep(2)
    
    ind = db.execute(text("SELECT needs_scoring, risk_score, scored_at FROM indicators WHERE id = :id"), {"id": indicator_id}).fetchone()
    print(f"Indicator after scoring: needs_scoring={ind[0]}, risk_score={ind[1]}, scored_at={ind[2]}")
    assert ind[0] is False, "needs_scoring should be False"
    assert ind[2] is not None, "scored_at should be updated"
    print("Test 6 PASSED: Bulk Scoring executed successfully.")
    
    print("\n=== Test 8: Database Verification ===")
    print("--- indicator_threat_actor ---")
    rows = db.execute(text("SELECT * FROM indicator_threat_actor WHERE indicator_id = :id"), {"id": indicator_id}).fetchall()
    for row in rows:
        print(row)
        
    print("--- indicators ---")
    rows = db.execute(text("SELECT id, type, value, needs_scoring, risk_score FROM indicators WHERE id = :id"), {"id": indicator_id}).fetchall()
    for row in rows:
        print(row)
        
    print("\n=== Test 9: Redis Verification ===")
    streams = [
        "tip.events.indicator.persisted",
        "tip.events.indicator.enriched",
        "tip.events.relationships.updated",
        "tip.events.risk_score.calculated"
    ]
    for stream in streams:
        print(f"\n--- {stream} ---")
        try:
            length = r.xlen(stream)
            print(f"XLEN: {length}")
            groups = r.xinfo_groups(stream)
            print(f"XINFO GROUPS: {groups}")
        except Exception as e:
            print(f"Could not fetch info for {stream}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python e2e_verify.py <indicator_id> <ta_name>")
        sys.exit(1)
    run_tests(sys.argv[1], sys.argv[2])
