"""Comprehensive reliability, security, and failure injection test suite for Phase 15."""

import pytest
from backend.domain.events import RevenueEvent
from backend.domain.ground_truth import CaseGroundTruth
from backend.core.constants import FailureClass, RecoveryStrategy, EventType, CaseState, PolicyDecision
from backend.recovery.state_machine.states import RecoveryCase
from backend.recovery.state_machine.machine import RecoveryStateMachine
from backend.recovery.policies.gate import PolicyGate
from backend.recovery.idempotency.manager import IdempotencyManager
from backend.recovery.execution.executor import BoundedRecoveryExecutor
from backend.recovery.verification.verifier import RecoveryOutcomeVerifier
from integrations.razorpay.client import RazorpayTestClient
from evaluation.engine import RACEEvaluationEngine


def test_failure_1_upstream_timeout_does_not_duplicate():
    """Verify that an upstream timeout transitions safely and does not trigger duplicate charges."""
    event = RevenueEvent(
        event_id="evt_fail_to",
        timestamp="2026-08-20T10:00:00Z",
        event_type=EventType.FAILED_PAYMENT,
        merchant_id="mer_test",
        customer_id="cust_to",
        amount=5000.0,
        currency="INR",
        payment_method="UPI",
        failure_reason="UPSTREAM_504",
        failure_class=FailureClass.GATEWAY_DEGRADATION,
        payment_state="FAILED",
    )
    case = RecoveryCase(
        case_id="case_fail_to",
        event_id=event.event_id,
        merchant_id=event.merchant_id,
        customer_id=event.customer_id,
        amount=event.amount,
        failure_reason=event.failure_reason,
        failure_class=event.failure_class.value,
    )
    RecoveryStateMachine.transition(case, CaseState.DIAGNOSED, reason="Diagnosed")
    RecoveryStateMachine.transition(case, CaseState.ACTION_SELECTED, reason="Selected")
    RecoveryStateMachine.transition(case, CaseState.POLICY_APPROVED, reason="Approved")

    timeout_client = RazorpayTestClient(simulate_timeout=True, use_mock_adapter=True)
    executor = BoundedRecoveryExecutor(timeout_client)
    res = executor.execute(event, case, RecoveryStrategy.RETRY_NOW)

    assert res.success is False
    assert res.reconciliation_required is True
    assert case.current_state == CaseState.EXECUTION_FAILED
    # Ensure retry count is 1 and no further duplicate call was made
    assert case.retry_count == 1


def test_failure_2_unknown_state_blocks_further_payment_actions():
    """Verify policy blocks any new money action if payment state is UNKNOWN."""
    event = RevenueEvent(
        event_id="evt_fail_unk",
        timestamp="2026-08-20T10:00:00Z",
        event_type=EventType.FAILED_PAYMENT,
        merchant_id="mer_test",
        customer_id="cust_unk",
        amount=1000.0,
        currency="INR",
        payment_method="CARD",
        failure_reason="UNKNOWN",
        failure_class=FailureClass.UNKNOWN,
        payment_state="PENDING",
    )
    case = RecoveryCase(
        case_id="case_fail_unk",
        event_id=event.event_id,
        merchant_id=event.merchant_id,
        customer_id=event.customer_id,
        amount=event.amount,
        failure_reason=event.failure_reason,
        failure_class=event.failure_class.value,
        actual_outcome="UNKNOWN",
    )
    result = PolicyGate.evaluate(event, case, RecoveryStrategy.RETRY_NOW)
    assert result.decision == PolicyDecision.BLOCKED
    assert result.is_allowed is False


def test_failure_3_duplicate_event_idempotency():
    """Verify duplicate event dispatch is rejected by idempotency layer."""
    idemp = IdempotencyManager()
    key = IdempotencyManager.generate_key("mer_sec", "cust_sec", "pay_sec", "RETRY_NOW", 1)
    idemp.acquire_lock(key, "case_sec", "RETRY_NOW", 1)

    # Attempt second lock
    with pytest.raises(Exception):
        idemp.acquire_lock(key, "case_sec", "RETRY_NOW", 1)


def test_failure_4_customer_opt_out_hard_stop():
    """Verify customer opt out terminates any action."""
    event = RevenueEvent(
        event_id="evt_sec_opt",
        timestamp="2026-08-20T10:00:00Z",
        event_type=EventType.FAILED_PAYMENT,
        merchant_id="mer_sec",
        customer_id="cust_sec",
        amount=2000.0,
        currency="INR",
        payment_method="UPI",
        failure_reason="OPT_OUT",
        failure_class=FailureClass.CUSTOMER_ABANDONMENT,
        payment_state="FAILED",
        customer_opted_out=True,
    )
    case = RecoveryCase(
        case_id="case_sec_opt",
        event_id=event.event_id,
        merchant_id=event.merchant_id,
        customer_id=event.customer_id,
        amount=event.amount,
        failure_reason=event.failure_reason,
        failure_class=event.failure_class.value,
    )
    result = PolicyGate.evaluate(event, case, RecoveryStrategy.REMINDER_THEN_RETRY)
    assert result.decision == PolicyDecision.BLOCKED


def test_failure_5_ai_fallback_to_deterministic():
    """Verify system runs gracefully when AI diagnosis is disabled or ablated."""
    engine = RACEEvaluationEngine(enable_ai_diagnosis=False)
    event = RevenueEvent(
        event_id="evt_sec_ai_off",
        timestamp="2026-08-20T10:00:00Z",
        event_type=EventType.FAILED_PAYMENT,
        merchant_id="mer_test",
        customer_id="cust_ai",
        amount=1500.0,
        currency="INR",
        payment_method="UPI",
        failure_reason="NETWORK_TIMEOUT",
        failure_class=FailureClass.TEMPORARY_NETWORK,
        payment_state="FAILED",
    )
    gt = CaseGroundTruth(
        case_id="case_sec_ai_off",
        event_id=event.event_id,
        true_revenue_at_risk=1500.0,
        true_recoverable_amount=1500.0,
        true_optimal_strategy=RecoveryStrategy.RETRY_NOW,
        true_counterfactual_outcomes={
            "RETRY_NOW": {"outcome": "RECOVERED", "recovered_amount": 1500.0, "p_success": 0.9}
        },
        allowed_actions=[RecoveryStrategy.RETRY_NOW, RecoveryStrategy.STOP],
    )
    res = engine.process_case(event, gt)
    assert res["audit_complete"] is True
    assert res["is_recovered"] is True
