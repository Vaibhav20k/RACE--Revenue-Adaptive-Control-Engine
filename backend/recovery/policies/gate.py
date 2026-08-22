"""Deterministic Policy Gate enforcing all safety constraints prior to money actions."""

from typing import List, Optional
from backend.core.constants import RecoveryStrategy, PolicyDecision
from backend.domain.events import RevenueEvent
from backend.recovery.state_machine.states import RecoveryCase
from backend.recovery.policies.rules import PolicyRules, PolicyEvaluationResult


class PolicyGate:
    """The authoritative gate for approving, rejecting, or escalating recovery actions."""

    @classmethod
    def evaluate(
        cls,
        event: RevenueEvent,
        case: RecoveryCase,
        proposed_action: RecoveryStrategy,
    ) -> PolicyEvaluationResult:
        """Evaluates proposed action against all invariant policy rules."""
        violations: List[str] = []

        # 1. Check customer opt-out
        opt_err = PolicyRules.check_customer_opt_out(event, proposed_action)
        if opt_err:
            violations.append(opt_err)

        # 2. Check retry limit
        retry_err = PolicyRules.check_retry_limit(case, proposed_action)
        if retry_err:
            violations.append(retry_err)

        # 3. Check payment state
        state_err = PolicyRules.check_payment_state(case, proposed_action)
        if state_err:
            violations.append(state_err)

        # 4. Check amount threshold (requires escalation rather than outright block)
        amt_err = PolicyRules.check_amount_limit(event, proposed_action)
        if amt_err:
            return PolicyEvaluationResult(
                decision=PolicyDecision.ESCALATE_REQUIRED,
                is_allowed=False,
                requires_human_approval=True,
                violations=[amt_err],
                rule_name="MAX_AUTOMATED_AMOUNT_EXCEEDED",
                rationale=f"Proposed action {proposed_action.value} requires human authorization: {amt_err}",
            )

        # If proposed action itself is STOP or customer opted out
        if proposed_action == RecoveryStrategy.STOP or event.customer_opted_out:
            violations_list = ["Customer opted out of automated communications and retries."] if event.customer_opted_out else ["Strategy is non-intervention STOP."]
            return PolicyEvaluationResult(
                decision=PolicyDecision.BLOCKED,
                is_allowed=False,
                requires_human_approval=False,
                violations=violations_list,
                rule_name="POLICY_BLOCKED_STOP",
                rationale="Recovery execution prohibited: Customer opted out or strategy is STOP (no action authorized).",
            )

        # If any hard violations exist
        if violations:
            return PolicyEvaluationResult(
                decision=PolicyDecision.BLOCKED,
                is_allowed=False,
                requires_human_approval=False,
                violations=violations,
                rule_name="POLICY_VIOLATION",
                rationale=f"Action {proposed_action.value} rejected due to policy violations: {'; '.join(violations)}",
            )

        # If proposed action itself is HUMAN_ESCALATION
        if proposed_action == RecoveryStrategy.HUMAN_ESCALATION:
            return PolicyEvaluationResult(
                decision=PolicyDecision.ESCALATE_REQUIRED,
                is_allowed=True,
                requires_human_approval=True,
                violations=[],
                rule_name="EXPLICIT_HUMAN_ESCALATION",
                rationale="Human review workflow approved for execution.",
            )

        # Approved
        return PolicyEvaluationResult(
            decision=PolicyDecision.APPROVED,
            is_allowed=True,
            requires_human_approval=False,
            violations=[],
            rule_name="ALL_POLICIES_PASSED",
            rationale=f"Action {proposed_action.value} cleared all deterministic safety rules.",
        )
