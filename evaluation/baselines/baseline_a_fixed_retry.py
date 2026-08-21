"""Baseline A: Fixed Retry Policy. Retries all failed payments after fixed delay up to max attempts."""

from typing import List, Dict, Any
from backend.core.constants import RecoveryStrategy, CaseState, PolicyDecision
from backend.domain.events import RevenueEvent
from backend.domain.ground_truth import CaseGroundTruth
from backend.recovery.state_machine.states import RecoveryCase
from backend.recovery.state_machine.machine import RecoveryStateMachine
from evaluation.baselines.simulator import RecoverySimulator


class BaselineAFixedRetry:
    """Baseline A implements naive fixed-retry logic."""

    @staticmethod
    def run_case(event: RevenueEvent, ground_truth: CaseGroundTruth) -> Dict[str, Any]:
        """Runs Baseline A on a single case."""
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

        interventions = 0
        total_cost = 0.0
        action_cost_per_retry = 5.0

        # Baseline A naively selects RETRY_LATER if retry_count < 3
        while case.retry_count < case.max_retries and case.current_state not in [
            CaseState.RECOVERED,
            CaseState.STOPPED,
            CaseState.ESCALATED,
        ]:
            # Step 1: Diagnose (dummy in naive baseline)
            RecoveryStateMachine.transition(case, CaseState.DIAGNOSED, reason="Naive fixed-retry diagnosis")

            # Step 2: Select Action
            case.selected_strategy = RecoveryStrategy.RETRY_LATER
            RecoveryStateMachine.transition(case, CaseState.ACTION_SELECTED, reason="Fixed retry scheduled")

            # Step 3: Policy approval (Naive check)
            case.policy_decision = PolicyDecision.APPROVED
            RecoveryStateMachine.transition(case, CaseState.POLICY_APPROVED, reason="Fixed retry approved")

            # Step 4: Execute
            interventions += 1
            case.retry_count += 1
            total_cost += action_cost_per_retry
            RecoveryStateMachine.transition(case, CaseState.ACTION_EXECUTED, reason=f"Attempt {case.retry_count} executed")

            # Step 5: Observe outcome
            RecoveryStateMachine.transition(case, CaseState.OUTCOME_OBSERVED, reason="Gateway state observed")
            outcome_status, recovered_amount = RecoverySimulator.execute_action(
                case, case.selected_strategy, ground_truth
            )

            case.actual_outcome = outcome_status
            case.recovered_amount = recovered_amount

            if outcome_status == "RECOVERED":
                RecoveryStateMachine.transition(case, CaseState.RECOVERED, reason="Payment successfully captured")
                break
            elif case.retry_count >= case.max_retries:
                RecoveryStateMachine.transition(case, CaseState.STOPPED, reason="Max retry limit reached")
                break
            else:
                RecoveryStateMachine.transition(case, CaseState.RETRY_ELIGIBLE, reason="Retry failed, eligible for next loop")

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
        """Evaluates Baseline A across a complete dataset split."""
        results = [cls.run_case(e, gt) for e, gt in zip(events, ground_truths)]
        total_risk = sum(e.amount for e in events)
        total_recovered = sum(r["recovered_amount"] for r in results)
        total_interventions = sum(r["interventions"] for r in results)
        total_cost = sum(r["total_cost"] for r in results)
        recovered_cases = sum(1 for r in results if r["is_recovered"])
        total_cases = len(events)

        return {
            "policy": "Baseline A (Fixed Retry)",
            "total_cases": total_cases,
            "total_revenue_at_risk": round(total_risk, 2),
            "total_recovered_revenue": round(total_recovered, 2),
            "recovery_rate_pct": round((recovered_cases / total_cases) * 100.0, 2) if total_cases > 0 else 0.0,
            "recovered_cases_count": recovered_cases,
            "total_interventions": total_interventions,
            "total_cost": round(total_cost, 2),
            "cost_per_recovered_rupee": round(total_cost / total_recovered, 4) if total_recovered > 0 else 0.0,
        }
