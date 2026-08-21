"""Simulation execution environment for running recovery policies against ground truth."""

from typing import Dict, Any, Tuple
from backend.core.constants import RecoveryStrategy, CaseState
from backend.domain.ground_truth import CaseGroundTruth
from backend.recovery.state_machine.states import RecoveryCase
from backend.recovery.state_machine.machine import RecoveryStateMachine


class RecoverySimulator:
    """Executes actions against the ground truth counterfactual outcome distribution."""

    @staticmethod
    def execute_action(
        case: RecoveryCase,
        strategy: RecoveryStrategy,
        ground_truth: CaseGroundTruth,
    ) -> Tuple[str, float]:
        """Simulates outcome of executing a strategy on a case. Returns (outcome_status, recovered_amount)."""
        strat_key = strategy.value
        cf_table = ground_truth.true_counterfactual_outcomes.get(strat_key)

        if not cf_table:
            return "FAILED", 0.0

        outcome_status = cf_table.get("outcome", "FAILED")
        recovered_amount = float(cf_table.get("recovered_amount", 0.0))
        return outcome_status, recovered_amount
