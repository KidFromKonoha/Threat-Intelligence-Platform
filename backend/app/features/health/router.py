from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.redis import get_redis_client
from app.db.session import get_db
from app.features.health.schemas import HealthResponse, ServiceStatus

router = APIRouter(prefix="/health", tags=["health"])
logger = get_logger(__name__)


@router.get("", response_model=HealthResponse)
def get_health(db: Session = Depends(get_db)) -> HealthResponse:
    """Report platform health, including database and cache connectivity."""
    database_status = _check_database(db)
    redis_status = _check_redis()

    overall = "ok" if database_status.status == "ok" and redis_status.status == "ok" else "degraded"

    return HealthResponse(status=overall, database=database_status, redis=redis_status)


def _check_database(db: Session) -> ServiceStatus:
    try:
        db.execute(text("SELECT 1"))
        return ServiceStatus(status="ok")
    except Exception as exc:  # noqa: BLE001
        logger.error("Database health check failed: %s", exc)
        return ServiceStatus(status="error", detail=str(exc))


def _check_redis() -> ServiceStatus:
    try:
        get_redis_client().ping()
        return ServiceStatus(status="ok")
    except Exception as exc:  # noqa: BLE001
        logger.error("Redis health check failed: %s", exc)
        return ServiceStatus(status="error", detail=str(exc))
