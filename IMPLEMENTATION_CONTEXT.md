# Implementation Context

This file captures what was actually implemented, to give future phases the
minimum context needed without re-reading README.md / SPEC.md in full.

---

## Folder Structure

```
backend/
  app/
    main.py                  # FastAPI app instance, CORS, router mounting
    api_v1.py                 # Aggregates all feature routers under /api/v1
    core/
      config.py               # Settings (env-driven), DATABASE_URL/REDIS_URL/CELERY_* properties
      logging.py               # configure_logging() / get_logger()
      redis.py                 # get_redis_client() singleton
      celery_app.py            # Celery app, autodiscovers app.features.*.tasks
    db/
      session.py               # engine, SessionLocal, Base (DeclarativeBase), get_db()
    features/
      health/
        router.py              # GET /health -> DB + Redis check
        schemas.py              # HealthResponse, ServiceStatus
      <future feature>/
        router.py
        schemas.py
        models.py               # (not yet present — add when first entity is implemented)
        service.py               # (not yet present — business logic layer convention)
        tasks.py                 # (not yet present — Celery tasks for that feature)
  alembic/
    env.py                     # imports Base from app.db.session; import feature models here as added
    script.py.mako
  alembic.ini
  requirements.txt
  Dockerfile
  .env.example

frontend/
  src/
    app/
      router.tsx                # createBrowserRouter, route tree root
      query-client.ts            # TanStack QueryClient instance
    components/
      layout/app-layout.tsx      # Header + Outlet shell, dark mode toggle
      ui/                        # shadcn-style primitives (button.tsx, card.tsx so far)
    features/
      health/use-health.ts       # TanStack Query hook per feature, mirrors backend features/
    hooks/use-theme.ts           # dark mode via .dark class on <html>, localStorage-persisted
    lib/
      api-client.ts              # API_BASE_URL, apiGet<T>()
      utils.ts                   # cn() className merge helper
    routes/dashboard-page.tsx    # first route page (health/status dashboard)
    main.tsx / App.tsx
  vite.config.ts                 # @tailwindcss/vite plugin, "@" -> ./src alias
  .env.example
  Dockerfile

infrastructure/
  docker-compose.yml             # postgres, redis, backend, frontend
```

**Convention going forward:** each backend feature is a self-contained package
under `app/features/<feature>/` with `router.py`, `schemas.py`, and (once
needed) `models.py`, `service.py`, `tasks.py`. Each frontend feature lives
under `src/features/<feature>/` with its TanStack Query hooks and types,
matching the backend feature name 1:1.

---

## Libraries Chosen

**Backend:** FastAPI, Pydantic v2 + pydantic-settings, SQLAlchemy 2.0 (declarative,
`DeclarativeBase`), Alembic, psycopg2-binary (sync driver), redis-py, Celery
(Redis as both broker and result backend — no separate broker chosen), uvicorn.

**Frontend:** Vite, React 19, TypeScript, **Tailwind CSS v4** (via `@tailwindcss/vite`
plugin — no `tailwind.config.js`/PostCSS config; theming done via CSS
`@theme inline` + CSS variables in `src/index.css`), shadcn/ui-style components
built manually (`class-variance-authority`, `clsx`, `tailwind-merge`,
`@radix-ui/react-slot`, `lucide-react` icons) rather than via the shadcn CLI,
React Router v6 (`createBrowserRouter`), TanStack Query v5.

---

## Architectural Decisions Actually Implemented

- **Sync SQLAlchemy** (not async) — simplest path for Phase 1; revisit only if
  a future phase has a concrete need for async DB access.
- **DB session per request** via FastAPI `Depends(get_db)`, not a context var
  or middleware.
- **Settings are a singleton** (`app.core.config.settings`, `lru_cache`-backed
  `get_settings()`), read once from environment / `.env`.
- **Redis client is a lazy singleton** (`get_redis_client()`), not injected via
  FastAPI `Depends`.
- **Celery autodiscovers tasks** from `app.features.*.tasks` — when a feature
  adds background jobs, just add `tasks.py` in that feature package; no
  registration needed elsewhere.
- **Health endpoint** (`GET /api/v1/health`) checks DB via `SELECT 1` and Redis
  via `PING`, returns `"ok"` only if both succeed, otherwise `"degraded"` with
  per-service `status`/`detail` — it does not raise/500 on dependency failure.
- **Dark mode** implemented via a `.dark` class toggled on `<html>` (Tailwind
  v4 `@custom-variant dark`), state in `localStorage` under key `tip-theme`,
  no external theme library.
- **API base URL** is injected via `VITE_API_BASE_URL` (frontend `.env`),
  defaulting to `http://localhost:8000/api/v1` for local dev outside Docker.
- **CORS** origins are configured via `BACKEND_CORS_ORIGINS` in backend settings,
  defaulting to `http://localhost:5173`.
- Docker Compose **mounts source as volumes** for both services (hot reload in
  dev); not a production-optimized multi-stage build yet.
- No authentication, RBAC, models, or business endpoints exist yet — explicitly
  deferred to later phases per TASK.md Phase 1 scope.

---

## Important Conventions

- Backend route prefix: every feature router is mounted under `/api/v1` via
  `app/api_v1.py`; an individual feature's router itself only declares its own
  sub-prefix (e.g. `/health`).
- Backend feature folder = frontend feature folder, same name, for easy
  cross-referencing.
- All cross-cutting backend code (config, logging, db, redis, celery) lives in
  `app/core/` or `app/db/`, never duplicated inside a feature.
- Frontend path alias `@/` always resolves to `frontend/src/`.
- Env var templates are committed as `.env.example` in both `backend/` and
  `frontend/`; real `.env` files are gitignored.

---

## Commands to Run the Project

**Via Docker Compose (recommended):**
```bash
cd infrastructure
docker compose up --build
```
- Backend: http://localhost:8000/api/v1/health, docs at http://localhost:8000/api/v1/docs
- Frontend: http://localhost:5173

**Backend locally (without Docker):**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # adjust POSTGRES_HOST/REDIS_HOST to localhost if running services locally
uvicorn app.main:app --reload
```

**Frontend locally (without Docker):**
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

**Alembic (run from `backend/`, once models exist):**
```bash
alembic revision --autogenerate -m "message"
alembic upgrade head
```

---

## Phase 2 — Database Foundation

### New Files

```
backend/
  app/
    db/
      enums.py          # All shared enum classes (IndicatorType, Severity, FeedStatus, …)
      mixins.py         # TimestampMixin — created_at / updated_at with server_default=func.now()
      associations.py   # All many-to-many join Table objects (no ORM classes)
    features/
      indicators/
        models.py       # Indicator
      threat_actors/
        models.py       # ThreatActor
      malware/
        models.py       # Malware
      campaigns/
        models.py       # Campaign
      vulnerabilities/
        models.py       # Vulnerability
      mitre/
        models.py       # MITRETechnique
      feeds/
        models.py       # Feed, FeedRun
      assets/
        models.py       # Asset
      investigations/
        models.py       # Investigation
      watchlists/
        models.py       # Watchlist
      reports/
        models.py       # Report, Comment
  alembic/
    versions/
      6d4d4982970a_database_foundation.py   # Single migration for all Phase 2 tables
```

### Architectural Decisions

- **String-backed enums** — All enum columns use `String(N)` + Python `str(enum.Enum)`
  values rather than PostgreSQL native ENUM types.  Adding new enum values never
  requires a DDL migration.

- **UUID as Text** — Primary keys are `Text` with
  `server_default=text("gen_random_uuid()::text")`.  PostgreSQL's
  `pgcrypto` / built-in `gen_random_uuid()` generates the value; the application
  layer never needs to import `uuid`.  No separate `pgcrypto` extension is needed
  on PostgreSQL ≥ 13.

- **Centralized associations** — All `Table` join objects live in
  `app/db/associations.py` and are imported before any feature model.  This
  prevents circular imports and keeps the full relationship graph reviewable in
  one file.

- **Centralized enums** — All enum classes live in `app/db/enums.py`.  Feature
  models import from there, not from each other.

- **TimestampMixin** — Defined in `app/db/mixins.py`.  `MITRETechnique` and
  `FeedRun` intentionally do not use it: MITRE data is static reference data;
  `FeedRun` uses `start_time`/`end_time` instead.

- **Comment polymorphism** — `Comment` uses two nullable FKs
  (`investigation_id`, `report_id`) rather than a generic polymorphic
  association table.  Only one FK is populated per row.  This keeps Phase 2
  simple and avoids premature abstraction; a generic entity-reference pattern
  can be introduced in a future phase if needed.

- **No new dependencies** — Phase 2 introduces no new Python packages.
  All required types (`ARRAY`, `JSON`, `DateTime`, etc.) are already available
  via the existing SQLAlchemy 2.0 installation.

### Model Bootstrap Convention (`app/db/__init__.py`)

**Architectural change applied during Phase 3A verification.**

`app/db/__init__.py` now imports all association tables and all feature ORM
models in a fixed order:

1. `app.db.associations` — registers every `Table` object on `Base.metadata`.
2. All `app.features.<feature>.models` modules — registers every mapped class.

**Why this is necessary:**

SQLAlchemy resolves `relationship(secondary="table_name")` and
`relationship("ClassName")` string arguments at mapper-configuration time,
which is triggered the moment any mapped class is first used in a query.
At that point, SQLAlchemy configures **all** mappers in the registry
simultaneously.  If any referenced `Table` object or ORM class has not yet
been imported, the process raises:

```
InvalidRequestError: expression '<name>' failed to locate a name
```

**Why `app/db/__init__.py` is the right place:**

Every entrypoint (uvicorn, Celery worker, `alembic`, shell scripts) imports
at least one symbol from `app.db` before issuing any query.  Placing the
bootstrap here means the mapper graph is always fully populated, regardless
of which feature model is imported first or which entrypoint is used.
No individual feature module needs to import models from other features.

**When adding a new model in a future phase:**
Add `import app.features.<new_feature>.models` to `app/db/__init__.py`
(in alphabetical order).  Also add it to `alembic/env.py` as before
(required for `alembic autogenerate` to detect the new tables).

---

## Phase 3A — Feed Collection Framework

### New Files

```
backend/
  app/
    features/
      feeds/
        schemas.py           # RawIndicator schema, CollectorMetrics
        base_collector.py    # BaseCollector abstract base class, CollectorConfig
        registry.py          # CollectorRegistry singleton (decorator registration, auto-discovery)
        pipeline.py          # ValidationPipeline, NormalizationPipeline, StoragePipeline
        runner.py            # FeedRunner (timing, logs, back-off retry logic, DB transactional integrity)
        scheduler.py         # FeedScheduler — cron-based dispatch abstraction; scheduler singleton
        tasks.py             # Celery tasks: feeds.run_collector + feeds.tick_scheduler
        collectors/
          __init__.py        # Auto-discovery hook
          dummy.py           # DummyCollector (simulated feed generating synthetic IOCs)
```

### Architectural Decisions

- **Decorator-Based Autodiscovery (`@registry.register`)** — Collectors register themselves dynamically by subclassing `BaseCollector` and applying the registry decorator. The framework imports everything under `collectors/` at startup to build the registry without modification to any core code.
- **Decoupled Pipelines** — Validation (pre-filtering), Normalization (parsing to schema), and Storage are split into independent pipeline classes. Collectors only implement target logic (`fetch`, `validate`, `normalize`), while the framework handles the data ingestion process.
- **Upsert Deduplication with SQL Conflict Clauses** — The `StoragePipeline` uses PostgreSQL-native `on_conflict_do_update` based on `(type, normalized_value)` to perform upserts, tracking `source_count` increments and updating `last_seen` dynamically on duplicate hits.
- **Fail-safe Error Isolation** — Unhandled exceptions inside individual collectors are caught by the `FeedRunner` and logged to the running `FeedRun` entry without interrupting other scheduled collector tasks.
- **Exponential Back-off Retries** — Retries are handled within the framework's `FeedRunner` instead of Celery's task retries. This ensures execution details (e.g. tracking temporary failures, tracking run durations) are captured accurately under the single database `FeedRun` instance.
- **Timeout Enforcement via ThreadPoolExecutor** — `_fetch_with_retry` wraps each `fetch()` call in a `concurrent.futures.ThreadPoolExecutor`. `Future.result(timeout=config.timeout)` enforces the hard deadline. This is the correct approach for synchronous Python because `time.sleep()`-based timeouts cannot interrupt blocking I/O.
- **Scheduler Abstraction (`FeedScheduler`)** — `scheduler.py` provides a `FeedScheduler` class with a `tick()` method. `tick()` queries all enabled feeds, evaluates each feed's `schedule` cron string (using `croniter` when available, falling back to an hourly interval policy), and dispatches a `run_collector` Celery task for each feed that is due. The `feeds.tick_scheduler` Celery task calls `scheduler.tick()` and is configured in `celery_app.py`'s `beat_schedule` to fire every 60 seconds.

### Bug Fixes Applied During Phase 3A Review

- **`max_retries` conflation** (`runner.py`): The original code set `max_retries=feed.rate_limit or 3`, which conflated two unrelated concepts (`rate_limit` is requests-per-minute; `max_retries` is retry count). Fixed to always use `max_retries=3` (the `CollectorConfig` default) since `Feed` has no `max_retries` column.
- **Timeout not enforced** (`runner.py`): `config.timeout` was documented and passed around but `collector.fetch()` was called with no timeout wrapper. Fixed by wrapping each `fetch()` attempt in a `ThreadPoolExecutor` and using `Future.result(timeout=config.timeout)`.

---

## Phase 3B — ThreatFox Collector

### New Files

```
backend/
  app/
    features/
      feeds/
        collectors/
          threatfox.py   # ThreatFoxCollector — production abuse.ch ThreatFox collector
```

### Collector Overview

`ThreatFoxCollector` is a production-quality collector for the [ThreatFox](https://threatfox.abuse.ch) community API operated by abuse.ch.

**Registration:** `@registry.register` — auto-discovered at startup; no other file changes required.

**API:** `POST https://threatfox-api.abuse.ch/api/v1/` with `{"query": "get_iocs", "days": N}`.
Auth-Key is read from `Feed.authentication["api_key"]`. Anonymous access (no key) is supported with reduced rate limits.

**HTTP:** Uses Python stdlib `urllib.request` — no new runtime dependency.

### Field Mapping

| ThreatFox field | Platform field | Notes |
|---|---|---|
| `ioc` | `value` | raw indicator string |
| `ioc_type` | `type` | via `_IOC_TYPE_MAP` |
| `ioc` (bare IP) | `normalized_value` | ip:port → bare IP only (see below) |
| `confidence_level` | `confidence` | int 0–100 |
| `threat_type` | `severity` | botnet_cc/payload_delivery/payload_url → HIGH; others → MEDIUM |
| `first_seen` | `first_seen` | parsed from `"%Y-%m-%d %H:%M:%S UTC"` |
| `last_seen` | `last_seen` | null → falls back to `first_seen` |
| `tags` + `malware_printable` + `malware` + `threat_type` | `tags` | merged, deduplicated |
| full record | `raw` | preserved for auditing |

### Supported IOC Types

| ThreatFox `ioc_type` | Platform `IndicatorType` |
|---|---|
| `ip:port` | `IPV4` |
| `domain` | `DOMAIN` |
| `url` | `URL` |
| `md5_hash` | `MD5` |
| `sha1_hash` | `SHA1` |
| `sha256_hash` | `SHA256` |

All other `ioc_type` values are silently dropped in `validate()`.

### `ip:port` Deduplication Strategy

ThreatFox represents C2 servers as `"1.2.3.4:4444"`.  The same C2 IP may appear on multiple ports across different records.

- `value` = `"1.2.3.4:4444"` (analysts search this).
- `normalized_value` = `"1.2.3.4"` (deduplication key in `(type, normalized_value)` unique index).

This means a C2 IP that rotates ports is stored as one `Indicator` row with `source_count` incrementing and `last_seen` updating — not as a new row per port.

### No New Dependencies

`urllib.request` and `json` are Python stdlib.  `requests` was not added to `requirements.txt`.

### Database Setup

Run once per environment to activate the feed:

```sql
INSERT INTO feeds (name, description, type, enabled, status, schedule, authentication)
VALUES (
    'threatfox',
    'ThreatFox IOC feed by abuse.ch',
    'open_source',
    true,
    'active',
    '0 */6 * * *',
    '{"api_key": "YOUR_THREATFOX_API_KEY"}'::json
);
```

`api_key` is optional — omit it for anonymous access.
`days` in `authentication` overrides `_DEFAULT_DAYS = 1` (e.g. `{"api_key": "...", "days": 3}`).

### Manual Run

```bash
docker exec tip-backend python -c "
import app.db
from app.features.feeds.runner import FeedRunner
m = FeedRunner('threatfox').run()
print(m)
"
```

---

## Phase 4 — Feed Management API

### New Dependencies

- `croniter==2.0.5` added to `requirements.txt` to support cron schedule expression validation in Pydantic schemas.

### API Layer Structure

- **Schemas (`backend/app/features/feeds/schemas.py`)**: Added `FeedBase`, `FeedCreate`, `FeedUpdate`, `FeedResponse`, and `FeedRunResponse` Pydantic models. Includes field validation for the `schedule` field using `croniter.is_valid()`.
- **Service (`backend/app/features/feeds/service.py`)**: Added `FeedService` class encapsulating the business logic for standard CRUD operations and custom logic like triggering Celery task for feed runner. 
- **Router (`backend/app/features/feeds/router.py`)**: Added RESTful endpoints (`/feeds`, `/feeds/{id}`, etc.) delegating business operations to the `FeedService`. Registered under `backend/app/api_v1.py`.

### Architectural Decisions

- **Async Manual Execution**: Instead of running `FeedRunner` synchronously on the HTTP thread when `POST /feeds/{id}/run` is called, it triggers the existing Celery task `run_collector.delay()` and immediately returns a `202 Accepted` response. This prevents blocking API calls for long-running collector fetches.
- **Dynamic Feed Statistics**: Rather than adding/duplicating statistics columns directly to the `Feed` model, feed performance and execution metrics (such as total records added, total runs, last status) are computed dynamically from the `FeedRun` table and presented via a lightweight `GET /feeds/status` endpoint to optimize for operational dashboards.

---

## Phase 5 — Search API

### New Files

```
backend/app/db/
  text_match.py                          # MatchMode enum + apply_text_match() helper

backend/app/features/indicators/
  schemas.py                             # IndicatorFilters, IndicatorResponse, IndicatorDetailResponse, PaginatedIndicators
  service.py                             # IndicatorSearchService
  router.py                              # GET /indicators, GET /indicators/{id}

backend/app/features/search/
  __init__.py
  schemas.py                             # GlobalSearchResult, EntitySummary, IndicatorSummary
  service.py                             # GlobalSearchService
  router.py                              # GET /search

backend/alembic/versions/
  830382a8ded4_search_indexes.py         # Alembic migration: performance indexes
```

### Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/indicators` | Filtered, sorted, paginated indicator search |
| `GET` | `/api/v1/indicators/{id}` | Full indicator detail with related entities |
| `GET` | `/api/v1/search` | Global cross-entity keyword search |

### Architectural Decisions

- **Resource organization**: Indicator endpoints live in the `indicators` feature module. Global search lives in the `search` feature module. No cross-module leakage.
- **Composable filter pattern**: `IndicatorSearchService.search()` builds a `predicates: list = []` and appends conditions one by one. A single `.filter(*predicates)` call applies them all. No nested if/else query tree.
- **Flexible text matching**: `app/db/text_match.py` exports `MatchMode` (exact / prefix / contains) and `apply_text_match(column, value, mode)`. Adding a new mode requires changing only this helper. Callers pass `value_match: MatchMode` as a query parameter.
- **Relational filters via EXISTS**: `feed`, `malware`, `threat_actor`, and `campaign` filters use `exists(select(...).where(...))` subqueries against the association tables — never a JOIN — to prevent row multiplication when an indicator has multiple related entities.
- **Tags filter**: `type_coerce(Indicator.tags, PG_ARRAY(Text)).overlap(filters.tags)` uses PostgreSQL's `&&` array overlap operator. `type_coerce` is required because `Mapped[list]` (unparameterised) is used in the Phase 2 model, which prevents `.overlap()` from being available directly on the column attribute.
- **Global search**: `GlobalSearchService` runs one `ilike "%q%"` query per entity type (7 queries total), each capped at `limit` rows. No cross-table JOIN. Logs query term, per-entity hit counts, total hits, and wall-clock duration.
- **Detail endpoint & uselist=False gotcha**: Phase 2 `Indicator` model relationships use `Mapped[list]` (generic, unparameterised) — SQLAlchemy infers `uselist=False` for all of them, meaning each relationship returns a scalar ORM object or `None`, not a collection. The `_coerce_rel()` helper in `service.py` wraps scalar values in a list before building the response schema, so the API always returns `[]` or `[item]` arrays. This is documented as a known constraint; fixing it requires updating Phase 2 models (out of scope for Phase 5).
- **Alembic migration `830382a8ded4`**: Adds `ix_indicator_confidence`, `ix_indicator_source_count`, `ix_indicator_first_seen`, `ix_indicator_last_seen` — columns used for sorting and range filtering that were not previously indexed.

### Known Constraint

> The `Indicator.*` relationships (feeds, malware, threat_actors, etc.) are all `uselist=False` due to the unparameterised `Mapped[list]` type hint in the Phase 2 ORM models. Each relationship currently returns at most one related entity. Fixing this to return proper many-to-many collections requires parameterising the type hints (e.g. `Mapped[list["Feed"]]`) in the Phase 2 models — this is safe and non-breaking but out of scope for Phase 5.

---

## Phase 6 — Correlation Engine

### New Files

```
backend/app/features/correlation/
  __init__.py
  schemas.py    # IndicatorAnchor, entity Ref schemas, RelationshipsResponse, RelatedIndicatorsResponse
  service.py    # CorrelationService
  router.py     # GET /indicators/{id}/relationships, GET /indicators/{id}/related
```

### Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/indicators/{id}/relationships` | Full relationship graph for one indicator |
| `GET` | `/api/v1/indicators/{id}/related` | Ranked similar indicators by shared entities |

### Architectural Decisions

- **Dedicated feature package**: `app/features/correlation/` owns all correlation logic. No changes to existing phases. The router is mounted on the `/indicators` prefix (same as the Phase 5 indicators router) so the URLs are `GET /indicators/{id}/relationships` and `GET /indicators/{id}/related`.

- **`get_relationships()` — N+1-free loading**: The anchor indicator is fetched once with `selectinload` for all 6 relationship types (feeds, malware, campaigns, threat_actors, techniques, reports). Vulnerabilities are not stored directly on `Indicator`; they are reached via the indicator's campaigns. A second batch `selectinload(Campaign.vulnerabilities)` is issued only when the indicator has campaigns, keeping the total to at most 2 SELECT IN queries for this case.

- **`get_related_indicators()` — single candidate query**: Related indicators are discovered with one SQL query using `OR`'d `EXISTS` subqueries — one per relationship category (malware, campaigns, threat_actors, reports, feeds). The candidates are loaded with `selectinload` for the same 5 categories so all scoring data is in memory. Scoring (shared_count) and SharedContext construction happen in Python in one pass — zero extra DB queries.

- **`_coerce_rel()` re-implemented locally as `_coerce()`**: Phase 2 models use unparameterised `Mapped[list]`, causing SQLAlchemy to infer `uselist=False`. The correlation service normalises every relationship attribute to a list via `_coerce()` before iteration, mirroring the pattern established in Phase 5.

- **Ranking**: Results from `get_related_indicators()` are sorted by `shared_count` descending in Python after scoring. `limit` (1–100, default 25) is applied after sorting.

- **`SharedContext`**: The response includes a `shared_context` object per related indicator that lists the *names* (not just IDs) of each shared entity category. This is resolved from already-in-memory selectinload data — no extra queries.

- **Logging**: Both service methods log correlation request ID, per-category counts (for relationships) or candidate/returned counts (for related), and wall-clock duration.

### Known Constraint (inherited from Phase 5)

> The `uselist=False` gotcha documented in Phase 5 applies here too. The `_coerce()` helper handles it consistently throughout the service. Real fix requires updating Phase 2 model type hints — out of scope.

---

## Phase 7 — Intelligence Enrichment

### New Files

```
backend/app/features/enrichment/
  __init__.py
  models.py       # EnrichmentResult
  provider_base.py# BaseEnrichmentProvider, EnrichmentResultData
  registry.py     # EnrichmentProviderRegistry (decorator @enrichment_registry.register)
  schemas.py      # EnrichmentSummary, EnrichmentStatusResponse
  service.py      # EnrichmentService
  tasks.py        # Celery task run_enrichment
  router.py       # POST /indicators/{id}/enrich, GET /indicators/{id}/enrichment
  providers/
    __init__.py
    dummy.py      # DummyEnrichmentProvider
backend/alembic/versions/
  ea271c0b7cde_enrichment_engine.py  # Migration for enrichment_results table
```

### Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/indicators/{id}/enrich` | Dispatches an asynchronous celery task for enrichment. Returns HTTP 202 Accepted. |
| `GET` | `/api/v1/indicators/{id}/enrichment` | Returns execution history and status from all providers that ran for this indicator. |

### Architectural Decisions

- **Provider Architecture**: Enrichment is structured as an extensible provider framework. Each provider must subclass `BaseEnrichmentProvider`, define its `provider_name` and `supported_indicator_types`, and implement `enrich()`. This mimics the Phase 3A collector framework for straightforward extension.
- **Auto-Discovery Registry**: The `EnrichmentProviderRegistry` uses a class decorator (`@enrichment_registry.register`) and `pkgutil.iter_modules` to dynamically load and register providers in `providers/` without hardcoded imports.
- **Asynchronous Execution via Celery**: The `POST /enrich` endpoint is non-blocking. It calls `run_enrichment.delay(indicator_id)`, which runs synchronously inside a Celery worker.
- **Independent Provider Execution**: `EnrichmentService.run_enrichment_sync()` iterates through all registered providers that support the indicator's type. It wraps each provider execution in a `try...except` block, ensuring that if one provider fails (e.g., timeout or bad response), it records the failure in the database and proceeds to the next provider. No provider can break the workflow.
- **Zero Coupling with Core Models**: `EnrichmentResult` has a foreign key to `indicators.id`, but no `back_populates` was added to `Indicator`. This conforms to the non-goal of modifying existing models unnecessarily and avoids bloated JOIN queries when querying indicators.
- **State Transition Logging**: An `EnrichmentResult` is created in `PENDING` state right before a provider executes. Upon completion, the row is updated to either `SUCCESS` or `FAILED` alongside the elapsed duration. This ensures visibility even if a worker crashes mid-execution.

## Phase 9 — Dashboard API

### New Files

```
backend/app/features/dashboard/
  __init__.py
  router.py
  schemas.py
  service.py
```

### API Layer Structure

- **Schemas (`backend/app/features/dashboard/schemas.py`)**: Defined aggregate Pydantic schemas for overview metrics, threat activity statistics, organizational matching, feed status, and recent intelligence summaries.
- **Service (`backend/app/features/dashboard/service.py`)**: `DashboardService` acts as a pure read-only aggregation layer. It executes optimized SQLAlchemy queries using `func.count()`, `func.date()`, and window functions to compile metrics across the entire application domain without retrieving or looping over large ORM collections in Python.
- **Router (`backend/app/features/dashboard/router.py`)**: Provides the five required HTTP GET endpoints: `/overview`, `/threat-activity`, `/organization`, `/feed-status`, and `/recent-intelligence`. Registered in `api_v1.py`.

### Architectural Decisions

- **Aggregate SQL Queries**: The dashboard relies entirely on database-level aggregation to ensure scaling. For instance, calculating top threat actors utilizes a direct `GROUP BY` and `ORDER BY count DESC` directly on the association table `indicator_threat_actor`, preventing N+1 problems and minimizing memory usage.
- **Zero Business Logic Duplication**: Data related to Indicators, Feeds, Assets, and Investigations are queried dynamically using their original models. No cached summary tables or materialized views were introduced, fulfilling the requirement for real-time overview using existing records.
- **Missing Optional Data Handling**: The service returns empty collections (`[]`) and zero counts (`0`) instead of failing when requested analytics categories (e.g., active watchlist matches) do not possess underlying data, keeping the front-end consumers stable.
- **Dependency Re-use**: Used the existing `IndicatorSummary` and `EntitySummary` schemas from the search feature to provide recent intelligence payloads.
