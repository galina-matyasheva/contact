from __future__ import annotations

import logging
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.strings import (
    AI_UNAVAILABLE_MESSAGE,
    EMAIL_FAILED_MESSAGE,
    FORBIDDEN_MESSAGE,
    INTERNAL_ERROR_MESSAGE,
    RATE_LIMIT_MESSAGE,
    VALIDATION_ERROR_MESSAGE,
)


class AppError(Exception):
    def __init__(self, message: str, status_code: int = 500, details: Any = None) -> None:
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class RateLimitError(AppError):
    def __init__(self, message: str = RATE_LIMIT_MESSAGE) -> None:
        super().__init__(message=message, status_code=429)


class AIServiceError(AppError):
    def __init__(self, message: str = AI_UNAVAILABLE_MESSAGE) -> None:
        super().__init__(message=message, status_code=503)


class EmailServiceError(AppError):
    def __init__(self, message: str = EMAIL_FAILED_MESSAGE) -> None:
        super().__init__(message=message, status_code=502)


class ForbiddenError(AppError):
    def __init__(self, message: str = FORBIDDEN_MESSAGE) -> None:
        super().__init__(message=message, status_code=403)


def error_response(message: str, status_code: int, details: Any = None) -> JSONResponse:
    payload: dict[str, Any] = {"success": False, "message": message}
    if details is not None:
        payload["errors"] = details
    return JSONResponse(status_code=status_code, content=payload)


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return error_response(message=exc.message, status_code=exc.status_code)


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = []
    for error in exc.errors():
        loc = " → ".join(str(part) for part in error.get("loc", []))
        errors.append({"field": loc, "message": error.get("msg", "")})
    return error_response(
        message=VALIDATION_ERROR_MESSAGE,
        status_code=422,
        details=errors,
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger = logging.getLogger(__name__)
    logger.error("Unhandled error: %s", exc, exc_info=True)
    return error_response(message=INTERNAL_ERROR_MESSAGE, status_code=500)
