from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request

from app.core.config import settings
from app.services.ai_service import AIService
from app.services.contact_service import ContactService
from app.services.email_service import EmailService
from app.services.rate_limiter import RateLimiter
from app.services.storage_service import FileStorage

_ai_service_instance: AIService | None = None
_email_service_instance: EmailService | None = None
_storage_instance: FileStorage | None = None
_rate_limiter_instance: RateLimiter | None = None
_contact_service_instance: ContactService | None = None


def get_ai_service() -> AIService:
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIService()
    return _ai_service_instance


def get_email_service() -> EmailService:
    global _email_service_instance
    if _email_service_instance is None:
        _email_service_instance = EmailService()
    return _email_service_instance


def get_storage_service() -> FileStorage:
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = FileStorage()
    return _storage_instance


def get_rate_limiter() -> RateLimiter:
    global _rate_limiter_instance
    if _rate_limiter_instance is None:
        _rate_limiter_instance = RateLimiter()
    return _rate_limiter_instance


def get_contact_service(
    storage: Annotated[FileStorage, Depends(get_storage_service)],
    ai: Annotated[AIService, Depends(get_ai_service)],
    email: Annotated[EmailService, Depends(get_email_service)],
    rate_limiter: Annotated[RateLimiter, Depends(get_rate_limiter)],
) -> ContactService:
    return ContactService(
        storage=storage,
        ai_service=ai,
        email_service=email,
        rate_limiter=rate_limiter,
    )


def get_client_ip(request: Request) -> str:
    if settings.TRUSTED_PROXY:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()
    return request.client.host if request.client else "unknown"
