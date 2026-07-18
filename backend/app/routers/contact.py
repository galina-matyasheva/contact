from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request

from app.core.dependencies import get_client_ip, get_contact_service
from app.core.strings import SUMMARY_CONTACT
from app.schemas.contact import ContactCreate, ContactResponse
from app.services.contact_service import ContactService

router = APIRouter(prefix="/api", tags=["contact"])


@router.post(
    "/contact",
    response_model=ContactResponse,
    status_code=200,
    summary=SUMMARY_CONTACT,
)
async def create_contact(
    body: ContactCreate,
    request: Request,
    client_ip: Annotated[str, Depends(get_client_ip)],
    contact_service: Annotated[ContactService, Depends(get_contact_service)],
) -> dict[str, Any]:
    result = await contact_service.process_contact(
        contact=body,
        client_ip=client_ip,
    )
    return result
