from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

from app.core.config import settings
from app.core.strings import SUMMARY_HEALTH
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get(
    "/api/health",
    response_model=HealthResponse,
    summary=SUMMARY_HEALTH,
)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
        subsystems={},
    )
