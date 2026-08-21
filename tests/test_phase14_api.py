"""Unit tests for Phase 14 Merchant Recovery Dashboard and REST API."""

import pytest
from fastapi.testclient import TestClient
from backend.api.app import app


@pytest.fixture
def client():
    """Returns FastAPI test client."""
    return TestClient(app)


def test_merchant_console_html(client):
    """Verify root path serves merchant recovery console HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert "RACE" in response.text
    assert "Revenue Adaptive Control Engine" in response.text


def test_api_overview_endpoint(client):
    """Verify /api/v1/overview returns structured KPI statistics."""
    response = client.get("/api/v1/overview")
    assert response.status_code == 200
    data = response.json()
    assert "revenue_at_risk_inr" in data
    assert "actual_recovered_inr" in data
    assert "recovery_rate_pct" in data
    assert data["policy_violations_count"] == 0
    assert data["duplicate_actions_count"] == 0


def test_api_cases_list_endpoint(client):
    """Verify /api/v1/cases returns list of cases with valid structure."""
    response = client.get("/api/v1/cases?limit=10")
    assert response.status_code == 200
    cases = response.json()
    assert len(cases) > 0
    first_case = cases[0]
    assert "case_id" in first_case
    assert "amount" in first_case
    assert "current_state" in first_case


def test_api_case_detail_endpoint(client):
    """Verify /api/v1/cases/{case_id} returns granular audit trail and explanation."""
    # First fetch list to get a valid case_id
    list_res = client.get("/api/v1/cases?limit=1")
    case_id = list_res.json()[0]["case_id"]

    detail_res = client.get(f"/api/v1/cases/{case_id}")
    assert detail_res.status_code == 200
    data = detail_res.json()
    assert data["case_id"] == case_id
    assert "event" in data
    assert "audit_trail" in data
    assert "explanation" in data


def test_api_benchmark_endpoint(client):
    """Verify /api/v1/benchmark executes and returns comparative results."""
    response = client.get("/api/v1/benchmark?split=validation")
    assert response.status_code == 200
    data = response.json()
    assert "baseline_a" in data
    assert "race" in data
    assert data["race"]["incremental_revenue_vs_baseline_a"] > 0.0
