from fastapi import APIRouter

from app.api.schemas import HealthResponse, ReadyResponse
from app.core.config import get_settings, validate_required_settings
from app.infrastructure.database.session import check_db_connection

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="ok", app_name=settings.app_name)


@router.get("/ready", response_model=ReadyResponse)
async def ready() -> ReadyResponse:
    missing = validate_required_settings()
    if missing:
        return ReadyResponse(status="not_ready", database=f"missing: {', '.join(missing)}")
    db_ok = check_db_connection()
    return ReadyResponse(
        status="ready" if db_ok else "not_ready",
        database="connected" if db_ok else "disconnected",
    )
