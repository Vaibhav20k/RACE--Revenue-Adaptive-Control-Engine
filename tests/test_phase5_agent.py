"""Unit tests for Phase 5 AI Investigation Agent and Diagnostic Synthesis."""

from backend.domain.events import RevenueEvent
from backend.core.constants import FailureClass, RecoveryStrategy, EventType
from backend.agents.tools import RecoveryContextTools
from backend.agents.investigator import RecoveryInvestigatorAgent
from backend.agents.state import AgentInvestigationState


def test_agent_read_only_tools():
    """Verify tool output structure and field completeness."""
    event = RevenueEvent(
        event_id="evt_tool_test",
        timestamp="2026-08-20T10:00:00Z",
        event_type=EventType.FAILED_PAYMENT,
        merchant_id="mer_saas",
        customer_id="cust_8821",
        amount=3500.0,
        currency="INR",
        payment_method="UPI",
        failure_reason="GATEWAY_503",
        failure_class=FailureClass.GATEWAY_DEGRADATION,
        payment_state="FAILED",
        gateway_route_health="DEGRADED",
    )
    p_ctx = RecoveryContextTools.get_payment_context(event)
    assert p_ctx["event_id"] == "evt_tool_test"
    assert p_ctx["amount"] == 3500.0

    c_ctx = RecoveryContextTools.get_customer_history(event)
    assert c_ctx["customer_id"] == "cust_8821"

    r_ctx = RecoveryContextTools.get_payment_route_health(event)
    assert r_ctx["is_degraded"] is True


def test_agent_investigation_degraded_gateway():
    """Verify that degraded gateway leads to RETRY_LATER recommendation with appropriate reasoning."""
    event = RevenueEvent(
        event_id="evt_agent_gw",
        timestamp="2026-08-20T10:00:00Z",
        event_type=EventType.FAILED_PAYMENT,
        merchant_id="mer_saas",
        customer_id="cust_1234",
        amount=1800.0,
        currency="INR",
        payment_method="UPI",
        failure_reason="ISSUER_DOWN_503",
        failure_class=FailureClass.GATEWAY_DEGRADATION,
        payment_state="FAILED",
        gateway_route_health="DEGRADED",
    )
    state = RecoveryInvestigatorAgent.investigate(event)
    assert isinstance(state, AgentInvestigationState)
    assert state.diagnosis.requires_gateway_recovery is True
    assert state.recommended_strategy == RecoveryStrategy.RETRY_LATER
    assert "Gateway route degraded" in state.recommendation_reason


def test_agent_investigation_customer_action_required():
    """Verify that insufficient funds triggers REMINDER_THEN_RETRY."""
    event = RevenueEvent(
        event_id="evt_agent_funds",
        timestamp="2026-08-20T10:00:00Z",
        event_type=EventType.FAILED_PAYMENT,
        merchant_id="mer_retail",
        customer_id="cust_5678",
        amount=2200.0,
        currency="INR",
        payment_method="CARD",
        failure_reason="INSUFFICIENT_FUNDS",
        failure_class=FailureClass.INSUFFICIENT_FUNDS,
        payment_state="FAILED",
    )
    state = RecoveryInvestigatorAgent.investigate(event)
    assert state.diagnosis.requires_customer_action is True
    assert state.recommended_strategy == RecoveryStrategy.REMINDER_THEN_RETRY


def test_agent_investigation_unrecoverable_fraud():
    """Verify that fraud triggers STOP and is marked unrecoverable."""
    event = RevenueEvent(
        event_id="evt_agent_fraud",
        timestamp="2026-08-20T10:00:00Z",
        event_type=EventType.FAILED_PAYMENT,
        merchant_id="mer_fintech",
        customer_id="cust_9999",
        amount=4000.0,
        currency="INR",
        payment_method="CARD",
        failure_reason="STOLEN_CARD",
        failure_class=FailureClass.FRAUD_SUSPECTED,
        payment_state="FAILED",
    )
    state = RecoveryInvestigatorAgent.investigate(event)
    assert state.diagnosis.is_recoverable is False
    assert state.recommended_strategy == RecoveryStrategy.STOP
