"""P0 Safety Regression Test Suite: Proves STOP Strategy and Blocked Cases Can Never Execute."""

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from backend.api.app import app
from integrations.razorpay.client import RazorpayTestClient
from backend.domain.events import RevenueEvent
from backend.domain.ground_truth import CaseGroundTruth
from backend.core.constants import FailureClass, RecoveryStrategy, CaseState, EventType
from backend.recovery.state_machine.states import RecoveryCase
from backend.recovery.state_machine.machine import RecoveryStateMachine
from backend.recovery.execution.executor import BoundedRecoveryExecutor
from backend.recovery.verification.verifier import RecoveryOutcomeVerifier
from backend.recovery.learning.statistics_store import StrategyStatisticsStore
from backend.recovery.learning.closed_loop import ClosedLoopLearningEngine
from evaluation.engine import RACEEvaluationEngine

client = TestClient(app)


def test_scenario_exact_reproduction_insufficient_funds_stop():
    """Exact reproduction of the reported bug:
    - Failure class: INSUFFICIENT_FUNDS
    - Customer opted out / unrecoverable scenario -> Strategy: STOP
    - ERV: INR 0.00
    - Outstanding: INR 4200.00
    - Gateway state: unpaid
    """
    # Step 1: Create case where STOP is selected
    create_res = client.post("/api/v1/cases", json={
        "amount": 4200.0,
        "currency": "INR",
        "failure_class": "INSUFFICIENT_FUNDS",
        "failure_reason": "INSUFFICIENT_FUNDS_OR_LIMIT",
        "customer_recovery_history_rate": 0.0,
        "customer_opted_out": True,  # Policy forces STOP
    })
    assert create_res.status_code == 201
    case_data = create_res.json()
    case_id = case_data["case_id"]
    assert case_data["selected_strategy"] == "STOP"
    assert case_data["current_state"] == "STOPPED"
    assert case_data["is_stopped"] is True

    # Step 2: Attempt execution via API
    exec_res = client.post(f"/api/v1/cases/{case_id}/execute")
    assert exec_res.status_code == 200
    data = exec_res.json()

    # Step 3: Verify HARD BLOCK invariants
    assert data["executed"] is False
    assert data["status"] == "STOPPED"
    assert data["final_state"] == "STOPPED"
    assert data["post_action_captured"] == 0.0
    assert data["pre_action_outstanding"] == 4200.0
    assert data["is_recovered"] is False
    assert data["is_stopped"] is True
    assert data["reference_id"] is None
    assert data["authoritative_payment_status"] == "unpaid"
    assert "Execution prohibited" in data["reason"]


def test_executor_directly_rejects_stop_without_calling_razorpay():
    """B & C. BoundedRecoveryExecutor directly rejects STOP and never calls Razorpay client."""
    mock_rzp = MagicMock(spec=RazorpayTestClient)
    executor = BoundedRecoveryExecutor(razorpay_client=mock_rzp)

    evt = RevenueEvent(
        event_id="evt_stop_safety_01",
        timestamp="2026-08-22T22:30:00Z",
        event_type=EventType.FAILED_PAYMENT,
        merchant_id="m_01",
        customer_id="c_01",
        amount=4200.0,
        currency="INR",
        failure_class=FailureClass.INSUFFICIENT_FUNDS,
        failure_reason="INSUFFICIENT_FUNDS_OR_LIMIT",
        payment_method="CARD",
        payment_state="FAILED",
        customer_opted_out=True,
    )
    case = RecoveryCase(
        case_id="case_stop_01",
        event_id=evt.event_id,
        merchant_id=evt.merchant_id,
        customer_id=evt.customer_id,
        amount=evt.amount,
        currency=evt.currency,
        failure_reason=evt.failure_reason,
        failure_class=evt.failure_class.value,
        selected_strategy=RecoveryStrategy.STOP,
        current_state=CaseState.ACTION_SELECTED,
    )

    result = executor.execute(evt, case, RecoveryStrategy.STOP)
    assert result.success is False
    assert result.status_code == "STOPPED"
    assert result.reference_id is None
    assert case.current_state == CaseState.STOPPED

    # Razorpay API MUST NEVER BE CALLED
    mock_rzp.create_order.assert_not_called()
    mock_rzp.create_payment_link.assert_not_called()
    mock_rzp.fetch_payment.assert_not_called()


def test_stop_does_not_update_learning_statistics():
    """G. Closed-loop learning must ignore STOP entirely."""
    stats_store = StrategyStatisticsStore()
    learning_engine = ClosedLoopLearningEngine(stats_store=stats_store)

    case = RecoveryCase(
        case_id="case_stop_learn_01",
        event_id="evt_01",
        merchant_id="m_01",
        customer_id="c_01",
        amount=4200.0,
        currency="INR",
        failure_reason="INSUFFICIENT_FUNDS",
        failure_class="INSUFFICIENT_FUNDS",
        selected_strategy=RecoveryStrategy.STOP,
        current_state=CaseState.STOPPED,
        actual_outcome="STOPPED",
        recovered_amount=0.0,
    )

    learning_engine.update_from_case(case, expected_value=0.0)

    # Buckets must not contain STOP
    all_buckets = stats_store.get_all_buckets()
    assert "INSUFFICIENT_FUNDS:STOP" not in all_buckets
    assert len(all_buckets) == 0


def test_verifier_rejects_unpaid_or_zero_amount_as_recovered():
    """I & J. Outcome verifier guarantees gateway state unpaid + 0 amount cannot become RECOVERED."""
    verifier = RecoveryOutcomeVerifier(razorpay_client=RazorpayTestClient(use_mock_adapter=True))
    case = RecoveryCase(
        case_id="case_unpaid_01",
        event_id="evt_01",
        merchant_id="m_01",
        customer_id="c_01",
        amount=4200.0,
        currency="INR",
        failure_reason="INSUFFICIENT_FUNDS",
        failure_class="INSUFFICIENT_FUNDS",
        selected_strategy=RecoveryStrategy.STOP,
        current_state=CaseState.STOPPED,
    )

    res = verifier.verify_payment_outcome(case, simulated_status="unpaid", simulated_amount=0.0)
    assert res.is_fully_recovered is False
    assert res.verified_amount_recovered == 0.0
    assert res.verified_state == "STOPPED"
    assert case.current_state == CaseState.STOPPED


def test_re_execution_of_stopped_case_remains_blocked():
    """N & P. Re-execution of an already STOPPED case is strictly refused."""
    res = client.post("/api/v1/cases", json={
        "amount": 5000.0,
        "currency": "INR",
        "failure_class": "FRAUD_SUSPECTED",
        "failure_reason": "HIGH_RISK_FRAUD_BLOCK",
    })
    assert res.status_code == 201
    case_id = res.json()["case_id"]

    # First execute attempt
    exec1 = client.post(f"/api/v1/cases/{case_id}/execute")
    assert exec1.status_code == 200
    assert exec1.json()["executed"] is False
    assert exec1.json()["final_state"] == "STOPPED"

    # Second execute attempt
    exec2 = client.post(f"/api/v1/cases/{case_id}/execute")
    assert exec2.status_code == 200
    assert exec2.json()["executed"] is False
    assert exec2.json()["status"] == "STOPPED"
    assert exec2.json()["post_action_captured"] == 0.0
