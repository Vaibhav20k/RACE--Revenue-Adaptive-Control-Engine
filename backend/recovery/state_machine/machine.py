"""State machine engine enforcing valid recovery case transitions."""

from datetime import datetime, timezone
from typing import Optional, Set, Dict
from backend.core.constants import CaseState
from backend.core.errors import RACEError
from backend.recovery.state_machine.states import RecoveryCase, StateTransition


# Explicit valid transitions table
VALID_TRANSITIONS: Dict[CaseState, Set[CaseState]] = {
    CaseState.AT_RISK: {CaseState.DIAGNOSED, CaseState.STOPPED, CaseState.ESCALATED},
    CaseState.DIAGNOSED: {CaseState.ACTION_SELECTED, CaseState.STOPPED, CaseState.ESCALATED},
    CaseState.ACTION_SELECTED: {CaseState.POLICY_APPROVED, CaseState.STOPPED, CaseState.ESCALATED},
    CaseState.POLICY_APPROVED: {CaseState.ACTION_EXECUTED, CaseState.EXECUTION_FAILED, CaseState.STOPPED},
    CaseState.ACTION_EXECUTED: {CaseState.OUTCOME_OBSERVED},
    CaseState.OUTCOME_OBSERVED: {
        CaseState.RECOVERED,
        CaseState.RETRY_ELIGIBLE,
        CaseState.STOPPED,
        CaseState.ESCALATED,
        CaseState.EXECUTION_FAILED,
    },
    CaseState.RETRY_ELIGIBLE: {CaseState.DIAGNOSED, CaseState.ACTION_SELECTED, CaseState.STOPPED, CaseState.ESCALATED},
    CaseState.EXECUTION_FAILED: {CaseState.ESCALATED, CaseState.STOPPED, CaseState.RETRY_ELIGIBLE},
    # Terminal states
    CaseState.RECOVERED: set(),
    CaseState.STOPPED: set(),
    CaseState.ESCALATED: set(),
}


class InvalidStateTransitionError(RACEError):
    """Raised when an illegal state transition is attempted."""
    def __init__(self, from_state: CaseState, to_state: CaseState):
        super().__init__(
            f"Invalid transition from {from_state.value} to {to_state.value}",
            code="INVALID_STATE_TRANSITION",
        )
        self.from_state = from_state
        self.to_state = to_state


class RecoveryStateMachine:
    """Controls and validates lifecycle state changes on a RecoveryCase."""

    @staticmethod
    def transition(
        case: RecoveryCase,
        to_state: CaseState,
        reason: str,
        metadata: Optional[dict] = None,
    ) -> RecoveryCase:
        """Transitions a case to the target state if allowed by the state machine."""
        allowed_targets = VALID_TRANSITIONS.get(case.current_state, set())
        if to_state not in allowed_targets:
            raise InvalidStateTransitionError(case.current_state, to_state)

        record = StateTransition(
            from_state=case.current_state,
            to_state=to_state,
            timestamp=datetime.now(timezone.utc).isoformat(),
            reason=reason,
            metadata=metadata or {},
        )
        case.history.append(record)
        case.current_state = to_state
        case.updated_at = datetime.now(timezone.utc).isoformat()
        return case
