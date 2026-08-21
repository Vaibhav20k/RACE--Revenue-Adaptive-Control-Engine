"""Unit tests for Phase 6 Expected Recovery Value (ERV) Engine."""

from backend.domain.events import RevenueEvent
from backend.core.constants import FailureClass, RecoveryStrategy, EventType
from backend.recovery.ranking.erv_engine import ERVEngine, ERVDecision


def test_erv_engine_selects_highest_net_value():
    """Verify that REMINDER_THEN_RETRY wins for insufficient funds with high customer response rate."""
    event = RevenueEvent(
        event_id="evt_erv_funds",
        timestamp="2026-08-20T10:00:00Z",
        event_type=EventType.FAILED_PAYMENT,
        merchant_id="mer_retail",
        customer_id="cust_123",
        amount=5000.0,
        currency="INR",
        payment_method="CARD",
        failure_reason="INSUFFICIENT_FUNDS",
        failure_class=FailureClass.INSUFFICIENT_FUNDS,
        payment_state="FAILED",
        customer_recovery_history_rate=0.85,
    )
    decision = ERVEngine.evaluate_candidates(event)
    assert isinstance(decision, ERVDecision)
    assert decision.best_strategy == RecoveryStrategy.REMINDER_THEN_RETRY
    assert decision.highest_erv > 3000.0
    assert len(decision.candidate_calculations) >= 3


def test_erv_engine_micro_amount_negative_erv_falls_back_to_stop():
    """Verify that a micro-amount (e.g. INR 15.0) where cost > value defaults to STOP."""
    event = RevenueEvent(
        event_id="evt_erv_micro",
        timestamp="2026-08-20T10:00:00Z",
        event_type=EventType.FAILED_PAYMENT,
        merchant_id="mer_retail",
        customer_id="cust_456",
        amount=15.0,
        currency="INR",
        payment_method="WALLET",
        failure_reason="INSUFFICIENT_FUNDS",
        failure_class=FailureClass.INSUFFICIENT_FUNDS,
        payment_state="FAILED",
        customer_recovery_history_rate=0.20,
    )
    decision = ERVEngine.evaluate_candidates(event)
    assert decision.best_strategy == RecoveryStrategy.STOP
    assert decision.highest_erv == 0.0


def test_erv_engine_temporary_network_healthy_route():
    """Verify that RETRY_NOW has top ERV for temporary network blip on healthy route."""
    event = RevenueEvent(
        event_id="evt_erv_net",
        timestamp="2026-08-20T10:00:00Z",
        event_type=EventType.FAILED_PAYMENT,
        merchant_id="mer_prime",
        customer_id="cust_789",
        amount=2500.0,
        currency="INR",
        payment_method="UPI",
        failure_reason="NETWORK_BLIP",
        failure_class=FailureClass.TEMPORARY_NETWORK,
        payment_state="FAILED",
        gateway_route_health="UP",
    )
    decision = ERVEngine.evaluate_candidates(event)
    assert decision.best_strategy == RecoveryStrategy.RETRY_NOW
    assert decision.highest_erv > 2000.0
