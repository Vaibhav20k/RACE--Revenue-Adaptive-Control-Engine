"""Structured state models for the AI investigation agent."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from backend.core.constants import RecoveryStrategy, FailureClass


class DiagnosisResult(BaseModel):
    """Structured diagnostic synthesis produced by the agent."""
    primary_failure_class: FailureClass
    root_cause_explanation: str
    is_transient: bool
    is_recoverable: bool
    requires_customer_action: bool
    requires_gateway_recovery: bool
    confidence_score: float = Field(ge=0.0, le=1.0)


class AgentInvestigationState(BaseModel):
    """Explicit state container for an investigation lifecycle."""
    event_id: str
    merchant_id: str
    customer_id: str
    amount: float
    context_snapshot: Dict[str, Any] = Field(default_factory=dict)
    diagnosis: Optional[DiagnosisResult] = None
    candidate_strategies: List[RecoveryStrategy] = Field(default_factory=list)
    strategy_evaluations: Dict[str, str] = Field(default_factory=dict)
    recommended_strategy: Optional[RecoveryStrategy] = None
    recommendation_reason: Optional[str] = None
    escalation_required: bool = False
