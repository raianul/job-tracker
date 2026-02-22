"""API endpoint tests (no DB required)."""
import pytest
from fastapi.testclient import TestClient


def test_root_returns_200_and_message(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Job Tracker API"
    assert "docs" in data


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_auth_me_returns_401_without_token(client: TestClient) -> None:
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_options_preflight_returns_200(client: TestClient) -> None:
    response = client.options(
        "/api/auth/dev-login",
        headers={"Origin": "http://localhost:3000"},
    )
    assert response.status_code == 200
    assert "access-control-allow-methods" in [h.lower() for h in response.headers.keys()]
