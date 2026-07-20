# Testing & Validation Handbook v1.0

This document is the official testing and validation standard for the Threat Intelligence Platform (TIP). It complements the Engineering Standards & Development Handbook. Our goal is to ensure unshakeable confidence in our production systems through rigorous automated and manual validation.

---

## 1. Testing Philosophy

- **Pyramid of Tests:** Favor a strong foundation of fast, isolated unit tests. Use integration tests for database/bus boundaries, and sparingly use end-to-end (E2E) tests for critical user journeys.
- **Fast Feedback:** Unit and integration tests must run in seconds, not minutes. 
- **Deterministic Tests:** Tests must yield the exact same result regardless of the order they run in, the time of day, or the underlying hardware.
- **No Flaky Tests:** A flaky test is worse than no test. If a test fails intermittently, it must be fixed or deleted immediately.
- **Regression Accountability:** Every bug discovered in production must result in a new automated regression test before the fix is merged.

---

## 2. Required Test Types

Every new feature or major refactor must include the following test coverage.

### Backend

- **Unit Tests:** Must cover 100% of pure business logic (e.g., rule evaluators, scoring formulas). Mock all external I/O (database, Redis, HTTP clients).
- **Integration Tests:** Must verify database repositories and SQL queries. Use an ephemeral test database (e.g., Testcontainers). Do NOT mock SQLAlchemy.
- **API Tests:** Use `TestClient` to verify HTTP contracts, status codes, and Pydantic validation boundaries.
- **Event Bus Tests:** Verify that producers construct and serialize correct `EventEnvelope` payloads. Verify that consumers correctly route deserialized payloads.
- **Worker Tests:** Verify that worker processes start, gracefully handle OS signals, and correctly invoke consumer logic.

### Frontend

- **Component Tests:** Verify rendering and local state for isolated UI components using React Testing Library.
- **Routing Tests:** Verify that navigation triggers correct component mounting and lazy-loading boundaries.
- **API Integration Tests:** Mock `fetch` or use MSW (Mock Service Worker) to verify that TanStack Query correctly handles loading, error, and success states.

### Performance

- **Load Tests:** High-volume ingestion testing (e.g., 100k events) to measure synchronous pipeline throughput.
- **Stress Tests:** Direct injection (e.g., 1M events via Redis) to measure absolute worker limits and queue saturation limits.
- **Soak Tests:** Extended duration testing to identify memory leaks, unclosed database sessions, or connection pool exhaustion.

### Reliability

- **Chaos Tests:** Deliberately terminating infrastructure (PostgreSQL, Redis, Workers) to verify recovery mechanisms.
- **Recovery Tests:** Verifying that data in the Redis Pending Entries List (PEL) is correctly auto-claimed and processed after an outage.

---

## 3. Manual Verification Checklist

Before considering any milestone functionally complete, engineers must manually verify:

- [ ] **API endpoints:** Test Happy Path, 400 Bad Request, and 404 Not Found scenarios.
- [ ] **Database state:** Inspect tables directly to ensure data constraints, timestamps, and relationships are correct.
- [ ] **Redis Streams:** Run `XRANGE` to verify events are emitted with the correct `EventEnvelope` schema.
- [ ] **Consumer Groups:** Run `XINFO GROUPS` to ensure workers are actively consuming and acknowledging messages.
- [ ] **Prometheus metrics:** Curl `/metrics` to ensure counters and latency summaries increment correctly.
- [ ] **Logs:** Verify structured logs display appropriate correlation IDs and no silent errors.
- [ ] **Docker containers:** Ensure `docker compose up` accurately boots the entire stack without crashing.
- [ ] **Frontend functionality:** Navigate the UI to ensure backend integration completes the feedback loop.
- [ ] **Duplicate event replay:** Inject the exact same event twice and verify idempotency (zero duplicated database rows).
- [ ] **Worker restart recovery:** Restart a worker mid-processing to verify it resumes from the PEL.
- [ ] **Database restart recovery:** Restart PostgreSQL to verify workers catch `OperationalError`, reconnect, and do not drop events.

---

## 4. Performance Validation

Engineers are required to validate performance against the Non-Functional Requirements (NFRs). Document measurements using the following tools:

- **EXPLAIN ANALYZE:** Run on every new database query. Expected threshold: No sequential scans for production tables. Index hits are mandatory.
- **Redis XLEN:** Measures the total size of the stream.
- **Redis XPENDING:** Measures messages delivered to consumers but not yet acknowledged (PEL). Expected threshold: Must drain to 0 under normal operation.
- **Redis XINFO GROUPS:** Measures consumer lag (`lag`). Expected threshold: Lag must stay below 5,000 events.
- **Docker stats:** Measures hardware utilization per container.
- **CPU:** Worker CPU utilization must remain stable. Expected threshold: PostgreSQL < 70%.
- **Memory:** Watch for unbounded growth indicating leaks.
- **Throughput:** Calculate via Prometheus `rate()` queries or load test outputs. Expected threshold: > 100 events/sec/thread.
- **Latency:** Calculate via Prometheus summaries or API benchmarks. Expected threshold: p95 API latency < 200 ms.

---

## 5. Production Readiness Checklist

Before merging any milestone into the `main` branch, ensure:

- [ ] Architecture remains strictly unchanged (v1.0 constraints preserved).
- [ ] All automated tests are passing.
- [ ] No N+1 queries exist in the codebase.
- [ ] No sequential scans exist on high-volume tables.
- [ ] All workers and event consumers are strictly idempotent.
- [ ] Correlation IDs are preserved and propagated across all boundaries.
- [ ] Structured logging is properly implemented.
- [ ] Prometheus metrics exist for throughput, errors, and latency.
- [ ] A `/health` endpoint is available and accurate.
- [ ] Documentation (Runbooks, README, API Docs) is updated.
- [ ] An Architectural Decision Record (ADR) is written and approved if any architectural boundary was modified.

---

## 6. Failure Injection Checklist

Engineers must intentionally destabilize the platform to verify self-healing mechanics. Verify the expected system behavior for the following scenarios:

- **Redis restart:** Workers should fail to connect, enter an exponential backoff loop, and reconnect without crashing the process.
- **PostgreSQL restart:** Workers should catch `OperationalError`, log the failure, **raise** the exception to avoid `xack`, and wait for the database to return.
- **Worker crash:** The orchestrator (Docker/K8s) should restart the container. Unacknowledged messages must remain in the PEL for auto-claiming.
- **Duplicate events:** Inject the identical payload twice. The system must use `ON CONFLICT DO UPDATE` or equivalent logic to prevent duplicate state.
- **Poison messages:** Inject malformed JSON. The consumer must log the deserialization error, acknowledge the message to unblock the queue, and optionally route it to a DLQ (`tip.events.dlq`).
- **Network failure:** Ensure HTTP timeouts on enrichment providers trigger backoffs, not catastrophic pipeline failures.
- **Large backlog:** Pre-load Redis with 1,000,000 events. Spin up workers and verify they can chew through the backlog without OOM (Out Of Memory) crashing.
- **Empty queues:** Workers must sleep efficiently without consuming 100% CPU while polling.

---

## 7. Benchmark Recording Template

When submitting a performance milestone or load test report, use this exact markdown template to ensure standardization:

```markdown
# Benchmark Report: [Feature/Test Name]

**Date:** YYYY-MM-DD
**Engineer:** [Name]

## Environment
- **Hardware:** [e.g., 8-core M1 Mac, 32GB RAM / AWS t3.xlarge]
- **Docker version:** [e.g., 24.0.2]
- **PostgreSQL version:** [e.g., 16.2]
- **Redis version:** [e.g., 7.2]

## Parameters
- **Dataset size:** [e.g., 1,000,000 synthetic events]
- **Concurrency:** [e.g., 1 HTTP client, 4 worker processes]

## Results
- **Throughput:** [e.g., 47,000 msgs/sec injection, 250 evals/sec processing]
- **Latency:** [e.g., p95 120ms]
- **Memory (Peak):** [e.g., Worker: 120MB, Postgres: 500MB]
- **CPU (Peak):** [e.g., Worker: 95%, Postgres: 40%]

## Analysis
- **Observations:** [What behavior was notable?]
- **Bottlenecks:** [Where did the system choke? e.g., Network I/O, DB CPU]

## Screenshots
[Attach Prometheus graphs or docker stats outputs here]
```

---

## 8. Definition of Done (DoD)

A feature, user story, or milestone is **NOT complete** until absolutely all of the following conditions are satisfied:

1. **Code implemented:** The business requirements are met.
2. **Tests written:** Unit and Integration tests are implemented and passing.
3. **Manual verification completed:** The Manual Verification Checklist (Section 3) is checked off.
4. **Performance validated:** The Performance Validation (Section 4) and benchmarks are recorded.
5. **Documentation updated:** Handbooks, APIs, and ADRs are current.
6. **Metrics exposed:** Relevant Prometheus metrics (counters, summaries) are instrumented.
7. **Logging added:** Structured logging with correlation IDs is active.
8. **Health checks updated:** Any new dependencies are added to the health endpoints.
9. **PR checklist completed:** The pull request meets all repository quality standards.
