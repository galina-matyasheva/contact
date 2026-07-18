from __future__ import annotations

import re
from datetime import datetime, timezone

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.strings import (
    DESC_AUTO_REPLY,
    DESC_CATEGORY,
    DESC_COMMENT,
    DESC_EMAIL,
    DESC_NAME,
    DESC_PHONE,
    DESC_SENTIMENT,
    PHONE_INVALID_MESSAGE,
)

PHONE_PATTERN = re.compile(r"^[\+]?[\d\s\-\(\)]{6,20}$")


class ContactCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description=DESC_NAME)
    phone: str = Field(..., min_length=6, max_length=20, description=DESC_PHONE)
    email: EmailStr = Field(..., description=DESC_EMAIL)
    comment: str = Field(
        ..., min_length=5, max_length=2000, description=DESC_COMMENT
    )

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v = v.strip()
        if not PHONE_PATTERN.match(v):
            raise ValueError(PHONE_INVALID_MESSAGE)
        return v


class AIAnalysisResponse(BaseModel):
    sentiment: str = Field(
        default="unknown",
        description=DESC_SENTIMENT,
    )
    category: str = Field(
        default="other",
        description=DESC_CATEGORY,
    )
    auto_reply: str = Field(default="", description=DESC_AUTO_REPLY)


class EmailResults(BaseModel):
    owner: bool
    user_copy: bool


class ContactResponse(BaseModel):
    success: bool
    message: str
    id: str | None = None
    ai_analysis: AIAnalysisResponse | None = None
    emails_sent: EmailResults | None = None
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
