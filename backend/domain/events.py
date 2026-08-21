"""Event schemas and revenue event models for RACE."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from backend.core.constants import EventType, FailureClass


class RevenueEvent(BaseModel):
    """Authoritative representation of an incoming revenue event."""
    event_id: str
    timestamp: str
    event_type: EventType
    merchant_id: str
    customer_id: str
    order_id: Optional[str] = None
    payment_id: Optional[str] = None
    subscription_id: Optional[str] = None
    amount: float = Field(gt=0, description="Transaction amount in INR")
    currency: str = "INR"
    payment_method: str
    failure_reason: str
    failure_class: FailureClass
    payment_state: str
    retry_count: int = 0
    time_since_failure_minutes: float = 0.0
    customer_recovery_history_rate: float = Field(default=0.5, ge=0.0, le=1.0)
    customer_opted_out: bool = False
    merchant_mcc_tier: str = "medium"
    gateway_route_health: str = "UP"
    metadata: Dict[str, Any] = Field(default_factory=dict)
