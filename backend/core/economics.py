"""Economic models and Expected Recovery Value (ERV) definitions for RACE."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class EconomicParameters:
    """Costs and penalty weights for recovery actions."""
    action_cost: float = 5.0
    friction_penalty: float = 10.0
    risk_penalty: float = 5.0


@dataclass(frozen=True)
class ERVCalculation:
    """Explicit breakdown of Expected Recovery Value calculation."""
    strategy: str
    recovery_probability: float
    recoverable_amount: float
    action_cost: float
    friction_penalty: float
    risk_penalty: float
    expected_recovery_value: float

    @classmethod
    def calculate(
        cls,
        strategy: str,
        recovery_probability: float,
        recoverable_amount: float,
        action_cost: float = 5.0,
        friction_penalty: float = 10.0,
        risk_penalty: float = 5.0,
    ) -> "ERVCalculation":
        """Calculates ERV = P(recovery) * recoverable_amount - cost - friction - risk."""
        p = max(0.0, min(1.0, float(recovery_probability)))
        amount = max(0.0, float(recoverable_amount))
        cost = max(0.0, float(action_cost))
        friction = max(0.0, float(friction_penalty))
        risk = max(0.0, float(risk_penalty))

        erv = (p * amount) - cost - friction - risk
        return cls(
            strategy=strategy,
            recovery_probability=round(p, 4),
            recoverable_amount=round(amount, 2),
            action_cost=round(cost, 2),
            friction_penalty=round(friction, 2),
            risk_penalty=round(risk, 2),
            expected_recovery_value=round(erv, 2),
        )


@dataclass
class RevenueAccounting:
    """Revenue metrics ledger for evaluation accounting."""
    revenue_at_risk: float = 0.0
    estimated_recoverable_revenue: float = 0.0
    actual_recovered_revenue: float = 0.0
    baseline_recovered_revenue: float = 0.0

    @property
    def incremental_recovered_revenue(self) -> float:
        """Incremental recovery over baseline."""
        return round(self.actual_recovered_revenue - self.baseline_recovered_revenue, 2)

    @property
    def recovery_rate(self) -> float:
        """Percentage of revenue at risk successfully recovered."""
        if self.revenue_at_risk <= 0.0:
            return 0.0
        return round((self.actual_recovered_revenue / self.revenue_at_risk) * 100.0, 4)
