"""Intelligent recovery router classifying route path and dispatching decisions."""

from enum import Enum
from typing import Dict, Any, List
from backend.core.constants import RecoveryStrategy, FailureClass
from backend.domain.events import RevenueEvent
from backend.recovery.ranking.candidate_generator import CandidateStrategyGenerator


class RoutingPath(str, Enum):
    DETERMINISTIC = "DETERMINISTIC"
    AI_REASONING = "AI_REASONING"
    HUMAN_ESCALATION = "HUMAN_ESCALATION"


class RecoveryRouter:
    """Classifies case complexity and determines execution route."""

    @staticmethod
    def determine_routing_path(event: RevenueEvent) -> RoutingPath:
        """Categorizes event into DETERMINISTIC, AI_REASONING, or HUMAN_ESCALATION."""
        # 1. Immediate escalation: high value or ambiguity
        if event.amount > 50000.0:
            return RoutingPath.HUMAN_ESCALATION

        # 2. Immediate deterministic route: clear stop conditions or routine network blips
        if event.customer_opted_out or event.failure_class in [
            FailureClass.FRAUD_SUSPECTED,
            FailureClass.EXPIRED_CARD,
        ]:
            return RoutingPath.DETERMINISTIC

        if event.retry_count >= 3:
            return RoutingPath.HUMAN_ESCALATION

        # 3. Micro amounts where action cost dominates
        if event.amount < 50.0:
            return RoutingPath.DETERMINISTIC

        # 4. Clear routine temporary failures with healthy routes
        if event.failure_class == FailureClass.TEMPORARY_NETWORK and event.gateway_route_health == "UP" and event.retry_count == 0:
            return RoutingPath.DETERMINISTIC

        # 5. All other multi-factor / ambiguous cases route to AI reasoning
        return RoutingPath.AI_REASONING

    @classmethod
    def route_case(cls, event: RevenueEvent) -> Dict[str, Any]:
        """Routes case and returns routing path, candidate strategies, and rationale."""
        path = cls.determine_routing_path(event)
        candidates = CandidateStrategyGenerator.generate_candidates(event)

        if path == RoutingPath.HUMAN_ESCALATION:
            reason = "High value or high operational uncertainty requires human review."
        elif path == RoutingPath.DETERMINISTIC:
            reason = "Standard deterministic rule / policy boundary applied directly."
        else:
            reason = "Multi-factor contextual diagnosis and ERV evaluation required."

        return {
            "routing_path": path.value,
            "candidates": [c.value for c in candidates],
            "reason": reason,
        }
