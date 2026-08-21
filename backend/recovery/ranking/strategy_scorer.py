"""Contextual probability estimation and parameter scoring for recovery strategies."""

from typing import Dict, Optional, TYPE_CHECKING
from backend.core.constants import RecoveryStrategy, FailureClass
from backend.domain.events import RevenueEvent

if TYPE_CHECKING:
    from backend.recovery.learning.statistics_store import StrategyStatisticsStore


class StrategyScorer:
    """Estimates recovery probability P(recovery | context, action) and parameter weights."""

    @staticmethod
    def estimate_strategy_probability(
        event: RevenueEvent,
        strategy: RecoveryStrategy,
        stats_store: Optional["StrategyStatisticsStore"] = None,
    ) -> float:
        """Estimates conditional success probability of applying a strategy to an event."""
        if event.customer_opted_out or event.failure_class in [FailureClass.FRAUD_SUSPECTED, FailureClass.EXPIRED_CARD]:
            if strategy == RecoveryStrategy.STOP:
                return 1.0
            return 0.0

        if strategy == RecoveryStrategy.STOP:
            return 0.0

        fc = event.failure_class.value if hasattr(event.failure_class, "value") else str(event.failure_class)
        cust_rate = float(event.customer_recovery_history_rate)
        is_gw_up = (event.gateway_route_health.upper() == "UP")

        # Baseline contextual prior
        if strategy == RecoveryStrategy.HUMAN_ESCALATION:
            prior_p = min(0.92, 0.50 + 0.40 * cust_rate)
        elif fc == FailureClass.TEMPORARY_NETWORK.value:
            if strategy == RecoveryStrategy.RETRY_NOW:
                prior_p = 0.88 if is_gw_up else 0.15
            elif strategy == RecoveryStrategy.RETRY_LATER:
                prior_p = 0.82
            elif strategy == RecoveryStrategy.REMINDER_THEN_RETRY:
                prior_p = 0.70
            else:
                prior_p = 0.10
        elif fc == FailureClass.INSUFFICIENT_FUNDS.value:
            if strategy == RecoveryStrategy.RETRY_NOW:
                prior_p = 0.12
            elif strategy == RecoveryStrategy.RETRY_LATER:
                prior_p = 0.45
            elif strategy == RecoveryStrategy.REMINDER_THEN_RETRY:
                prior_p = min(0.88, 0.55 + 0.35 * cust_rate)
            else:
                prior_p = 0.10
        elif fc == FailureClass.GATEWAY_DEGRADATION.value:
            if strategy == RecoveryStrategy.RETRY_NOW:
                prior_p = 0.05
            elif strategy == RecoveryStrategy.RETRY_LATER:
                prior_p = 0.82
            elif strategy == RecoveryStrategy.REMINDER_THEN_RETRY:
                prior_p = 0.50
            else:
                prior_p = 0.10
        elif fc == FailureClass.AUTH_REQUIRED.value:
            if strategy == RecoveryStrategy.RETRY_NOW:
                prior_p = 0.08
            elif strategy == RecoveryStrategy.RETRY_LATER:
                prior_p = 0.20
            elif strategy == RecoveryStrategy.REMINDER_THEN_RETRY:
                prior_p = min(0.85, 0.50 + 0.35 * cust_rate)
            else:
                prior_p = 0.10
        elif fc == FailureClass.CUSTOMER_ABANDONMENT.value:
            if strategy == RecoveryStrategy.RETRY_NOW:
                prior_p = 0.02
            elif strategy == RecoveryStrategy.RETRY_LATER:
                prior_p = 0.10
            elif strategy == RecoveryStrategy.REMINDER_THEN_RETRY:
                prior_p = min(0.75, 0.40 + 0.35 * cust_rate)
            else:
                prior_p = 0.10
        else:
            if strategy == RecoveryStrategy.RETRY_NOW:
                prior_p = 0.30
            elif strategy == RecoveryStrategy.RETRY_LATER:
                prior_p = 0.50
            elif strategy == RecoveryStrategy.REMINDER_THEN_RETRY:
                prior_p = 0.60
            else:
                prior_p = 0.10

        # Incorporate closed-loop empirical outcome feedback if available
        if stats_store is not None:
            return stats_store.get_empirical_rate(fc, strategy.value, default=prior_p)

        return prior_p

    @staticmethod
    def get_action_parameters(strategy: RecoveryStrategy, amount: float) -> Dict[str, float]:
        """Returns baseline action cost, friction penalty, and risk penalty in INR."""
        if strategy == RecoveryStrategy.STOP:
            return {"action_cost": 0.0, "friction_penalty": 0.0, "risk_penalty": 0.0}
        
        if strategy == RecoveryStrategy.HUMAN_ESCALATION:
            return {"action_cost": 50.0, "friction_penalty": 5.0, "risk_penalty": 2.0}
        
        if strategy == RecoveryStrategy.REMINDER_THEN_RETRY:
            return {"action_cost": 8.0, "friction_penalty": 15.0, "risk_penalty": 5.0}
        
        if strategy == RecoveryStrategy.RETRY_NOW:
            return {"action_cost": 5.0, "friction_penalty": 8.0, "risk_penalty": 5.0}
        
        if strategy == RecoveryStrategy.RETRY_LATER:
            return {"action_cost": 5.0, "friction_penalty": 5.0, "risk_penalty": 4.0}

        return {"action_cost": 10.0, "friction_penalty": 10.0, "risk_penalty": 10.0}
