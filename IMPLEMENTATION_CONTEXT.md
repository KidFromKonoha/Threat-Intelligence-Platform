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
