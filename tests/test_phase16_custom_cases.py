"""Unit and integration tests for user-created persistent custom test cases in RACE."""

import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from backend.api.app import app
from backend.storage.custom_case_repository import CustomCaseRepository, build_custom_ground_truth
from backend.core.constants import FailureClass, RecoveryStrategy, CaseState
from backend.domain.events import RevenueEvent

client = TestClient(app)


def test_custom_case_repository_persistence(tmp_path):
    """Verifies SQLite repository stores, queries, and updates custom cases."""
    db_file = tmp_path / "test_race_cases.db"
    repo = CustomCaseRepository(db_path=db_file)

    case_id_1 = repo.get_next_case_id()
    assert case_id_1 == "RACE-CUSTOM-0001"

    evt = RevenueEvent(
        event_id="evt_test_01",
        timestamp="2026-08-21T12:00:00Z",
        event_type="failed_payment",
        merchant_id="merch_01",
        customer_id="cust_01",
        amount=1500.0,
        currency="INR",
        payment_method="CARD",
        failure_reason="GATEWAY_TIMEOUT",
        failure_class=FailureClass.TEMPORARY_NETWORK,
        payment_state="FAILED",
        gateway_route_health="UP",
    )
    gt = build_custom_ground_truth(evt, case_id=case_id_1)
    res = {
        "case_id": case_id_1,
        "final_state": "ACTION_SELECTED",
        "recovered_amount": 0.0,
        "is_recovered": False,
        "is_escalated": False,
        "is_stopped": False,
    }

    saved = repo.save_case(evt, gt, res)
    assert saved["case_id"] == "RACE-CUSTOM-0001"
    assert saved["source"] == "CUSTOM"
    assert saved["amount"] == 1500.0

    # Test next ID increment
    case_id_2 = repo.get_next_case_id()
    assert case_id_2 == "RACE-CUSTOM-0002"

    # Test retrieval
    fetched = repo.get_case("RACE-CUSTOM-0001")
    assert fetched is not None
    assert fetched["failure_class"] == "TEMPORARY_NETWORK"

    # Test outcome update
    repo.update_case_outcome(
        case_id="RACE-CUSTOM-0001",
        final_state="RECOVERED",
        recovered_amount=1500.0,
        is_recovered=True,
        is_escalated=False,
        is_stopped=False,
        selected_strategy="RETRY_NOW",
        audit_trail=[{"audit_id": "aud_01", "outcome": "RECOVERED"}],
    )
    updated = repo.get_case("RACE-CUSTOM-0001")
    assert updated["current_state"] == "RECOVERED"
    assert updated["recovered_amount"] == 1500.0
    assert updated["is_recovered"] is True


def test_custom_case_api_create_and_retrieve():
    """Tests POST /api/v1/cases and GET /api/v1/cases/{case_id}."""
    payload = {
        "amount": 2500.0,
        "currency": "INR",
        "failure_class": "TEMPORARY_NETWORK",
        "failure_reason": "GATEWAY_TIMEOUT",
        "payment_method": "CARD",
        "gateway_route_health": "UP",
        "customer_recovery_history_rate": 0.75,
        "customer_opted_out": False,
    }
    response = client.post("/api/v1/cases", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "case_id" in data
    assert data["case_id"].startswith("RACE-CUSTOM-")
    assert data["source"] == "CUSTOM"
    assert data["amount"] == 2500.0
    assert data["selected_strategy"] == "RETRY_NOW"

    # Retrieve case detail
    case_id = data["case_id"]
    get_res = client.get(f"/api/v1/cases/{case_id}")
    assert get_res.status_code == 200
    detail = get_res.json()
    assert detail["case_id"] == case_id
    assert detail["source"] == "CUSTOM"
    assert len(detail["audit_trail"]) > 0


def test_custom_case_policy_enforcement_opt_out():
    """Tests that customer opt-out deterministically transitions custom case to STOPPED."""
    payload = {
        "amount": 3500.0,
        "currency": "INR",
        "failure_class": "INSUFFICIENT_FUNDS",
        "failure_reason": "INSUFFICIENT_FUNDS_OR_LIMIT",
        "payment_method": "CARD",
        "gateway_route_health": "UP",
        "customer_opted_out": True,  # Hard stop
    }
    response = client.post("/api/v1/cases", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["current_state"] == "STOPPED"
    assert data["is_stopped"] is True


def test_custom_case_policy_enforcement_high_value():
    """Tests that amounts > INR 50,000 trigger human escalation."""
    payload = {
        "amount": 75000.0,
        "currency": "INR",
        "failure_class": "INSUFFICIENT_FUNDS",
        "failure_reason": "INSUFFICIENT_FUNDS_OR_LIMIT",
        "payment_method": "CARD",
        "gateway_route_health": "UP",
        "customer_opted_out": False,
    }
    response = client.post("/api/v1/cases", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["current_state"] == "ESCALATED"
    assert data["is_escalated"] is True
    assert data["selected_strategy"] == "HUMAN_ESCALATION"


def test_custom_case_execution_and_verification():
    """Tests POST /api/v1/cases/{case_id}/execute on a custom case."""
    payload = {
        "amount": 1800.0,
        "currency": "INR",
        "failure_class": "TEMPORARY_NETWORK",
        "failure_reason": "GATEWAY_TIMEOUT",
        "payment_method": "CARD",
        "gateway_route_health": "UP",
        "customer_opted_out": False,
    }
    create_res = client.post("/api/v1/cases", json=payload)
    assert create_res.status_code == 201
    case_id = create_res.json()["case_id"]

    exec_res = client.post(f"/api/v1/cases/{case_id}/execute")
    assert exec_res.status_code == 200
    exec_data = exec_res.json()
    assert exec_data["case_id"] == case_id
    assert exec_data["source"] == "CUSTOM"
    assert exec_data["post_action_captured"] == 1800.0
    assert exec_data["is_recovered"] is True


def test_custom_case_creation_validation_errors():
    """Tests input validation rejecting invalid amounts or invalid failure classes."""
    # Negative amount
    res1 = client.post("/api/v1/cases", json={"amount": -50.0, "failure_class": "TEMPORARY_NETWORK"})
    assert res1.status_code == 422

    # Zero amount
    res2 = client.post("/api/v1/cases", json={"amount": 0.0, "failure_class": "TEMPORARY_NETWORK"})
    assert res2.status_code == 422

    # Invalid failure class enum
    res3 = client.post("/api/v1/cases", json={"amount": 100.0, "failure_class": "NON_EXISTENT_CLASS"})
    assert res3.status_code == 422


def test_benchmark_isolation_uncontaminated():
    """Verifies that creating custom cases never alters the frozen benchmark dataset files or counts."""
    val_path = Path("datasets/validation/revenue_events_validation.json")
    with open(val_path, "r", encoding="utf-8") as f:
        events = json.load(f)
    assert len(events) == 200

    # Ensure all validation cases have standard benchmark IDs
    for e in events:
        assert not e["event_id"].startswith("evt_race_custom")
