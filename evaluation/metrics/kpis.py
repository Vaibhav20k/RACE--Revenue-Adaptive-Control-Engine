"""KPI calculation functions for recovery evaluation."""

from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class BenchmarkReport:
    """Consolidated benchmark report comparing a policy against ground truth."""
    policy_name: str
    total_cases: int
    total_revenue_at_risk: float
    estimated_recoverable_revenue: float
    actual_recovered_revenue: float
    incremental_revenue_vs_baseline_a: float
    recovery_rate_pct: float
    total_interventions: int
    successful_interventions: int
    unnecessary_interventions: int
    escalated_cases: int
    stopped_cases: int
    execution_failures: int
    duplicate_actions: int
    policy_violations: int
    audit_completeness_pct: float
    total_action_cost: float
    cost_per_recovered_rupee: float
    net_recovery_value: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_name": self.policy_name,
            "total_cases": self.total_cases,
            "total_revenue_at_risk": round(self.total_revenue_at_risk, 2),
            "estimated_recoverable_revenue": round(self.estimated_recoverable_revenue, 2),
            "actual_recovered_revenue": round(self.actual_recovered_revenue, 2),
            "incremental_revenue_vs_baseline_a": round(self.incremental_revenue_vs_baseline_a, 2),
            "recovery_rate_pct": round(self.recovery_rate_pct, 2),
            "total_interventions": self.total_interventions,
            "successful_interventions": self.successful_interventions,
            "unnecessary_interventions": self.unnecessary_interventions,
            "escalated_cases": self.escalated_cases,
            "stopped_cases": self.stopped_cases,
            "execution_failures": self.execution_failures,
            "duplicate_actions": self.duplicate_actions,
            "policy_violations": self.policy_violations,
            "audit_completeness_pct": round(self.audit_completeness_pct, 2),
            "total_action_cost": round(self.total_action_cost, 2),
            "cost_per_recovered_rupee": round(self.cost_per_recovered_rupee, 4),
            "net_recovery_value": round(self.net_recovery_value, 2),
        }
