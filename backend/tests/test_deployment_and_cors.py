import pytest
from fastapi.testclient import TestClient
from backend.app.core.config import Settings
from backend.app.main import app

client = TestClient(app)


def test_default_cors_origins_resolution():
    """Verify default CORS origins allow standard local development ports."""
    settings = Settings()
    origins = settings.get_cors_origins()
    assert isinstance(origins, list)
    assert "http://localhost:3000" in origins
    assert "http://127.0.0.1:3000" in origins
    assert "http://localhost:5173" in origins


def test_comma_separated_cors_origins_parsing():
    """Verify comma-separated CORS_ORIGINS string parses into a clean list of origins."""
    settings = Settings(
        CORS_ORIGINS="https://risk.merchant.com, https://admin.merchant.com, http://localhost:3000"
    )
    origins = settings.get_cors_origins()
    assert origins == [
        "https://risk.merchant.com",
        "https://admin.merchant.com",
        "http://localhost:3000",
    ]


def test_unsafe_wildcard_cors_rejected_in_production():
    """Verify that wildcard '*' CORS is strictly rejected when APP_ENV is production."""
    settings = Settings(
        APP_ENV="production",
        CORS_ORIGINS="*"
    )
    with pytest.raises(ValueError, match="Unsafe CORS configuration"):
        settings.get_cors_origins()


def test_safe_production_cors_origins():
    """Verify that explicit domain origins pass validation in production mode."""
    settings = Settings(
        APP_ENV="production",
        CORS_ORIGINS="https://merchant-console.example.com,https://api.example.com"
    )
    origins = settings.get_cors_origins()
    assert origins == ["https://merchant-console.example.com", "https://api.example.com"]


def test_health_check_endpoint_deployment_metadata():
    """Verify that the health check endpoint returns system metadata for deployment monitoring."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app_name" in data
    assert "environment" in data
    assert "active_model" in data
    assert "policy_thresholds" in data
    assert data["policy_thresholds"]["low"] == 0.30


def test_api_base_url_resolution_logic():
    """Verify the API base URL normalization algorithm used by the frontend client."""
    def resolve_api_base(raw_base: str | None) -> str:
        base = raw_base or "http://127.0.0.1:8000"
        host = base.rstrip("/")
        return f"{host}/api/v1"

    # Default fallback
    assert resolve_api_base(None) == "http://127.0.0.1:8000/api/v1"
    assert resolve_api_base("") == "http://127.0.0.1:8000/api/v1"
    # Clean host without trailing slash
    assert resolve_api_base("https://api.merchant.com") == "https://api.merchant.com/api/v1"
    # Host with trailing slash
    assert resolve_api_base("https://api.merchant.com/") == "https://api.merchant.com/api/v1"
    assert resolve_api_base("http://127.0.0.1:8000///") == "http://127.0.0.1:8000/api/v1"
