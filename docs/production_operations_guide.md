# Production Operations & Deployment Guide

This guide details the operational procedures, architecture, observability endpoints, and disaster recovery strategies for the Threat Intelligence Platform (TIP) Architecture v1.0.

---

## 1. Architecture Overview (v1.0)

The Threat Intelligence Platform is built on an **Event-Driven Architecture (EDA)**.
- **Synchronous Layer:** HTTP APIs (`FastAPI`) are strictly Read Models or synchronous ingestion pipelines.
- **Asynchronous Layer:** Background processing is entirely decoupled using `Redis Streams`.
- **Database:** PostgreSQL (`SQLAlchemy`) acts as the primary persistence layer.

### Pipeline Flow
1. **Ingestion (StoragePipeline):** Upserts indicators and emits `tip.events.indicator.persisted`.
2. **Enrichment:** Listens to `persisted`, queries external providers, emits `tip.events.indicator.enriched`.
3. **Relationship Engine:** Listens to `enriched`, infers graph edges (Assets, Campaigns, Threat Actors), emits `tip.events.relationships.updated`.
4. **Scoring Engine:** Listens to `updated`, recalculates Risk Score based on relationships/confidence, emits `tip.events.risk_score.calculated`.
5. **Watchlist Engine:** Listens to `risk_score.calculated`, evaluates enabled watchlists, and writes `WatchlistAlert` rows.
6. **Audit Logger:** Listens to all events for compliance and security auditing.

---

## 2. Deployment Guide

### Prerequisites
- Docker & Docker Compose
- PostgreSQL 16+
- Redis 7+

### Starting the Platform
```bash
# Start all containers in the background
docker compose up -d

# Check status of the core infrastructure and workers
docker compose ps
```

### Running Migrations
Always run Alembic migrations before starting workers on a new deployment:
```bash
docker compose exec backend alembic upgrade head
```

---

## 3. Observability & Monitoring

### Structured Logging
All workers output standard structured logging (timestamp, level, module, message). 
**Correlation IDs** (`correlation_id`) are attached to the `EventEnvelope` and propagate across the entire worker pipeline (Ingestion -> Enrichment -> Relationship -> Scoring -> Watchlist) to trace the lifecycle of a single Indicator.

### Prometheus Metrics
Each background worker exposes Prometheus metrics via an HTTP server.
- **Enrichment Worker:** `http://localhost:8001/metrics`
- **Relationship Worker:** `http://localhost:8002/metrics`
- **Scoring Worker:** `http://localhost:8003/metrics`
- **Watchlist Worker:** `http://localhost:8004/metrics`

*Note: Port mappings may vary based on `docker-compose.yml`. Use `docker ps` to verify host ports.*

**Key Metrics:**
- `tip_watchlist_evaluations_total` (Counter)
- `tip_alerts_created_total` (Counter)
- `tip_alert_processing_latency_seconds` (Summary)
- `tip_alert_queue_depth` (Gauge)

---

## 4. Disaster Recovery (DR)

### Worker Crash Recovery (Redis PEL)
All asynchronous workers use Redis **Consumer Groups**. 
If a worker crashes mid-processing (e.g., PostgreSQL connection drops), the event **is not acknowledged** (`xack`).
- The event remains in the **Pending Entries List (PEL)**.
- Upon restart, the `ConsumerGroupSubscriber` performs an `XAUTOCLAIM` on startup to automatically recover and reprocess orphaned messages older than 5 minutes.
- **No data loss occurs during worker or database failure.**

### PostgreSQL Database Failure
- Workers catch `SQLAlchemyError` or `OperationalError`, log the failure (with `exc_info=True`), and explicitly `raise` the exception.
- This forces the message to stay in the PEL for retry once PostgreSQL is back online.
- PostgreSQL backups should be managed via standard `pg_dump` or WAL archiving (e.g., pgBackRest).

### Poison Messages (Dead Letter Queue)
If an event causes a continuous crash loop, the `ConsumerGroupSubscriber` tracks the `times_delivered`. If `delivery_count > EVENT_MAX_RETRIES` (default: 3), the event is:
1. Removed from the primary topic.
2. Pushed to `tip.events.dlq` (Dead Letter Queue) for manual inspection.
3. Acknowledged (`xack`) to unblock the pipeline.
