

## Phase 8 — Investigation & Case Management

### New Files

```
backend/app/features/investigations/
  router.py
  schemas.py
  service.py
```

### API Layer Structure

- **Schemas (`backend/app/features/investigations/schemas.py`)**: Defined schemas for CRUD operations (`InvestigationCreate`, `InvestigationUpdate`), `InvestigationSummaryResponse` for aggregating related threat intelligence, and `InvestigationTimelineEvent` for chronological event tracking.
- **Service (`backend/app/features/investigations/service.py`)**: `InvestigationService` encapsulates all business logic. Rather than directly embedding the logic to find nested relations (like malware or campaigns), `get_summary()` relies on the `CorrelationService.get_relationships()` method previously developed in Phase 6. This leverages existing N+1-free bulk loading behavior.
- **Router (`backend/app/features/investigations/router.py`)**: Provides endpoints for creating, linking/unlinking indicators, summarizing, and tracking the timeline of investigations. Registered in `api_v1.py`.

### Architectural Decisions

- **Dynamic Summary Generation**: Instead of maintaining complex many-to-many relationships from `Investigation` to every single entity type (like `vulnerabilities` and `reports`), the service dynamically aggregates this data. It loops through the `Investigation`'s explicitly linked indicators and calls `CorrelationService.get_relationships()` to recursively discover all related metadata on-the-fly.
- **Dynamic Timeline Tracking**: Instead of creating a dedicated `InvestigationEvent` (Audit Log) table which risks bloating the database, the `get_timeline()` endpoint derives chronological events dynamically from existing timestamp properties across the database (`Investigation.created_at`, `investigation_indicator.created_at`, `EnrichmentResult.created_at`, and `Indicator.updated_at`).
- **Database Migration**: The core `investigations` table and its many-to-many tables (like `investigation_indicator`) were already created during Phase 1 (`6d4d4982970a_database_foundation.py`). Phase 8 added a single Alembic migration (`5acb6156270b_investigation_engine`) to append a `created_at` timestamp exclusively to `investigation_indicator` to support the timeline feature.
