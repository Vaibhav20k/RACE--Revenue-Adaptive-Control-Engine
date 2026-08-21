"""State models and state transition records for recovery cases."""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from backend.core.constants import CaseState, RecoveryStrategy, PolicyDecision


class StateTransition(BaseModel):
    """Immutable audit record of a state transition."""
    from_state: CaseState
    to_state: CaseState
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    reason: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RecoveryCase(BaseModel):
    """Complete state container for a revenue recovery case."""
    case_id: str
    event_id: str
    merchant_id: str
    customer_id: str
    amount: float
    currency: str = "INR"
    current_state: CaseState = CaseState.AT_RISK
    failure_reason: str
    failure_class: str
    retry_count: int = 0
    max_retries: int = 3
    selected_strategy: Optional[RecoveryStrategy] = None
    policy_decision: Optional[PolicyDecision] = None
    policy_reason: Optional[str] = None
    actual_outcome: Optional[str] = None
    recovered_amount: float = 0.0
    history: List[StateTransition] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
