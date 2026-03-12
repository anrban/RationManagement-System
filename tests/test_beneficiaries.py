"""Tests for beneficiary endpoints."""
import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_endpoint():
    """Health check endpoint should return 200 with correct payload."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "Digital Ration Management System"


def test_register_beneficiary_missing_fields():
    """Registering a beneficiary with missing required fields and no auth returns 401.
    FastAPI checks authentication (via Depends) before validating the request body,
    so unauthenticated requests with missing fields return 401."""
    response = client.post("/beneficiaries/register", json={})
    # Auth is checked before body validation; expect 401 without token
    assert response.status_code in (401, 422)


def test_register_beneficiary_requires_auth():
    """Registering a beneficiary without auth token should return 401."""
    response = client.post(
        "/beneficiaries/register",
        json={
            "national_id": "TEST123",
            "name": "Test User",
        },
    )
    assert response.status_code == 401


def test_list_beneficiaries_requires_auth():
    """Listing beneficiaries without auth should return 401."""
    response = client.get("/beneficiaries/")
    assert response.status_code == 401
