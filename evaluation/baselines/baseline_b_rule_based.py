"""Baseline B: Rule-Based Recovery Policy. Maps failure codes to static action rules with basic stops."""

from typing import List, Dict, Any
from backend.core.constants import RecoveryStrategy, CaseState, PolicyDecision, FailureClass
from backend.domain.events import RevenueEvent
from backend.domain.ground_truth import CaseGroundTruth
from backend.recovery.state_machine.states import RecoveryCase
from backend.recovery.state_machine.machine import RecoveryStateMachine
from evaluation.baselines.simulator import RecoverySimulator


class BaselineBRuleBased:
    """Baseline B implements deterministic rule lookup for recovery actions."""

    @staticmethod
    def select_strategy(event: RevenueEvent) -> RecoveryStrategy:
        """Deterministic rule lookup mapping."""
        if event.customer_opted_out:
            return RecoveryStrategy.STOP
        if event.amount > 50000.0:
            return RecoveryStrategy.HUMAN_ESCALATION
        if event.failure_class in [FailureClass.FRAUD_SUSPECTED, FailureClass.EXPIRED_CARD]:
            return RecoveryStrategy.STOP
        if event.failure_class == FailureClass.TEMPORARY_NETWORK:
            return RecoveryStrategy.RETRY_NOW
        if event.failure_class == FailureClass.GATEWAY_DEGRADATION:
            return RecoveryStrategy.RETRY_LATER
        if event.failure_class in [FailureClass.INSUFFICIENT_FUNDS, FailureClass.AUTH_REQUIRED, FailureClass.CUSTOMER_ABANDONMENT]:
            return RecoveryStrategy.REMINDER_THEN_RETRY
        return RecoveryStrategy.RETRY_LATER

    @classmethod
    def run_case(cls, event: RevenueEvent, ground_truth: CaseGroundTruth) -> Dict[str, Any]:
        """Runs Baseline B on a single case."""
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
        interventions = 0
        total_cost = 0.0

        if strategy == RecoveryStrategy.STOP:
            RecoveryStateMachine.transition(case, CaseState.STOPPED, reason="Rule-based immediate stop")
            return {
                "case_id": case.case_id,
                "final_state": case.current_state.value,
                "recovered_amount": 0.0,
                "interventions": 0,
                "total_cost": 0.0,
                "is_recovered": False,
            }

        if strategy == RecoveryStrategy.HUMAN_ESCALATION:
            RecoveryStateMachine.transition(case, CaseState.ESCALATED, reason="Rule-based human escalation")
            # Human escalation incurs cost and recovers according to ground truth
            outcome_status, recovered_amount = RecoverySimulator.execute_action(case, strategy, ground_truth)
            case.actual_outcome = outcome_status
            case.recovered_amount = recovered_amount
            is_rec = (outcome_status == "RECOVERED")
            return {
                "case_id": case.case_id,
                "final_state": case.current_state.value,
                "recovered_amount": recovered_amount,
                "interventions": 1,
                "total_cost": 50.0,  # Human review cost
                "is_recovered": is_rec,
            }

        # Automated strategy execution
        RecoveryStateMachine.transition(case, CaseState.DIAGNOSED, reason="Rule mapped diagnosis")
        case.selected_strategy = strategy
        RecoveryStateMachine.transition(case, CaseState.ACTION_SELECTED, reason=f"Selected {strategy.value}")
        case.policy_decision = PolicyDecision.APPROVED
        RecoveryStateMachine.transition(case, CaseState.POLICY_APPROVED, reason="Policy approved")

        interventions += 1
        case.retry_count += 1
        action_cost = 10.0 if strategy == RecoveryStrategy.REMINDER_THEN_RETRY else 5.0
        total_cost += action_cost

        RecoveryStateMachine.transition(case, CaseState.ACTION_EXECUTED, reason="Action executed")
        RecoveryStateMachine.transition(case, CaseState.OUTCOME_OBSERVED, reason="Outcome observed")

        outcome_status, recovered_amount = RecoverySimulator.execute_action(case, strategy, ground_truth)
        case.actual_outcome = outcome_status
        case.recovered_amount = recovered_amount

        if outcome_status == "RECOVERED":
            RecoveryStateMachine.transition(case, CaseState.RECOVERED, reason="Payment recovered")
        else:
            RecoveryStateMachine.transition(case, CaseState.STOPPED, reason="First rule attempt failed, stopping")

        return {
            "case_id": case.case_id,
            "final_state": case.current_state.value,
            "recovered_amount": case.recovered_amount,
            "interventions": interventions,
            "total_cost": total_cost,
            "is_recovered": case.current_state == CaseState.RECOVERED,
        }

    @classmethod
    def evaluate_dataset(
        cls,
        events: List[RevenueEvent],
        ground_truths: List[CaseGroundTruth],
    ) -> Dict[str, Any]:
        """Evaluates Baseline B across a complete dataset split."""
        results = [cls.run_case(e, gt) for e, gt in zip(events, ground_truths)]
        total_risk = sum(e.amount for e in events)
        total_recovered = sum(r["recovered_amount"] for r in results)
        total_interventions = sum(r["interventions"] for r in results)
        total_cost = sum(r["total_cost"] for r in results)
        recovered_cases = sum(1 for r in results if r["is_recovered"])
        total_cases = len(events)

        return {
            "policy": "Baseline B (Rule-Based)",
            "total_cases": total_cases,
            "total_revenue_at_risk": round(total_risk, 2),
            "total_recovered_revenue": round(total_recovered, 2),
            "recovery_rate_pct": round((recovered_cases / total_cases) * 100.0, 2) if total_cases > 0 else 0.0,
            "recovered_cases_count": recovered_cases,
            "total_interventions": total_interventions,
            "total_cost": round(total_cost, 2),
            "cost_per_recovered_rupee": round(total_cost / total_recovered, 4) if total_recovered > 0 else 0.0,
        }
