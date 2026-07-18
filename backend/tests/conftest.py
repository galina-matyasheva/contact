from __future__ import annotations

from pathlib import Path
from typing import Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.dependencies import (
    get_ai_service,
    get_contact_service,
    get_email_service,
    get_rate_limiter,
    get_storage_service,
)
from app.services.ai_service import AIService
from app.services.contact_service import ContactService
from app.services.email_service import EmailService
from app.services.rate_limiter import RateLimiter
from app.services.storage_service import FileStorage


@pytest.fixture()
def tmp_data_dir(tmp_path: Path) -> Path:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "logs").mkdir()
    (data_dir / "metrics").mkdir()
    (data_dir / "emails").mkdir()
    return data_dir


@pytest.fixture()
def storage(tmp_data_dir: Path) -> Generator[FileStorage, None, None]:
    instance = FileStorage(data_dir=tmp_data_dir)
    app.dependency_overrides[get_storage_service] = lambda: instance
    yield instance
    app.dependency_overrides.pop(get_storage_service, None)


@pytest.fixture()
def rate_limiter() -> Generator[RateLimiter, None, None]:
    instance = RateLimiter(max_requests=5, window_seconds=60)
    app.dependency_overrides[get_rate_limiter] = lambda: instance
    yield instance
    app.dependency_overrides.pop(get_rate_limiter, None)


@pytest.fixture()
def mock_ai_service() -> Generator[MagicMock, None, None]:
    mock = MagicMock(spec=AIService)
    mock.analyze_contact = AsyncMock(
        return_value={
            "sentiment": "unknown",
            "category": "other",
            "auto_reply": "",
        }
    )
    app.dependency_overrides[get_ai_service] = lambda: mock
    yield mock
    app.dependency_overrides.pop(get_ai_service, None)


@pytest.fixture()
def mock_email_service() -> Generator[MagicMock, None, None]:
    mock = MagicMock(spec=EmailService)
    mock.send_emails = AsyncMock(return_value={"owner": True, "user_copy": True})
    app.dependency_overrides[get_email_service] = lambda: mock
    yield mock
    app.dependency_overrides.pop(get_email_service, None)


@pytest.fixture()
def client(
    storage: FileStorage,
    rate_limiter: RateLimiter,
    mock_ai_service: MagicMock,
    mock_email_service: MagicMock,
) -> Generator[TestClient, None, None]:
    contact_svc = ContactService(
        storage=storage,
        ai_service=mock_ai_service,
        email_service=mock_email_service,
        rate_limiter=rate_limiter,
    )
    app.dependency_overrides[get_contact_service] = lambda: contact_svc
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(get_contact_service, None)
