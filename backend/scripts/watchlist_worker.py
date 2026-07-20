import sys
import time
import logging
from pathlib import Path
from prometheus_client import start_http_server, Counter, Summary, Gauge

backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.core.events.bus import RedisEventBus
from app.db.session import SessionLocal
from app.features.indicators.models import Indicator
from app.features.watchlists.engine import WatchlistEngineService
from sqlalchemy.orm import selectinload

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Prometheus Metrics
EVALUATIONS_TOTAL = Counter("tip_watchlist_evaluations_total", "Total indicator evaluations against watchlists")
ALERTS_CREATED_TOTAL = Counter("tip_alerts_created_total", "Total watchlist alerts created/updated")
PROCESSING_LATENCY = Summary("tip_alert_processing_latency_seconds", "Latency of evaluating an indicator")
QUEUE_DEPTH = Gauge("tip_alert_queue_depth", "Current queue depth for watchlist worker")

def process_event(event: dict) -> None:
    indicator_id = event["payload"]["indicator_id"]
    
    start_time = time.time()
    
    db = SessionLocal()
    try:
        # Load the indicator with all relationships required by the rules engine
        indicator = db.query(Indicator).options(
            selectinload(Indicator.threat_actors),
            selectinload(Indicator.campaigns),
            selectinload(Indicator.malware),
            selectinload(Indicator.techniques)
        ).filter(Indicator.id == indicator_id).first()
        
        if not indicator:
            logger.warning(f"Indicator {indicator_id} not found, skipping.")
            return

        EVALUATIONS_TOTAL.inc()
        alerts_generated = WatchlistEngineService.evaluate_indicator(db, indicator)
        
        if alerts_generated > 0:
            ALERTS_CREATED_TOTAL.inc(alerts_generated)
            logger.info(f"Generated {alerts_generated} alerts for indicator {indicator_id}")
            
    except Exception as e:
        logger.error(f"Error processing watchlist evaluation for {indicator_id}: {e}", exc_info=True)
        raise
    finally:
        db.close()
        PROCESSING_LATENCY.observe(time.time() - start_time)

def main():
    logger.info("Starting Watchlist Worker...")
    
    # Start Prometheus metrics server
    start_http_server(8001)
    logger.info("Prometheus metrics available on port 8001")
    
    from app.core.events.registry import EventRegistry
    from app.core.events.subscriber import ConsumerGroupSubscriber
    
    registry = EventRegistry()
    
    # We only subscribe to RiskScoreCalculated because it's the final step in the pipeline.
    # Evaluating earlier would lead to incomplete rule matching.
    topics = [
        "tip.events.risk_score.calculated"
    ]
    
    for topic in topics:
        registry.register(topic, process_event)
        
    subscriber = ConsumerGroupSubscriber(
        registry=registry,
        group_name="watchlist_engine_group",
        consumer_name="watchlist_worker_1"
    )
    
    logger.info(f"Subscribing to {topics}...")
    subscriber.consume(topics)

if __name__ == "__main__":
    main()
