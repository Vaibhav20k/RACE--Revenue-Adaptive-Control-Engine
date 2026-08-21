"""AI Recovery Investigator orchestrating structured diagnostic analysis and recommendations."""

from typing import Dict, Any, List
from backend.core.constants import RecoveryStrategy, FailureClass
from backend.domain.events import RevenueEvent
from backend.agents.state import AgentInvestigationState, DiagnosisResult
from backend.agents.tools import RecoveryContextTools
from backend.recovery.diagnosis.synthesizer import DiagnosticSynthesizer
from backend.recovery.ranking.candidate_generator import CandidateStrategyGenerator


class RecoveryInvestigatorAgent:
    """Stateful AI agent that performs root cause analysis and recommends recovery strategies."""

    @classmethod
    def investigate(cls, event: RevenueEvent) -> AgentInvestigationState:
        """Executes a full diagnostic cycle and outputs structured investigation state."""
        # 1. Query context through read-only tools
        p_ctx = RecoveryContextTools.get_payment_context(event)
        c_ctx = RecoveryContextTools.get_customer_history(event)
        r_ctx = RecoveryContextTools.get_payment_route_health(event)
        m_ctx = RecoveryContextTools.get_merchant_context(event)

        context_snapshot = {
            "payment": p_ctx,
            "customer": c_ctx,
            "route": r_ctx,
            "merchant": m_ctx,
        }

        # 2. Synthesize diagnosis
        diagnosis = DiagnosticSynthesizer.synthesize(event)

        # 3. Generate candidate strategies
        candidates = CandidateStrategyGenerator.generate_candidates(event)

        # 4. Evaluate each candidate
        evaluations: Dict[str, str] = {}
        for c in candidates:
            if c == RecoveryStrategy.STOP:
                evaluations[c.value] = "Terminates further interventions to prevent friction and costs."
            elif c == RecoveryStrategy.HUMAN_ESCALATION:
                evaluations[c.value] = "Transfers high-value or ambiguous case to human operations team."
            elif c == RecoveryStrategy.RETRY_NOW:
                evaluations[c.value] = "Immediate retry suitable for transient switch glitches on healthy routes."
            elif c == RecoveryStrategy.RETRY_LATER:
                evaluations[c.value] = "Delayed retry allowing gateway recovery or customer fund replenishment."
            elif c == RecoveryStrategy.REMINDER_THEN_RETRY:
                evaluations[c.value] = "Dispatches permitted customer notification prior to retrying transaction."

        # 5. Select recommended candidate
        escalation_required = False
        if event.amount > 50000.0 or diagnosis.primary_failure_class == FailureClass.UNKNOWN:
            recommended = RecoveryStrategy.HUMAN_ESCALATION
            reason = f"High amount (INR {event.amount:.2f}) or ambiguous telemetry requires human escalation."
            escalation_required = True
        elif not diagnosis.is_recoverable:
            recommended = RecoveryStrategy.STOP
            reason = f"Failure class {diagnosis.primary_failure_class.value} is non-recoverable."
        elif diagnosis.requires_gateway_recovery:
            recommended = RecoveryStrategy.RETRY_LATER
            reason = "Gateway route degraded; delayed retry allows upstream recovery."
        elif diagnosis.requires_customer_action:
            recommended = RecoveryStrategy.REMINDER_THEN_RETRY
            reason = "Customer action required (funds/auth); reminder maximizes recovery likelihood."
        elif diagnosis.is_transient and r_ctx["gateway_status"] == "UP":
            recommended = RecoveryStrategy.RETRY_NOW
            reason = "Transient switch glitch with healthy route permits immediate retry."
        else:
            recommended = RecoveryStrategy.RETRY_LATER
            reason = "Standard cooldown retry recommended."

        return AgentInvestigationState(
            event_id=event.event_id,
            merchant_id=event.merchant_id,
            customer_id=event.customer_id,
            amount=event.amount,
            context_snapshot=context_snapshot,
            diagnosis=diagnosis,
            candidate_strategies=candidates,
            strategy_evaluations=evaluations,
            recommended_strategy=recommended,
            recommendation_reason=reason,
            escalation_required=escalation_required,
        )
