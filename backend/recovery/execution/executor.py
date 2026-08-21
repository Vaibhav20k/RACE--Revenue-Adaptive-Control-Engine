"""Bounded Recovery Action Executor dispatching policy-approved actions through Razorpay."""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from backend.core.constants import RecoveryStrategy, CaseState
from backend.domain.events import RevenueEvent
from backend.recovery.state_machine.states import RecoveryCase
from backend.recovery.state_machine.machine import RecoveryStateMachine
from integrations.razorpay.client import RazorpayTestClient
from integrations.razorpay.schemas import RazorpayOrderRequest, RazorpayPaymentLinkRequest
from integrations.razorpay.errors import RazorpayTimeoutError, RazorpayAPIError


@dataclass(frozen=True)
class ExecutionResult:
    """Structured output from recovery action execution."""
    success: bool
    status_code: str  # "EXECUTED", "TIMEOUT", "GATEWAY_ERROR", "STOPPED", "ESCALATED"
    reference_id: Optional[str]
    error_message: Optional[str]
    reconciliation_required: bool = False


class BoundedRecoveryExecutor:
    """Executes policy-approved recovery actions safely using Razorpay test mode."""

    def __init__(self, razorpay_client: Optional[RazorpayTestClient] = None):
        self.client = razorpay_client or RazorpayTestClient()

    def execute(
        self,
        event: RevenueEvent,
        case: RecoveryCase,
        strategy: RecoveryStrategy,
    ) -> ExecutionResult:
        """Executes the chosen recovery action and updates state machine transitions."""
        amount_paise = int(round(event.amount * 100))

        if strategy == RecoveryStrategy.STOP:
            RecoveryStateMachine.transition(case, CaseState.STOPPED, reason="Action STOP executed")
            return ExecutionResult(
                success=True,
                status_code="STOPPED",
                reference_id=None,
                error_message=None,
            )

        if strategy == RecoveryStrategy.HUMAN_ESCALATION:
            RecoveryStateMachine.transition(case, CaseState.ESCALATED, reason="Human escalation workflow dispatched")
            return ExecutionResult(
                success=True,
                status_code="ESCALATED",
                reference_id=f"esc_{case.case_id}",
                error_message=None,
            )

        # Transition to ACTION_EXECUTED
        case.retry_count += 1
        RecoveryStateMachine.transition(
            case,
            CaseState.ACTION_EXECUTED,
            reason=f"Executing {strategy.value} attempt {case.retry_count}",
        )

        try:
            if strategy in [RecoveryStrategy.RETRY_NOW, RecoveryStrategy.RETRY_LATER]:
                # Prepare test-mode recovery order
                req = RazorpayOrderRequest(
                    amount=amount_paise,
                    currency="INR",
                    receipt=f"rec_{case.case_id}_{case.retry_count}",
                    notes={"case_id": case.case_id, "strategy": strategy.value},
                )
                order_resp = self.client.create_order(req)
                return ExecutionResult(
                    success=True,
                    status_code="EXECUTED",
                    reference_id=order_resp.id,
                    error_message=None,
                )

            elif strategy == RecoveryStrategy.REMINDER_THEN_RETRY:
                # Dispatch payment link / reminder
                req = RazorpayPaymentLinkRequest(
                    amount=amount_paise,
                    currency="INR",
                    description=f"Payment recovery reminder for order {event.order_id or case.case_id}",
                    customer={"name": f"Customer {event.customer_id}", "email": f"{event.customer_id}@example.com"},
                    notes={"case_id": case.case_id, "strategy": strategy.value},
                )
                link_resp = self.client.create_payment_link(req)
                return ExecutionResult(
                    success=True,
                    status_code="EXECUTED",
                    reference_id=link_resp.id,
                    error_message=None,
                )

        except RazorpayTimeoutError as e:
            # Graceful timeout failure: mark state as EXECUTION_FAILED without blindly retrying
            RecoveryStateMachine.transition(
                case,
                CaseState.EXECUTION_FAILED,
                reason="Upstream gateway timeout during action execution",
                metadata={"error": str(e)},
            )
            return ExecutionResult(
                success=False,
                status_code="TIMEOUT",
                reference_id=None,
                error_message=str(e),
                reconciliation_required=True,
            )

        except RazorpayAPIError as e:
            RecoveryStateMachine.transition(
                case,
                CaseState.EXECUTION_FAILED,
                reason="Razorpay API error during execution",
                metadata={"error": str(e)},
            )
            return ExecutionResult(
                success=False,
                status_code="GATEWAY_ERROR",
                reference_id=None,
                error_message=str(e),
                reconciliation_required=False,
            )

        return ExecutionResult(
            success=False,
            status_code="UNKNOWN_ERROR",
            reference_id=None,
            error_message="Unhandled execution path",
        )
