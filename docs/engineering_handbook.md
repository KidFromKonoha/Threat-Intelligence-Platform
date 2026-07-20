# Engineering Standards & Development Handbook v1.0

Welcome to the Threat Intelligence Platform (TIP) engineering team. This handbook is the authoritative reference for all development after Architecture v1.0. It defines our conventions, standards, and guardrails.

This document exists to ensure that multiple engineers can contribute to the platform concurrently without introducing architectural drift, spaghetti code, or operational regressions.

---

## 1. Engineering Philosophy

We build enterprise-grade software. Our guiding principles are:

1. **Simplicity over cleverness:** Code is read 10x more than it is written. Write boring, predictable, and readable code.
2. **Explicit over implicit:** Avoid magic. Do not use complex metaprogramming if a simple function suffices. 
3. **Event-driven by default:** Background work must be asynchronous and decoupled using Redis Streams. No synchronous blocking operations.
4. **Backend owns business logic:** The frontend is strictly a visual read-model. It must never calculate risk scores, deduce relationships, or filter data that the backend should have pre-processed.
5. **Idempotency first:** Every background worker and event consumer must be safely restartable. Processing the same event twice must result in the exact same database state.
6. **Observability by design:** If it isn't logged and tracked with Prometheus metrics and correlation IDs, it isn't production-ready.
7. **Production-first mindset:** Assume the database will drop connections, Redis will restart, and the network will partition. Design for failure.

---

## 2. Repository Organization

Our monorepo is structured by domain and architectural boundary.

- `backend/`: Python FastAPI application and background workers.
  - `app/core/`: Shared infrastructure (logging, configuration, event bus, base schemas).
  - `app/db/`: SQLAlchemy setup, base models, and session management.
  - `app/features/`: Vertical slices containing business domains (e.g., `feeds`, `enrichment`, `watchlists`).
- `frontend/`: React single-page application (SPA).
  - `src/features/`: Domain-specific UI components and hooks.
  - `src/components/`: Reusable, generic UI components (buttons, modals).
- `docs/`: Architectural Decision Records (ADRs), runbooks, and engineering guides.
- `scripts/`: Standalone python workers, load testing scripts, and seed data utilities.
- `alembic/`: Database migration scripts.
- `docker/`: Dockerfiles and compose setups for local development and CI.

---

## 3. Backend Development Standards

- **Feature Organization:** Use Vertical Slice Architecture. Keep routers, models, schemas, and services for a domain co-located within `app/features/{domain}/`.
- **Service Classes:** Services should contain pure business logic.
- **Dependency Injection:** Inject `SessionLocal` and `RedisEventBus` into service methods. Do not instantiate them globally inside the service class.
- **SQLAlchemy Usage:** Use `selectinload` to prevent N+1 queries. Separate database models (`models.py`) from Pydantic validation schemas (`schemas.py`).
- **Transaction Management:** Bulk operations must use `ON CONFLICT DO UPDATE`. Ensure `db.commit()` is called only when the logical transaction is complete.
- **Logging:** Use the centralized `configure_logging()` setup. Use `logger.exception()` to automatically attach stack traces in exception blocks.

---

## 4. Frontend Standards

- **React Architecture:** Use functional components and React Hooks exclusively. No class components.
- **TanStack Query:** Use React Query for all server state. Never use `useEffect` for data fetching. Abstract query keys into centralized factory objects.
- **Routing:** Use React Router. Implement strict route protection and lazy loading for heavy graph visualizers.
- **State Management:** Use Zustand for lightweight global state (e.g., theme, selected indicator). Avoid Redux.
- **Graph Visualization:** React Flow handles all relationship graphs. Separate data parsing from rendering.
- **Styling:** Use standard CSS or Tailwind. Avoid deep inline styles. Keep a consistent theme variable file.

---

## 5. Event Bus Standards

The platform relies on Redis Streams and Consumer Groups.

- **Event Naming:** Use `domain.entity.action` (e.g., `tip.events.indicator.persisted`, `tip.events.risk_score.calculated`).
- **Payload Design:** Must use the standardized `EventEnvelope` Pydantic schema.
- **Correlation IDs:** Every event must have a `correlation_id` (UUIDv4) that propagates to downstream events.
- **Consumer Responsibilities:** Catch all exceptions, log with `exc_info=True`, and explicitly **raise** the exception to prevent premature `xack` (acknowledgment) and data loss.
- **Idempotency:** Consumers must use `ON CONFLICT DO UPDATE` or pre-check states to avoid duplicate processing.

**Example Event Envelope:**
```json
{
  "event_id": "uuid-v4",
  "event_version": "1.0",
  "occurred_at": "2026-07-15T10:00:00Z",
  "producer": "enrichment_engine",
  "correlation_id": "trace-uuid-v4",
  "payload": {
    "indicator_id": "uuid-v4"
  }
}
```

---

## 6. Database Standards

- **Migrations:** All schema changes must be generated via Alembic (`alembic revision --autogenerate`). Never modify tables manually.
- **Indexing Strategy:** Every foreign key must have an index. Frequently filtered columns (e.g., `risk_score`) require B-Tree indexes.
- **UUID Usage:** Use UUIDv4 for all primary keys. Do not use auto-incrementing integers.
- **JSONB Usage:** Use JSONB for unstructured data (e.g., raw API responses in enrichment). Do not use JSONB to bypass proper relational modeling for core business entities.
- **Timestamps:** Every table must have `created_at` and `updated_at` (UTC timezone-aware).

---

## 7. API Standards

- **REST Conventions:** Follow standard HTTP semantics (`GET`, `POST`, `PUT`, `DELETE`).
- **Naming:** Use plural nouns (`/api/v1/indicators/{id}`).
- **Pagination:** Any collection returning >50 items must implement limit/offset pagination.
- **Validation:** Rely strictly on Pydantic schemas. 
- **Error Format:** Return structured JSON errors: `{"detail": "Reason", "code": "ERROR_CODE"}`.

---

## 8. Logging Standards

- **Structured Logging:** All logs must follow the `%(asctime)s | %(levelname)s | %(name)s | %(message)s` format.
- **Correlation IDs:** Always include `[Correlation ID: <uuid>]` in log messages related to event processing.
- **Exception Logging:** Always re-raise exceptions in background workers after logging to avoid breaking Consumer Group PEL (Pending Entries List) tracking.

---

## 9. Testing Standards

- **Unit Tests:** Business logic (rule engines, scoring formulas) must have 100% test coverage using Pytest. Mock external dependencies.
- **Integration Tests:** Test database queries against an ephemeral test database. Do not mock SQLAlchemy.
- **Event-Driven Tests:** Verify that workers publish correct events when processing valid inputs.
- **Load Tests:** Use synthetic generation scripts (`load_test_100k.py`) to verify system throughput prior to major releases.

---

## 10. Performance Standards

- **API Latency:** 95th percentile (p95) latency for read endpoints must be < 200ms.
- **Worker Throughput:** The Watchlist and Scoring engines must process > 100 events/sec on a single thread.
- **Dashboard Load Time:** Initial render < 1.5 seconds.
- **Query Limits:** No full table sequential scans in production. Always verify execution plans using `EXPLAIN ANALYZE`.

---

## 11. Security Standards

- **Authentication:** Use JWT tokens for API access.
- **Secrets Management:** Never hardcode secrets. Use `.env` files and strictly validate them on startup via Pydantic `BaseSettings`.
- **SQL Injection:** Never use raw string interpolation for SQL. Use SQLAlchemy's parameterized queries exclusively.
- **Dependency Scanning:** Keep `requirements.txt` and `package.json` updated. Audit dependencies regularly.

---

## 12. Documentation Standards

- **ADRs (Architecture Decision Records):** Any new architectural pattern, library introduction, or database schema refactor must be documented in `docs/adr/`.
- **API Documentation:** Keep FastAPI auto-generated OpenAPI schemas updated via correct Pydantic models.
- **README:** Must contain explicit instructions to run the stack via `docker compose up`.

---

## 13. Git Workflow

- **Branching:** Use Trunk-Based Development. Feature branches branch off `main` and merge back into `main`.
- **Commit Format:** Use Conventional Commits (`feat:`, `fix:`, `chore:`, `refactor:`).
- **Pull Requests:** Must be small, focused, and reviewed by at least one peer.
- **Merge Policy:** Squash and merge. Ensure a clean, linear git history.

---

## 14. Code Review Checklist

Before approving a PR, reviewers MUST verify:
- [ ] **Architecture:** Does this violate Architecture v1.0 constraints (e.g., frontend calculating data)?
- [ ] **Idempotency:** Is the worker safe to retry if it fails halfway?
- [ ] **Database:** Are there missing indexes? Is there an N+1 query vulnerability?
- [ ] **Logging:** Are errors caught and logged properly with a stack trace?
- [ ] **Testing:** Does this PR include relevant tests?
- [ ] **Documentation:** Does this change require an ADR or README update?

---

## 15. Architecture Guardrails

Architecture v1.0 is frozen. Do not violate these principles:
- **Collectors NEVER enrich.** (They only normalize and store).
- **Enrichment NEVER scores.** (It only queries external APIs and saves results).
- **Scoring NEVER calls external APIs.** (It relies solely on persisted graph data).
- **APIs NEVER calculate intelligence.** (APIs are Read Models querying pre-calculated data).
- **Frontend NEVER contains business rules.** (It is a pure visualization layer).
- **Every dashboard visualization MUST originate from persisted data.**

---

## 16. Engineering Decision Matrix

This matrix is the default decision guide for building new capabilities. Follow these defaults unless an Architectural Decision Record (ADR) explicitly overrides them.

| Situation | Preferred Solution |
| :--- | :--- |
| User request | REST API |
| Background work | Redis Event Bus |
| Long-running processing | Worker |
| Business rules | Backend Service |
| External APIs | Enrichment Providers |
| Relationship creation | Relationship Engine |
| Risk calculation | Scoring Engine |
| Visualization | Frontend |
| Persistent state | PostgreSQL |
| Temporary coordination | Redis |
| Configuration | Pydantic Settings |
| Analytics | Read Models |

---

## 17. ADR Template

Every architectural change after v1.0 must be documented using this standard Architecture Decision Record (ADR) template:

```markdown
# ADR [Number]: [Title]

**Status:** [Proposed | Accepted | Rejected | Superseded]  
**Date:** [YYYY-MM-DD]  
**Owner:** [Name/Team]  

## Context
[What is the problem or situation that requires a decision?]

## Decision
[What is the change that we are making?]

## Alternatives Considered
[What other options did we evaluate, and why were they rejected?]

## Trade-offs
[What are the pros and cons of this decision?]

## Consequences
[What becomes easier or more difficult because of this change?]

## References
[Links to related documents, PRs, or external resources]
```

---

## 18. Non-Functional Requirements (NFR)

These are measurable engineering targets used as objectives during production validation and load testing. All services must be engineered to support these baselines:

- **API p95 latency:** < 200 ms
- **Dashboard initial load:** < 2 seconds
- **Worker throughput:** > 100 events/sec/thread
- **Event propagation:** < 30 seconds
- **Availability target:** 99.9%
- **PostgreSQL CPU target:** < 70%
- **Redis consumer lag target:** < 5,000 events
- **RTO (Recovery Time Objective):** < 15 minutes
- **RPO (Recovery Point Objective):** < 1 minute

---

## 19. Engineering Roadmap

### Immediate Improvements
- Implement strict `pre-commit` hooks for Python `ruff` and JS `eslint`.
- Consolidate background worker setup code into a **Worker Runtime Library** based on composition rather than deep inheritance.
  - Suggested structure:
    ```text
    app/core/worker_runtime/
        consumer.py
        lifecycle.py
        metrics.py
        retry.py
        logging.py
        signal_handler.py
        health.py
    ```
  - **Philosophy:** Use composition to build workers (e.g., attach a `metrics` module and a `signal_handler` to a `consumer`) instead of forcing all workers to inherit from a rigid `WorkerManager` base class.

### Short-Term Improvements
- Integrate GitHub Actions for automated Pytest pipelines.
- Implement central Error Boundaries in the React frontend.

### Medium-Term Improvements
- Migrate query keys in TanStack Query to central factory objects.

### Architecture v2.0 Candidates
- **Distributed Tracing:** Full integration of OpenTelemetry for cross-service Jaeger/Zipkin tracing.
- **Transactional Outbox Pattern:** Implement exactly-once publication between PostgreSQL and Redis Streams.
  - Outbox relay worker.
  - Event replay tooling.
  - Idempotent publisher guarantees.
- **Modular Monolith Evolution:** Continue evolving the Modular Monolith until independent deployment boundaries become a measurable operational necessity.
  - Introduce service extraction only when operational metrics justify it (independent scaling, deployment cadence, team ownership, or technology divergence).
  - Do not recommend microservices as the default future.
