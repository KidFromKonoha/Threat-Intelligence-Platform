from fastapi import APIRouter, Depends

from app.features.health.router import router as health_router
from app.features.auth.router import router as auth_router
from app.features.users.router import router as users_router
from app.features.feeds.router import router as feeds_router
from app.features.indicators.router import router as indicators_router
from app.features.search.router import router as search_router
from app.features.correlation.router import router as correlation_router
from app.features.enrichment.router import router as enrichment_router
from app.features.investigations.router import router as investigations_router
from app.features.dashboard.router import router as dashboard_router
from app.features.entity_details.router import router as entity_details_router
from app.features.watchlists.router import router as watchlists_router
from app.features.reports.router import router as reports_router
from app.features.graph.router import router as graph_router

from app.features.auth.dependencies import require_viewer

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(feeds_router, dependencies=[Depends(require_viewer)])
api_router.include_router(indicators_router, dependencies=[Depends(require_viewer)])
api_router.include_router(search_router, dependencies=[Depends(require_viewer)])
api_router.include_router(correlation_router, dependencies=[Depends(require_viewer)])
api_router.include_router(enrichment_router, dependencies=[Depends(require_viewer)])
api_router.include_router(investigations_router, dependencies=[Depends(require_viewer)])
api_router.include_router(dashboard_router, dependencies=[Depends(require_viewer)])
api_router.include_router(entity_details_router, dependencies=[Depends(require_viewer)])
api_router.include_router(watchlists_router, dependencies=[Depends(require_viewer)])
api_router.include_router(reports_router, dependencies=[Depends(require_viewer)])
api_router.include_router(graph_router, dependencies=[Depends(require_viewer)])
