"""Tests for analytics endpoints."""
import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_analytics_summary_requires_auth():
    """Analytics summary endpoint should return 401 without auth."""
    response = client.get("/analytics/summary")
    assert response.status_code == 401


def test_analytics_trends_requires_auth():
    """Distribution trends endpoint should return 401 without auth."""
    response = client.get("/analytics/distribution-trends")
    assert response.status_code == 401


def test_analytics_fraud_flags_requires_auth():
    """Fraud flags endpoint should return 401 without auth."""
    response = client.get("/analytics/fraud-flags")
    assert response.status_code == 401
