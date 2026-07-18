from __future__ import annotations

import logging

from datetime import datetime, timezone

from app.core.exceptions import RateLimitError
from app.core.strings import CONTACT_SUCCESS_MESSAGE
from app.core.utils import anonymize_ip
from app.schemas.contact import ContactCreate
from app.services.ai_service import AIService
from app.services.email_service import EmailService
from app.services.rate_limiter import RateLimiter
from app.services.storage_service import FileStorage

logger = logging.getLogger(__name__)


class ContactService:
    def __init__(
        self,
        storage: FileStorage,
        ai_service: AIService,
        email_service: EmailService,
        rate_limiter: RateLimiter,
    ) -> None:
        self._storage = storage
        self._ai = ai_service
        self._email = email_service
        self._rate_limiter = rate_limiter

    async def process_contact(
        self,
        contact: ContactCreate,
        client_ip: str,
    ) -> dict:
        if await self._rate_limiter.is_rate_limited(client_ip):
            raise RateLimitError()

        contact_data = contact.model_dump()

        ai_analysis = await self._ai.analyze_contact(contact_data)

        contact_id = await self._storage.save_contact(
            contact_data=contact_data,
            ai_analysis=ai_analysis,
        )

        email_results = await self._email.send_emails(
            contact_data=contact_data,
            contact_id=contact_id,
            ai_analysis=ai_analysis,
        )

        logger.info("Обращение %s обработано от %s", contact_id, anonymize_ip(client_ip))

        return {
            "success": True,
            "message": CONTACT_SUCCESS_MESSAGE,
            "id": contact_id,
            "ai_analysis": ai_analysis,
            "emails_sent": email_results,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def get_metrics(self) -> dict:
        return await self._storage.get_metrics()
