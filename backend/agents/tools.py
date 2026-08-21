"""Read-only diagnostic tools equipped with input/output schemas for the investigation agent."""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from backend.domain.events import RevenueEvent


class PaymentContextQuery(BaseModel):
    event_id: str


class CustomerHistoryQuery(BaseModel):
    customer_id: str


class GatewayHealthQuery(BaseModel):
    payment_method: str


class RecoveryContextTools:
    """Provides validated read-only telemetry queries to the diagnostic agent."""

    @staticmethod
    def get_payment_context(event: RevenueEvent) -> Dict[str, Any]:
        """Extracts granular transaction details and failure signatures."""
        return {
            "event_id": event.event_id,
            "amount": event.amount,
            "currency": event.currency,
            "payment_method": event.payment_method,
            "failure_reason": event.failure_reason,
            "failure_class": event.failure_class.value if hasattr(event.failure_class, "value") else str(event.failure_class),
            "payment_state": event.payment_state,
            "retry_count": event.retry_count,
            "time_since_failure_minutes": event.time_since_failure_minutes,
        }

    @staticmethod
    def get_customer_history(event: RevenueEvent) -> Dict[str, Any]:
        """Queries customer profile, historical recovery rate, and opt-out preferences."""
        return {
            "customer_id": event.customer_id,
            "historical_recovery_rate": event.customer_recovery_history_rate,
            "customer_opted_out": event.customer_opted_out,
            "risk_tier": "HIGH" if event.customer_recovery_history_rate < 0.3 else "NORMAL",
        }

    @staticmethod
    def get_payment_route_health(event: RevenueEvent) -> Dict[str, Any]:
        """Queries upstream gateway operational status and recent latency."""
        return {
            "payment_method": event.payment_method,
            "gateway_status": event.gateway_route_health,
            "is_degraded": event.gateway_route_health.upper() != "UP",
        }

    @staticmethod
    def get_merchant_context(event: RevenueEvent) -> Dict[str, Any]:
        """Queries merchant operational preferences and category tier."""
        return {
            "merchant_id": event.merchant_id,
            "mcc_risk_tier": event.merchant_mcc_tier,
            "max_automated_limit": 50000.0,
        }
