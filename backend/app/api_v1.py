from fastapi import APIRouter

from app.features.health.router import router as health_router
from app.features.feeds.router import router as feeds_router
from app.features.indicators.router import router as indicators_router
from app.features.search.router import router as search_router
from app.features.correlation.router import router as correlation_router
from app.features.enrichment.router import router as enrichment_router
from app.features.investigations.router import router as investigations_router
from app.features.dashboard.router import router as dashboard_router
from app.features.entity_details.router import router as entity_details_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(feeds_router)
api_router.include_router(indicators_router)
api_router.include_router(search_router)
api_router.include_router(correlation_router)
api_router.include_router(enrichment_router)
api_router.include_router(investigations_router)
api_router.include_router(dashboard_router)
api_router.include_router(entity_details_router)
