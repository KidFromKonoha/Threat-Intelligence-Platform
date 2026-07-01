from fastapi import APIRouter

from app.features.health.router import router as health_router
from app.features.feeds.router import router as feeds_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(feeds_router)
