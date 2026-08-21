"""Outcome Verifier inspecting authoritative payment states and calculating verified captured amounts."""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from backend.core.constants import CaseState
from backend.recovery.state_machine.states import RecoveryCase
from backend.recovery.state_machine.machine import RecoveryStateMachine
from integrations.razorpay.client import RazorpayTestClient
from integrations.razorpay.schemas import RazorpayPaymentStatusResponse


@dataclass(frozen=True)
class VerificationResult:
    """Explicit verification record of a payment recovery attempt."""
    case_id: str
    verified_state: str  # "RECOVERED", "FAILED", "PENDING", "UNKNOWN"
    verified_amount_recovered: float
    is_fully_recovered: bool
    reconciliation_notes: str


class RecoveryOutcomeVerifier:
    """Verifies actual payment status post-intervention from gateway telemetry."""

    def __init__(self, razorpay_client: Optional[RazorpayTestClient] = None):
        self.client = razorpay_client or RazorpayTestClient()

    def verify_payment_outcome(
        self,
        case: RecoveryCase,
        payment_id: Optional[str] = None,
        simulated_status: Optional[str] = None,
        simulated_amount: Optional[float] = None,
    ) -> VerificationResult:
        """Verifies payment outcome against gateway or simulated environment."""
        # Step 1: Transition case to OUTCOME_OBSERVED
        if case.current_state == CaseState.ACTION_EXECUTED:
            RecoveryStateMachine.transition(case, CaseState.OUTCOME_OBSERVED, reason="Observing authoritative outcome")

        # Step 2: Resolve status from simulated or API fetch
        if simulated_status is not None:
            status = simulated_status
            amount = simulated_amount or (case.amount if status == "RECOVERED" else 0.0)
        elif payment_id:
            try:
                resp: RazorpayPaymentStatusResponse = self.client.fetch_payment(payment_id)
                if resp.status == "captured":
                    status = "RECOVERED"
                    amount = resp.amount / 100.0
                elif resp.status in ["created", "authorized"]:
                    status = "PENDING"
                    amount = 0.0
                else:
                    status = "FAILED"
                    amount = 0.0
            except Exception:
                status = "UNKNOWN"
                amount = 0.0
        else:
            status = "FAILED"
            amount = 0.0

        is_recovered = (status == "RECOVERED" and amount > 0.0)
        case.actual_outcome = status
        case.recovered_amount = amount

        # Step 3: Transition case to appropriate terminal or retry state
        if is_recovered:
            RecoveryStateMachine.transition(
                case,
                CaseState.RECOVERED,
                reason=f"Authoritatively verified captured amount of INR {amount:.2f}",
            )
            notes = f"Verified recovery: captured INR {amount:.2f}."
        elif status == "UNKNOWN":
            RecoveryStateMachine.transition(
                case,
                CaseState.EXECUTION_FAILED,
                reason="Authoritative status is UNKNOWN; deferred for reconciliation",
            )
            notes = "Payment status could not be verified; action locked to prevent duplicates."
        elif case.retry_count >= case.max_retries:
            RecoveryStateMachine.transition(
                case,
                CaseState.STOPPED,
                reason="Intervention failed and max retry limit reached",
            )
            notes = "Attempt failed; retry budget exhausted."
        else:
            RecoveryStateMachine.transition(
                case,
                CaseState.RETRY_ELIGIBLE,
                reason="Attempt failed but case remains retry-eligible within budget",
            )
            notes = "Attempt failed; remaining retry budget permits further action."

        return VerificationResult(
            case_id=case.case_id,
            verified_state=status,
            verified_amount_recovered=amount,
            is_fully_recovered=is_recovered,
            reconciliation_notes=notes,
        )
