from unittest.mock import patch

from fastapi.testclient import TestClient


def test_metrics_requires_api_key(client: TestClient) -> None:
    with patch("app.routers.metrics.settings") as mock_settings:
        mock_settings.METRICS_API_KEY = "secret-key"
        response = client.get("/api/metrics")
    assert response.status_code == 403


def test_metrics_wrong_key(client: TestClient) -> None:
    with patch("app.routers.metrics.settings") as mock_settings:
        mock_settings.METRICS_API_KEY = "secret-key"
        response = client.get("/api/metrics", headers={"X-Api-Key": "wrong"})
    assert response.status_code == 403


def test_metrics_valid_key(client: TestClient) -> None:
    with patch("app.routers.metrics.settings") as mock_settings:
        mock_settings.METRICS_API_KEY = "secret-key"
        response = client.get("/api/metrics", headers={"X-Api-Key": "secret-key"})
    assert response.status_code == 200
    data = response.json()
    assert "total_contacts" in data
    assert "today_contacts" in data
    assert "sentiment_distribution" in data
    assert "category_distribution" in data


def test_metrics_no_key_configured(client: TestClient) -> None:
    with patch("app.routers.metrics.settings") as mock_settings:
        mock_settings.METRICS_API_KEY = ""
        response = client.get("/api/metrics")
    assert response.status_code == 200


def test_metrics_returns_structured_data(client: TestClient) -> None:
    with patch("app.routers.metrics.settings") as mock_settings:
        mock_settings.METRICS_API_KEY = ""
        response = client.get("/api/metrics")
    data = response.json()
    assert isinstance(data["total_contacts"], int)
    assert isinstance(data["today_contacts"], int)
    assert isinstance(data["sentiment_distribution"], dict)
    assert isinstance(data["category_distribution"], dict)
