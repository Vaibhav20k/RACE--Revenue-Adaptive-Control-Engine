"""Closed-loop controller orchestrating outcome observation and feedback into future decisions."""

from typing import Optional
from backend.core.constants import CaseState
from backend.recovery.state_machine.states import RecoveryCase
from backend.recovery.learning.statistics_store import StrategyStatisticsStore


class ClosedLoopLearningEngine:
    """Integrates observed outcomes into future probabilistic estimations."""

    def __init__(self, stats_store: Optional[StrategyStatisticsStore] = None):
        self.stats_store = stats_store or StrategyStatisticsStore()

    def update_from_case(self, case: RecoveryCase, expected_value: float) -> None:
        """Extracts outcome metrics from completed case and updates statistics store."""
        if not case.selected_strategy:
            return

        strat_val = case.selected_strategy.value if hasattr(case.selected_strategy, "value") else str(case.selected_strategy)
        # STOP and non-execution decisions must never be counted as recovery attempts
        if strat_val == "STOP" or case.current_state in [CaseState.STOPPED, CaseState.ESCALATED]:
            return

        is_success = (case.current_state == CaseState.RECOVERED and case.recovered_amount > 0.0)
        self.stats_store.record_outcome(
            failure_class=case.failure_class,
            strategy=strat_val,
            expected_value=expected_value,
            actual_recovered_amount=case.recovered_amount,
            is_success=is_success,
        )

