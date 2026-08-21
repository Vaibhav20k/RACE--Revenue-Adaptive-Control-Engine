"""Unit tests for Phase 7 Deterministic Policy Gate and Stopping Controls."""

from backend.domain.events import RevenueEvent
from backend.core.constants import FailureClass, RecoveryStrategy, EventType, PolicyDecision
from backend.recovery.state_machine.states import RecoveryCase
from backend.recovery.policies.gate import PolicyGate


def test_policy_blocks_on_retry_limit_exceeded():
    """Verify that attempting a 4th retry is blocked by policy."""
    event = RevenueEvent(
        event_id="evt_pol_retry",
        timestamp="2026-08-20T10:00:00Z",
        event_type=EventType.FAILED_PAYMENT,
        merchant_id="mer_prime",
        customer_id="cust_111",
        amount=1500.0,
        currency="INR",
        payment_method="UPI",
        failure_reason="NETWORK_TIMEOUT",
        failure_class=FailureClass.TEMPORARY_NETWORK,
        payment_state="FAILED",
    )
    case = RecoveryCase(
        case_id="case_pol_1",
        event_id=event.event_id,
        merchant_id=event.merchant_id,
        customer_id=event.customer_id,
        amount=event.amount,
        failure_reason=event.failure_reason,
        failure_class=event.failure_class.value,
        retry_count=3,  # Already at limit
    )
    result = PolicyGate.evaluate(event, case, RecoveryStrategy.RETRY_NOW)
    assert result.decision == PolicyDecision.BLOCKED
    assert result.is_allowed is False
    assert any("Retry limit" in v for v in result.violations)


def test_policy_escalates_on_high_amount():
    """Verify that an automated action on INR 75,000 transaction triggers ESCALATE_REQUIRED."""
    event = RevenueEvent(
        event_id="evt_pol_high",
        timestamp="2026-08-20T10:00:00Z",
        event_type=EventType.FAILED_PAYMENT,
        merchant_id="mer_prime",
        customer_id="cust_222",
        amount=75000.0,
        currency="INR",
        payment_method="NETBANKING",
        failure_reason="AUTH_TIMEOUT",
        failure_class=FailureClass.AUTH_REQUIRED,
        payment_state="FAILED",
    )
    case = RecoveryCase(
        case_id="case_pol_2",
        event_id=event.event_id,
        merchant_id=event.merchant_id,
        customer_id=event.customer_id,
        amount=event.amount,
        failure_reason=event.failure_reason,
        failure_class=event.failure_class.value,
        retry_count=0,
    )
    result = PolicyGate.evaluate(event, case, RecoveryStrategy.REMINDER_THEN_RETRY)
    assert result.decision == PolicyDecision.ESCALATE_REQUIRED
    assert result.requires_human_approval is True
    assert result.is_allowed is False


def test_policy_blocks_on_customer_opt_out():
    """Verify that customer opt-out blocks any active money intervention."""
    event = RevenueEvent(
        event_id="evt_pol_opt",
        timestamp="2026-08-20T10:00:00Z",
        event_type=EventType.FAILED_PAYMENT,
        merchant_id="mer_prime",
        customer_id="cust_333",
        amount=2000.0,
        currency="INR",
        payment_method="UPI",
        failure_reason="NETWORK_TIMEOUT",
        failure_class=FailureClass.TEMPORARY_NETWORK,
        payment_state="FAILED",
        customer_opted_out=True,
    )
    case = RecoveryCase(
        case_id="case_pol_3",
        event_id=event.event_id,
        merchant_id=event.merchant_id,
        customer_id=event.customer_id,
        amount=event.amount,
        failure_reason=event.failure_reason,
        failure_class=event.failure_class.value,
        retry_count=0,
    )
    result = PolicyGate.evaluate(event, case, RecoveryStrategy.RETRY_NOW)
    assert result.decision == PolicyDecision.BLOCKED
    assert result.is_allowed is False


def test_policy_blocks_on_unknown_payment_state():
    """Verify that unknown payment state halts new payment actions until reconciled."""
    event = RevenueEvent(
        event_id="evt_pol_unk",
        timestamp="2026-08-20T10:00:00Z",
        event_type=EventType.FAILED_PAYMENT,
        merchant_id="mer_prime",
        customer_id="cust_444",
        amount=1000.0,
        currency="INR",
        payment_method="UPI",
        failure_reason="TIMEOUT",
        failure_class=FailureClass.GATEWAY_DEGRADATION,
        payment_state="PENDING",
    )
    case = RecoveryCase(
        case_id="case_pol_4",
        event_id=event.event_id,
        merchant_id=event.merchant_id,
        customer_id=event.customer_id,
        amount=event.amount,
        failure_reason=event.failure_reason,
        failure_class=event.failure_class.value,
        actual_outcome="UNKNOWN",
    )
    result = PolicyGate.evaluate(event, case, RecoveryStrategy.RETRY_LATER)
    assert result.decision == PolicyDecision.BLOCKED
    assert result.is_allowed is False
    assert any("unknown" in v.lower() for v in result.violations)
