"""Policy rule definitions and deterministic validation checks."""

from dataclasses import dataclass
from typing import Optional, List
from backend.core.constants import RecoveryStrategy, PolicyDecision
from backend.core.errors import PolicyViolationError
from backend.domain.events import RevenueEvent
from backend.recovery.state_machine.states import RecoveryCase


@dataclass(frozen=True)
class PolicyEvaluationResult:
    """Explicit result of policy validation checks."""
    decision: PolicyDecision
    is_allowed: bool
    requires_human_approval: bool
    violations: List[str]
    rule_name: str
    rationale: str


class PolicyRules:
    """Collection of invariant financial and operational safety rules."""

    MAX_RETRIES: int = 3
    MAX_AUTOMATED_AMOUNT_INR: float = 50000.0
    MIN_COOLDOWN_MINUTES: float = 30.0
    MAX_RECOVERY_WINDOW_HOURS: float = 72.0

    @classmethod
    def check_retry_limit(cls, case: RecoveryCase, action: RecoveryStrategy) -> Optional[str]:
        """Validates that automated retry attempt count has not exceeded limit."""
        if action in [RecoveryStrategy.RETRY_NOW, RecoveryStrategy.RETRY_LATER, RecoveryStrategy.REMINDER_THEN_RETRY]:
            if case.retry_count >= cls.MAX_RETRIES:
                return f"Retry limit of {cls.MAX_RETRIES} attempts exceeded (current attempts: {case.retry_count})."
        return None

    @classmethod
    def check_amount_limit(cls, event: RevenueEvent, action: RecoveryStrategy) -> Optional[str]:
        """Validates that amount does not exceed automated execution threshold."""
        if action in [RecoveryStrategy.RETRY_NOW, RecoveryStrategy.RETRY_LATER, RecoveryStrategy.REMINDER_THEN_RETRY]:
            if event.amount > cls.MAX_AUTOMATED_AMOUNT_INR:
                return f"Amount INR {event.amount:.2f} exceeds maximum automated limit INR {cls.MAX_AUTOMATED_AMOUNT_INR:.2f}."
        return None

    @classmethod
    def check_customer_opt_out(cls, event: RevenueEvent, action: RecoveryStrategy) -> Optional[str]:
        """Validates customer communication and retry preferences."""
        if event.customer_opted_out and action != RecoveryStrategy.STOP:
            return "Customer has opted out of automated communications and retries."
        return None

    @classmethod
    def check_payment_state(cls, case: RecoveryCase, action: RecoveryStrategy) -> Optional[str]:
        """Validates that payment is in an actionable state."""
        if case.actual_outcome == "PAID" or case.recovered_amount > 0.0:
            return "Payment has already been successfully recovered."
        if case.actual_outcome == "UNKNOWN":
            return "Payment state is currently unknown; state reconciliation required before new action."
        return None
