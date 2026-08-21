"""Diagnostic synthesizer aggregating context into root-cause assessment."""

from backend.core.constants import FailureClass
from backend.domain.events import RevenueEvent
from backend.agents.state import DiagnosisResult
from backend.agents.tools import RecoveryContextTools


class DiagnosticSynthesizer:
    """Synthesizes structured telemetry and context into a formal diagnosis."""

    @classmethod
    def synthesize(cls, event: RevenueEvent) -> DiagnosisResult:
        """Evaluates event context and generates explicit diagnosis with evidence."""
        p_ctx = RecoveryContextTools.get_payment_context(event)
        c_ctx = RecoveryContextTools.get_customer_history(event)
        r_ctx = RecoveryContextTools.get_payment_route_health(event)

        fc = event.failure_class
        fc_val = fc.value if hasattr(fc, "value") else str(fc)

        if c_ctx["customer_opted_out"]:
            return DiagnosisResult(
                primary_failure_class=FailureClass.CUSTOMER_ABANDONMENT,
                root_cause_explanation="Customer has explicitly opted out of communications and automated retries.",
                is_transient=False,
                is_recoverable=False,
                requires_customer_action=False,
                requires_gateway_recovery=False,
                confidence_score=0.99,
            )

        if fc_val == FailureClass.FRAUD_SUSPECTED.value:
            return DiagnosisResult(
                primary_failure_class=FailureClass.FRAUD_SUSPECTED,
                root_cause_explanation="Security / risk engine flagged instrument for suspected fraud.",
                is_transient=False,
                is_recoverable=False,
                requires_customer_action=False,
                requires_gateway_recovery=False,
                confidence_score=0.95,
            )

        if fc_val == FailureClass.EXPIRED_CARD.value:
            return DiagnosisResult(
                primary_failure_class=FailureClass.EXPIRED_CARD,
                root_cause_explanation="Payment instrument is permanently expired or cancelled by issuing bank.",
                is_transient=False,
                is_recoverable=False,
                requires_customer_action=True,
                requires_gateway_recovery=False,
                confidence_score=0.95,
            )

        if r_ctx["is_degraded"] or fc_val == FailureClass.GATEWAY_DEGRADATION.value:
            return DiagnosisResult(
                primary_failure_class=FailureClass.GATEWAY_DEGRADATION,
                root_cause_explanation="Upstream gateway or issuer switch is experiencing temporary degradation (HTTP 503/504).",
                is_transient=True,
                is_recoverable=True,
                requires_customer_action=False,
                requires_gateway_recovery=True,
                confidence_score=0.90,
            )

        if fc_val == FailureClass.TEMPORARY_NETWORK.value:
            return DiagnosisResult(
                primary_failure_class=FailureClass.TEMPORARY_NETWORK,
                root_cause_explanation="Transient network glitch or communication timeout during payment processing.",
                is_transient=True,
                is_recoverable=True,
                requires_customer_action=False,
                requires_gateway_recovery=False,
                confidence_score=0.88,
            )

        if fc_val in [FailureClass.INSUFFICIENT_FUNDS.value, FailureClass.AUTH_REQUIRED.value]:
            return DiagnosisResult(
                primary_failure_class=FailureClass(fc_val),
                root_cause_explanation="Customer action required (balance top-up, card limit adjustment, or 3DS authentication approval).",
                is_transient=True,
                is_recoverable=True,
                requires_customer_action=True,
                requires_gateway_recovery=False,
                confidence_score=0.85,
            )

        if fc_val == FailureClass.CUSTOMER_ABANDONMENT.value:
            return DiagnosisResult(
                primary_failure_class=FailureClass.CUSTOMER_ABANDONMENT,
                root_cause_explanation="Customer dropped off during checkout workflow before completing authorization.",
                is_transient=True,
                is_recoverable=True,
                requires_customer_action=True,
                requires_gateway_recovery=False,
                confidence_score=0.80,
            )

        return DiagnosisResult(
            primary_failure_class=FailureClass.UNKNOWN,
            root_cause_explanation="Ambiguous failure telemetry requires multi-factor investigation or human escalation.",
            is_transient=False,
            is_recoverable=True,
            requires_customer_action=False,
            requires_gateway_recovery=False,
            confidence_score=0.50,
        )
