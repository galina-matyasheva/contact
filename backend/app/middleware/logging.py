import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.dependencies import get_client_ip
from app.core.utils import anonymize_ip

logger = logging.getLogger("access")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.monotonic()
        client_ip = get_client_ip(request)
        anon_ip = anonymize_ip(client_ip)

        response = await call_next(request)

        duration_ms = (time.monotonic() - start_time) * 1000
        request_id = getattr(request.state, "request_id", "-")

        logger.info(
            "%s | %s | %s %s | %d | %.1fms",
            anon_ip,
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

        return response
