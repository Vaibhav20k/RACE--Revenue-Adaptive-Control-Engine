"""Audit models for storing structured financial decision records."""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class AuditRecord(BaseModel):
    """Complete audit record capturing an end-to-end recovery decision step."""
    audit_id: str
    workflow_id: str
    case_id: str
    event_id: str
    merchant_id: str
    customer_id: str
    revenue_at_risk: float
    estimated_recoverable_amount: float
    failure_reason: str
    failure_class: str
    context_snapshot: Dict[str, Any] = Field(default_factory=dict)
    candidate_actions: List[str] = Field(default_factory=list)
    selected_action: str
    selection_reason: str
    erv_breakdown: Optional[Dict[str, Any]] = None
    policy_checks: List[str] = Field(default_factory=list)
    policy_decision: str
    action_status: str
    idempotency_key: str
    request_reference: Optional[str] = None
    outcome: Optional[str] = None
    recovered_amount: float = 0.0
    from_state: str
    to_state: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
