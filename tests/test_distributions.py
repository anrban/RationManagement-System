"""Tests for distribution endpoints."""
import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_distribution_logs_requires_auth():
    """Distribution logs endpoint should return 401 without auth."""
    response = client.get("/distributions/logs")
    assert response.status_code == 401


def test_record_distribution_requires_auth():
    """Recording a distribution should return 401 without auth."""
    response = client.post(
        "/distributions/record",
        json={
            "beneficiary_id": "00000000-0000-0000-0000-000000000001",
            "ration_type": "rice",
            "quantity_kg": 5.0,
        },
    )
    assert response.status_code == 401


def test_get_distribution_requires_auth():
    """Getting a single distribution should return 401 without auth."""
    response = client.get("/distributions/00000000-0000-0000-0000-000000000001")
    assert response.status_code == 401
