"""Unit tests for Phase 4 Dynamic Recovery Router and Candidate Strategy Generation."""

from backend.domain.events import RevenueEvent
from backend.core.constants import FailureClass, RecoveryStrategy, EventType
from backend.recovery.ranking.candidate_generator import CandidateStrategyGenerator
from backend.recovery.routing.router import RecoveryRouter, RoutingPath


def test_opt_out_routes_deterministic_stop():
    """Verify that an opted-out customer yields only STOP and routes deterministically."""
    event = RevenueEvent(
        event_id="evt_opt_out",
        timestamp="2026-08-20T10:00:00Z",
        event_type=EventType.FAILED_PAYMENT,
        merchant_id="mer_test",
        customer_id="cust_test",
        amount=1200.0,
        currency="INR",
        payment_method="UPI",
        failure_reason="CUSTOMER_OPT_OUT",
        failure_class=FailureClass.CUSTOMER_ABANDONMENT,
        payment_state="FAILED",
        customer_opted_out=True,
    )
    candidates = CandidateStrategyGenerator.generate_candidates(event)
    assert candidates == [RecoveryStrategy.STOP]

    route_info = RecoveryRouter.route_case(event)
    assert route_info["routing_path"] == RoutingPath.DETERMINISTIC.value
    assert route_info["candidates"] == ["STOP"]


def test_high_value_routes_human_escalation():
    """Verify that a transaction > 50,000 INR routes to HUMAN_ESCALATION."""
    event = RevenueEvent(
        event_id="evt_high_val",
        timestamp="2026-08-20T10:00:00Z",
        event_type=EventType.FAILED_PAYMENT,
        merchant_id="mer_test",
        customer_id="cust_test",
        amount=75000.0,
        currency="INR",
        payment_method="NETBANKING",
        failure_reason="LIMIT_EXCEEDED",
        failure_class=FailureClass.UNKNOWN,
        payment_state="FAILED",
    )
    candidates = CandidateStrategyGenerator.generate_candidates(event)
    assert RecoveryStrategy.HUMAN_ESCALATION in candidates

    route_info = RecoveryRouter.route_case(event)
    assert route_info["routing_path"] == RoutingPath.HUMAN_ESCALATION.value


def test_degraded_gateway_excludes_retry_now():
    """Verify that gateway degradation excludes RETRY_NOW and includes RETRY_LATER."""
    event = RevenueEvent(
        event_id="evt_gw_down",
        timestamp="2026-08-20T10:00:00Z",
        event_type=EventType.FAILED_PAYMENT,
        merchant_id="mer_test",
        customer_id="cust_test",
        amount=3400.0,
        currency="INR",
        payment_method="UPI",
        failure_reason="GATEWAY_503",
        failure_class=FailureClass.GATEWAY_DEGRADATION,
        payment_state="FAILED",
        gateway_route_health="DEGRADED",
    )
    candidates = CandidateStrategyGenerator.generate_candidates(event)
    assert RecoveryStrategy.RETRY_NOW not in candidates
    assert RecoveryStrategy.RETRY_LATER in candidates


def test_insufficient_funds_includes_reminder_then_retry():
    """Verify that insufficient funds failure offers reminder then retry."""
    event = RevenueEvent(
        event_id="evt_low_funds",
        timestamp="2026-08-20T10:00:00Z",
        event_type=EventType.FAILED_PAYMENT,
        merchant_id="mer_test",
        customer_id="cust_test",
        amount=1500.0,
        currency="INR",
        payment_method="CARD",
        failure_reason="INSUFFICIENT_BALANCE",
        failure_class=FailureClass.INSUFFICIENT_FUNDS,
        payment_state="FAILED",
    )
    candidates = CandidateStrategyGenerator.generate_candidates(event)
    assert RecoveryStrategy.REMINDER_THEN_RETRY in candidates
    assert RecoveryStrategy.RETRY_LATER in candidates
