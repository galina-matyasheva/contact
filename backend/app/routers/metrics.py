from __future__ import annotations

import hmac
import logging

from fastapi import APIRouter, Depends, Header

from app.core.config import settings
from app.core.dependencies import get_contact_service
from app.core.exceptions import ForbiddenError
from app.core.strings import FORBIDDEN_API_KEY_MESSAGE, SUMMARY_METRICS
from app.schemas.metrics import MetricsResponse
from app.services.contact_service import ContactService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["metrics"])


def _verify_api_key(x_api_key: str = Header(default="")) -> None:
    if not settings.METRICS_API_KEY:
        if settings.is_production:
            logger.warning("METRICS_API_KEY not set — metrics endpoint is open")
        return
    if not hmac.compare_digest(x_api_key, settings.METRICS_API_KEY):
        raise ForbiddenError(FORBIDDEN_API_KEY_MESSAGE)


@router.get(
    "/api/metrics",
    response_model=MetricsResponse,
    summary=SUMMARY_METRICS,
)
async def get_metrics(
    contact_service: ContactService = Depends(get_contact_service),
    _: None = Depends(_verify_api_key),
) -> MetricsResponse:
    data = await contact_service.get_metrics()
    return MetricsResponse(**data)
