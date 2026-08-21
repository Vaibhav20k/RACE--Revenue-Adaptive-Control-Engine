"""Ground truth schemas for evaluation (kept strictly separate from runtime agent)."""

from typing import List, Dict, Any
from pydantic import BaseModel, Field
from backend.core.constants import RecoveryStrategy


class CaseGroundTruth(BaseModel):
    """Hidden ground truth values for evaluating decision quality and revenue capture."""
    case_id: str
    event_id: str
    true_revenue_at_risk: float
    true_recoverable_amount: float
    true_optimal_strategy: RecoveryStrategy
    true_counterfactual_outcomes: Dict[str, Dict[str, Any]]
    allowed_actions: List[RecoveryStrategy]
    requires_escalation: bool = False
    is_policy_blocked: bool = False
    scenario_description: str = ""
