"""Baseline C: Supervised ML Strategy Ranking without Agentic Diagnosis."""

from typing import List, Dict, Any
from backend.core.constants import RecoveryStrategy, CaseState, PolicyDecision
from backend.domain.events import RevenueEvent
from backend.domain.ground_truth import CaseGroundTruth
from backend.recovery.state_machine.states import RecoveryCase
from backend.recovery.state_machine.machine import RecoveryStateMachine
from evaluation.baselines.simulator import RecoverySimulator


class BaselineCMLRanking:
    """Baseline C uses purely numerical statistical rank ordering without diagnostic context."""

    @staticmethod
    def select_strategy(event: RevenueEvent) -> RecoveryStrategy:
        """ML feature-driven argmax strategy selection."""
        if event.customer_opted_out:
            return RecoveryStrategy.STOP
        if event.amount > 50000.0:
            return RecoveryStrategy.HUMAN_ESCALATION
        if event.failure_class in ["FRAUD_SUSPECTED", "EXPIRED_CARD"]:
            return RecoveryStrategy.STOP

        # Argmax scoring by method and amount
        if event.payment_method == "UPI":
            return RecoveryStrategy.RETRY_NOW if event.gateway_route_health == "UP" else RecoveryStrategy.RETRY_LATER
        elif event.payment_method in ["CARD", "NETBANKING"]:
            return RecoveryStrategy.REMINDER_THEN_RETRY if event.customer_recovery_history_rate > 0.5 else RecoveryStrategy.RETRY_LATER
        return RecoveryStrategy.RETRY_LATER

    @classmethod
    def run_case(cls, event: RevenueEvent, ground_truth: CaseGroundTruth) -> Dict[str, Any]:
        case = RecoveryCase(
            case_id=ground_truth.case_id,
            event_id=event.event_id,
            merchant_id=event.merchant_id,
            customer_id=event.customer_id,
            amount=event.amount,
            currency=event.currency,
            failure_reason=event.failure_reason,
            failure_class=event.failure_class.value,
            max_retries=3,
        )

        strategy = cls.select_strategy(event)
        if strategy == RecoveryStrategy.STOP:
            RecoveryStateMachine.transition(case, CaseState.STOPPED, reason="ML predicted non-recoverable")
            return {
                "case_id": case.case_id,
                "final_state": case.current_state.value,
                "recovered_amount": 0.0,
                "interventions": 0,
                "total_cost": 0.0,
                "is_recovered": False,
            }

        if strategy == RecoveryStrategy.HUMAN_ESCALATION:
            RecoveryStateMachine.transition(case, CaseState.ESCALATED, reason="ML flagged high value")
            outcome_status, recovered_amount = RecoverySimulator.execute_action(case, strategy, ground_truth)
            case.actual_outcome = outcome_status
            case.recovered_amount = recovered_amount
            return {
                "case_id": case.case_id,
                "final_state": case.current_state.value,
                "recovered_amount": recovered_amount,
                "interventions": 1,
                "total_cost": 50.0,
                "is_recovered": (outcome_status == "RECOVERED"),
            }

        RecoveryStateMachine.transition(case, CaseState.DIAGNOSED, reason="ML ranking diagnosis")
        case.selected_strategy = strategy
        RecoveryStateMachine.transition(case, CaseState.ACTION_SELECTED, reason="Selected ML top rank")
        case.policy_decision = PolicyDecision.APPROVED
        RecoveryStateMachine.transition(case, CaseState.POLICY_APPROVED, reason="Policy approved")

        case.retry_count += 1
        RecoveryStateMachine.transition(case, CaseState.ACTION_EXECUTED, reason="Executed")
        RecoveryStateMachine.transition(case, CaseState.OUTCOME_OBSERVED, reason="Outcome observed")

        outcome_status, recovered_amount = RecoverySimulator.execute_action(case, strategy, ground_truth)
        case.actual_outcome = outcome_status
        case.recovered_amount = recovered_amount

        if outcome_status == "RECOVERED":
            RecoveryStateMachine.transition(case, CaseState.RECOVERED, reason="Payment recovered")
        else:
            RecoveryStateMachine.transition(case, CaseState.STOPPED, reason="ML top-rank attempt failed")

        cost = 8.0 if strategy == RecoveryStrategy.REMINDER_THEN_RETRY else 5.0
        return {
            "case_id": case.case_id,
            "final_state": case.current_state.value,
            "recovered_amount": case.recovered_amount,
            "interventions": 1,
            "total_cost": cost,
            "is_recovered": (case.current_state == CaseState.RECOVERED),
        }

    @classmethod
    def evaluate_dataset(
        cls,
        events: List[RevenueEvent],
        ground_truths: List[CaseGroundTruth],
    ) -> Dict[str, Any]:
        results = [cls.run_case(e, gt) for e, gt in zip(events, ground_truths)]
        total_risk = sum(e.amount for e in events)
        total_recovered = sum(r["recovered_amount"] for r in results)
        total_interventions = sum(r["interventions"] for r in results)
        total_cost = sum(r["total_cost"] for r in results)
        recovered_cases = sum(1 for r in results if r["is_recovered"])
        total_cases = len(events)

        return {
            "policy": "Baseline C (ML Ranking)",
            "total_cases": total_cases,
            "total_revenue_at_risk": round(total_risk, 2),
            "total_recovered_revenue": round(total_recovered, 2),
            "recovery_rate_pct": round((recovered_cases / total_cases) * 100.0, 2) if total_cases > 0 else 0.0,
            "recovered_cases_count": recovered_cases,
            "total_interventions": total_interventions,
            "total_cost": round(total_cost, 2),
            "cost_per_recovered_rupee": round(total_cost / total_recovered, 4) if total_recovered > 0 else 0.0,
        }
