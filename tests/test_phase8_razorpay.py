"""Unit tests for Phase 8 Razorpay Test-Mode Integration and Bounded Execution."""

from backend.domain.events import RevenueEvent
from backend.core.constants import FailureClass, RecoveryStrategy, EventType, CaseState
from backend.recovery.state_machine.states import RecoveryCase
from backend.recovery.state_machine.machine import RecoveryStateMachine
from integrations.razorpay.client import RazorpayTestClient
from integrations.razorpay.schemas import RazorpayOrderRequest, RazorpayPaymentLinkRequest
from backend.recovery.execution.executor import BoundedRecoveryExecutor


def test_razorpay_client_mock_order_creation():
    """Verify test-mode order creation returns structured response with valid id."""
    client = RazorpayTestClient(use_mock_adapter=True)
    req = RazorpayOrderRequest(amount=250000, currency="INR", receipt="rec_test_101")
    resp = client.create_order(req)
    assert resp.entity == "order"
    assert resp.amount == 250000
    assert resp.id.startswith("order_")


def test_razorpay_client_mock_payment_link():
    """Verify payment link creation returns URL and created status."""
    client = RazorpayTestClient(use_mock_adapter=True)
    req = RazorpayPaymentLinkRequest(
        amount=150000,
        currency="INR",
        description="Test payment recovery",
        customer={"name": "Test Cust", "email": "test@example.com"},
    )
    resp = client.create_payment_link(req)
    assert resp.status == "created"
    assert resp.short_url.startswith("https://rzp.io")


def test_executor_happy_path_retry():
    """Verify bounded executor performs order creation and updates state machine correctly."""
    event = RevenueEvent(
        event_id="evt_exec_1",
        timestamp="2026-08-20T10:00:00Z",
        event_type=EventType.FAILED_PAYMENT,
        merchant_id="mer_test",
        customer_id="cust_1",
        amount=1200.0,
        currency="INR",
        payment_method="UPI",
        failure_reason="NETWORK_ERROR",
        failure_class=FailureClass.TEMPORARY_NETWORK,
        payment_state="FAILED",
    )
    case = RecoveryCase(
        case_id="case_exec_1",
        event_id=event.event_id,
        merchant_id=event.merchant_id,
        customer_id=event.customer_id,
        amount=event.amount,
        failure_reason=event.failure_reason,
        failure_class=event.failure_class.value,
    )
    # Move to POLICY_APPROVED
    RecoveryStateMachine.transition(case, CaseState.DIAGNOSED, reason="Diagnosed")
    RecoveryStateMachine.transition(case, CaseState.ACTION_SELECTED, reason="Selected")
    RecoveryStateMachine.transition(case, CaseState.POLICY_APPROVED, reason="Approved")

    executor = BoundedRecoveryExecutor(RazorpayTestClient(use_mock_adapter=True))
    res = executor.execute(event, case, RecoveryStrategy.RETRY_NOW)
    assert res.success is True
    assert res.status_code == "EXECUTED"
    assert res.reference_id is not None
    assert case.current_state == CaseState.ACTION_EXECUTED
    assert case.retry_count == 1


def test_executor_graceful_timeout_handling():
    """Verify timeout transitions to EXECUTION_FAILED and sets reconciliation_required without duplicate execution."""
    event = RevenueEvent(
        event_id="evt_exec_to",
        timestamp="2026-08-20T10:00:00Z",
        event_type=EventType.FAILED_PAYMENT,
        merchant_id="mer_test",
        customer_id="cust_2",
        amount=3000.0,
        currency="INR",
        payment_method="UPI",
        failure_reason="TIMEOUT",
        failure_class=FailureClass.GATEWAY_DEGRADATION,
        payment_state="FAILED",
    )
    case = RecoveryCase(
        case_id="case_exec_to",
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

    # Client configured to simulate upstream timeout
    timeout_client = RazorpayTestClient(simulate_timeout=True, use_mock_adapter=True)
    executor = BoundedRecoveryExecutor(timeout_client)
    res = executor.execute(event, case, RecoveryStrategy.RETRY_NOW)

    assert res.success is False
    assert res.status_code == "TIMEOUT"
    assert res.reconciliation_required is True
    assert case.current_state == CaseState.EXECUTION_FAILED
