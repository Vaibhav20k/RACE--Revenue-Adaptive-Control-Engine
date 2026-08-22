"""Regression test suite for UI data wiring, policy consistency, and decision execution."""

import pytest
from fastapi.testclient import TestClient
from backend.api.app import app
from backend.core.constants import FailureClass, RecoveryStrategy, PolicyDecision, EventType
from backend.domain.events import RevenueEvent
from backend.domain.ground_truth import CaseGroundTruth
from evaluation.engine import RACEEvaluationEngine


@pytest.fixture
def client():
    return TestClient(app)


def test_queue_recommended_strategy_not_na(client):
    """Verifies that the recovery queue returns real strategies and not 'N/A'."""
    res = client.get("/api/v1/cases?limit=20")
    assert res.status_code == 200
    cases = res.json()
    assert len(cases) > 0

    valid_strategies = {
        "RETRY_NOW",
        "RETRY_LATER",
        "REMINDER_THEN_RETRY",
        "HUMAN_ESCALATION",
        "STOP",
        "NOT INVESTIGATED",
    }
    for c in cases:
        assert c["selected_strategy"] in valid_strategies, f"Unexpected strategy: {c['selected_strategy']}"
        assert c["selected_strategy"] != "N/A"


def test_case_detail_has_rich_explanation_not_na(client):
    """Verifies that case details provide a grounded human explanation and not 'N/A'."""
    res = client.get("/api/v1/cases?limit=5")
    cases = res.json()
    for c in cases:
        detail_res = client.get(f"/api/v1/cases/{c['case_id']}")
        assert detail_res.status_code == 200
        detail = detail_res.json()
        assert "explanation" in detail
        assert detail["explanation"] != "N/A"
        assert len(detail["explanation"]) > 10


from backend.storage.custom_case_repository import build_custom_ground_truth


def test_policy_approved_case_consistency():
    """Verifies that an approved case produces consistent policy gate and execution state."""
    engine = RACEEvaluationEngine()
    evt = RevenueEvent(
        event_id="evt_test_approved",
        timestamp="2026-08-22T10:00:00Z",
        event_type=EventType.FAILED_PAYMENT,
        merchant_id="merchant_test",
        customer_id="cust_test",
        payment_id="pay_test",
        order_id="ord_test",
        amount=1500.0,
        currency="INR",
        payment_method="CARD",
        payment_state="FAILED",
        failure_class=FailureClass.TEMPORARY_NETWORK,
        failure_reason="GATEWAY_TIMEOUT",
        gateway_route_health="UP",
        customer_recovery_history_rate=0.8,
        customer_opted_out=False,
        retry_count=0,
    )
    gt = build_custom_ground_truth(evt, case_id="case_test_approved")

    res = engine.process_case(evt, gt)
    assert res["policy_decision"] == PolicyDecision.APPROVED.value
    assert res["selected_strategy"] in ["RETRY_NOW", "RETRY_LATER"]
    assert res["is_stopped"] is False


def test_policy_blocked_opt_out_consistency():
    """Verifies that an opted-out case produces a STOP decision, and zero recovery."""
    engine = RACEEvaluationEngine()
    evt = RevenueEvent(
        event_id="evt_test_blocked",
        timestamp="2026-08-22T10:00:00Z",
        event_type=EventType.FAILED_PAYMENT,
        merchant_id="merchant_test",
        customer_id="cust_test",
        payment_id="pay_test",
        order_id="ord_test",
        amount=2500.0,
        currency="INR",
        payment_method="CARD",
        payment_state="FAILED",
        failure_class=FailureClass.INSUFFICIENT_FUNDS,
        failure_reason="INSUFFICIENT_FUNDS_OR_LIMIT",
        gateway_route_health="UP",
        customer_recovery_history_rate=0.7,
        customer_opted_out=True,  # Hard stop
        retry_count=0,
    )
    gt = build_custom_ground_truth(evt, case_id="case_test_blocked")

    res = engine.process_case(evt, gt)
    assert res["selected_strategy"] == RecoveryStrategy.STOP.value
    assert res["is_stopped"] is True
    assert res["is_recovered"] is False
    assert res["recovered_amount"] == 0.0


def test_policy_escalation_high_value():
    """Verifies that transactions > INR 50K trigger ESCALATE_REQUIRED."""
    engine = RACEEvaluationEngine()
    evt = RevenueEvent(
        event_id="evt_test_high_val",
        timestamp="2026-08-22T10:00:00Z",
        event_type=EventType.FAILED_PAYMENT,
        merchant_id="merchant_test",
        customer_id="cust_test",
        payment_id="pay_test",
        order_id="ord_test",
        amount=75000.0,  # > 50K threshold
        currency="INR",
        payment_method="CARD",
        payment_state="FAILED",
        failure_class=FailureClass.INSUFFICIENT_FUNDS,
        failure_reason="INSUFFICIENT_FUNDS_OR_LIMIT",
        gateway_route_health="UP",
        customer_recovery_history_rate=0.9,
        customer_opted_out=False,
        retry_count=0,
    )
    gt = build_custom_ground_truth(evt, case_id="case_test_high_val")

    res = engine.process_case(evt, gt)
    assert res["policy_decision"] == PolicyDecision.ESCALATE_REQUIRED.value
    assert res["selected_strategy"] == RecoveryStrategy.HUMAN_ESCALATION.value
    assert res["is_escalated"] is True


def test_bayesian_learning_exact_failure_class_update():
    """Verifies that the closed-loop engine updates the EXACT failure class and strategy."""
    engine = RACEEvaluationEngine()
    evt = RevenueEvent(
        event_id="evt_test_network",
        timestamp="2026-08-22T10:00:00Z",
        event_type=EventType.FAILED_PAYMENT,
        merchant_id="merchant_test",
        customer_id="cust_test",
        payment_id="pay_test",
        order_id="ord_test",
        amount=1200.0,
        currency="INR",
        payment_method="CARD",
        payment_state="FAILED",
        failure_class=FailureClass.TEMPORARY_NETWORK,
        failure_reason="GATEWAY_TIMEOUT",
        gateway_route_health="UP",
        customer_recovery_history_rate=0.85,
        customer_opted_out=False,
        retry_count=0,
    )
    gt = build_custom_ground_truth(evt, case_id="case_test_network")

    engine.process_case(evt, gt)
    fc_str = FailureClass.TEMPORARY_NETWORK.value
    strat_str = RecoveryStrategy.RETRY_NOW.value
    updated_rate = engine.learning_engine.stats_store.get_empirical_rate(fc_str, strat_str)
    assert updated_rate > 0.0


def test_custom_scenario_validation_errors(client):
    """Verifies client/server validation rejects negative or zero amounts."""
    res_neg = client.post("/api/v1/cases", json={
        "amount": -50.0,
        "currency": "INR",
        "failure_class": "INSUFFICIENT_FUNDS",
    })
    assert res_neg.status_code == 422

    res_zero = client.post("/api/v1/cases", json={
        "amount": 0.0,
        "currency": "INR",
        "failure_class": "INSUFFICIENT_FUNDS",
    })
    assert res_zero.status_code == 422


def test_benchmarks_and_about_pages_accessible(client):
    """Verifies that /benchmarks and /about load successfully with 200 OK."""
    rb = client.get("/benchmarks")
    assert rb.status_code == 200
    assert "Scientific Evaluation Report" in rb.text
    assert "Component Ablation" in rb.text

    ra = client.get("/about")
    assert ra.status_code == 200
    assert "Technical Specification" in ra.text
