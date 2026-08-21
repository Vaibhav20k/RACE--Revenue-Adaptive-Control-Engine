"""Candidate strategy generation based on failure telemetry and merchant policy."""

from typing import List
from backend.core.constants import RecoveryStrategy, FailureClass
from backend.domain.events import RevenueEvent


class CandidateStrategyGenerator:
    """Generates eligible candidate recovery strategies for an incoming revenue event."""

    @staticmethod
    def generate_candidates(event: RevenueEvent) -> List[RecoveryStrategy]:
        """Returns a list of allowable candidate strategies based on context."""
        # 1. Hard stopping conditions
        if event.customer_opted_out:
            return [RecoveryStrategy.STOP]

        if event.failure_class in [FailureClass.FRAUD_SUSPECTED, FailureClass.EXPIRED_CARD]:
            return [RecoveryStrategy.STOP]

        # 2. Hard escalation condition
        if event.amount > 50000.0:
            return [RecoveryStrategy.HUMAN_ESCALATION, RecoveryStrategy.STOP]

        # 3. Maximum retry limit exceeded
        if event.retry_count >= 3:
            return [RecoveryStrategy.HUMAN_ESCALATION, RecoveryStrategy.STOP]

        # 4. Contextual candidate generation by failure class
        if event.failure_class == FailureClass.TEMPORARY_NETWORK:
            if event.gateway_route_health == "UP":
                return [RecoveryStrategy.RETRY_NOW, RecoveryStrategy.RETRY_LATER, RecoveryStrategy.STOP]
            else:
                return [RecoveryStrategy.RETRY_LATER, RecoveryStrategy.STOP]

        elif event.failure_class == FailureClass.GATEWAY_DEGRADATION:
            return [RecoveryStrategy.RETRY_LATER, RecoveryStrategy.HUMAN_ESCALATION, RecoveryStrategy.STOP]

        elif event.failure_class == FailureClass.INSUFFICIENT_FUNDS:
            return [RecoveryStrategy.REMINDER_THEN_RETRY, RecoveryStrategy.RETRY_LATER, RecoveryStrategy.STOP]

        elif event.failure_class == FailureClass.AUTH_REQUIRED:
            return [RecoveryStrategy.REMINDER_THEN_RETRY, RecoveryStrategy.STOP]

        elif event.failure_class == FailureClass.CUSTOMER_ABANDONMENT:
            return [RecoveryStrategy.REMINDER_THEN_RETRY, RecoveryStrategy.STOP]

        # Default fallback candidate set
        return [
            RecoveryStrategy.RETRY_NOW,
            RecoveryStrategy.RETRY_LATER,
            RecoveryStrategy.REMINDER_THEN_RETRY,
            RecoveryStrategy.HUMAN_ESCALATION,
            RecoveryStrategy.STOP,
        ]
