"""Unit tests for Phase 10 Outcome Observation and Recovery Verification."""

from backend.core.constants import CaseState
from backend.recovery.state_machine.states import RecoveryCase
from backend.recovery.state_machine.machine import RecoveryStateMachine
from backend.recovery.verification.verifier import RecoveryOutcomeVerifier, VerificationResult
from integrations.razorpay.client import RazorpayTestClient


def test_outcome_verifier_successful_captured_payment():
    """Verify captured payment transitions case to RECOVERED and sets recovered amount."""
    case = RecoveryCase(
        case_id="case_ver_1",
        event_id="evt_ver_1",
        merchant_id="mer_test",
        customer_id="cust_test",
        amount=4000.0,
        failure_reason="TEMP_FAIL",
        failure_class="TEMPORARY_NETWORK",
        retry_count=1,
    )
    RecoveryStateMachine.transition(case, CaseState.DIAGNOSED, reason="Diagnosed")
    RecoveryStateMachine.transition(case, CaseState.ACTION_SELECTED, reason="Selected")
    RecoveryStateMachine.transition(case, CaseState.POLICY_APPROVED, reason="Approved")
    RecoveryStateMachine.transition(case, CaseState.ACTION_EXECUTED, reason="Executed")

    verifier = RecoveryOutcomeVerifier(RazorpayTestClient(use_mock_adapter=True))
    res = verifier.verify_payment_outcome(case, payment_id="pay_test_captured")

    assert res.is_fully_recovered is True
    assert res.verified_state == "RECOVERED"
    assert res.verified_amount_recovered == 5000.0  # From mock adapter
    assert case.current_state == CaseState.RECOVERED
    assert case.recovered_amount == 5000.0


def test_outcome_verifier_failed_attempt_retry_eligible():
    """Verify failed attempt with retry_count < max_retries transitions to RETRY_ELIGIBLE."""
    case = RecoveryCase(
        case_id="case_ver_2",
        event_id="evt_ver_2",
        merchant_id="mer_test",
        customer_id="cust_test",
        amount=2000.0,
        failure_reason="TEMP_FAIL",
        failure_class="TEMPORARY_NETWORK",
        retry_count=1,
        max_retries=3,
    )
    RecoveryStateMachine.transition(case, CaseState.DIAGNOSED, reason="Diagnosed")
    RecoveryStateMachine.transition(case, CaseState.ACTION_SELECTED, reason="Selected")
    RecoveryStateMachine.transition(case, CaseState.POLICY_APPROVED, reason="Approved")
    RecoveryStateMachine.transition(case, CaseState.ACTION_EXECUTED, reason="Executed")

    verifier = RecoveryOutcomeVerifier()
    res = verifier.verify_payment_outcome(case, simulated_status="FAILED", simulated_amount=0.0)

    assert res.is_fully_recovered is False
    assert res.verified_state == "FAILED"
    assert case.current_state == CaseState.RETRY_ELIGIBLE


def test_outcome_verifier_failed_attempt_limit_reached_stopped():
    """Verify failed attempt with retry_count == max_retries transitions to STOPPED."""
    case = RecoveryCase(
        case_id="case_ver_3",
        event_id="evt_ver_3",
        merchant_id="mer_test",
        customer_id="cust_test",
        amount=2000.0,
        failure_reason="TEMP_FAIL",
        failure_class="TEMPORARY_NETWORK",
        retry_count=3,
        max_retries=3,
    )
    RecoveryStateMachine.transition(case, CaseState.DIAGNOSED, reason="Diagnosed")
    RecoveryStateMachine.transition(case, CaseState.ACTION_SELECTED, reason="Selected")
    RecoveryStateMachine.transition(case, CaseState.POLICY_APPROVED, reason="Approved")
    RecoveryStateMachine.transition(case, CaseState.ACTION_EXECUTED, reason="Executed")

    verifier = RecoveryOutcomeVerifier()
    res = verifier.verify_payment_outcome(case, simulated_status="FAILED", simulated_amount=0.0)

    assert res.is_fully_recovered is False
    assert case.current_state == CaseState.STOPPED
