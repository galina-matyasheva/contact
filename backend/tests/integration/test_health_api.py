from unittest.mock import patch

from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("healthy", "degraded")
    assert "version" in data
    assert "timestamp" in data
    assert "subsystems" in data


def test_health_response_model(client: TestClient) -> None:
    response = client.get("/api/health")
    data = response.json()
    assert isinstance(data["status"], str)
    assert isinstance(data["version"], str)
    assert isinstance(data["timestamp"], str)
    assert isinstance(data["subsystems"], dict)
