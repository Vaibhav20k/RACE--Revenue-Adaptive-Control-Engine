"""Unit tests for Phase 2 deterministic baseline recovery system and state machine."""

import json
import pytest
from pathlib import Path
from backend.core.constants import CaseState, RecoveryStrategy, PolicyDecision
from backend.domain.events import RevenueEvent
from backend.domain.ground_truth import CaseGroundTruth
from backend.recovery.state_machine.states import RecoveryCase
from backend.recovery.state_machine.machine import RecoveryStateMachine, InvalidStateTransitionError
from evaluation.baselines.baseline_a_fixed_retry import BaselineAFixedRetry
from evaluation.baselines.baseline_b_rule_based import BaselineBRuleBased


def test_valid_state_machine_flow():
    """Verify that a standard happy-path progression through the state machine succeeds."""
    case = RecoveryCase(
        case_id="case_test_001",
        event_id="evt_test_001",
        merchant_id="mer_test",
        customer_id="cust_test",
        amount=2500.0,
        failure_reason="NETWORK_ERROR",
        failure_class="TEMPORARY_NETWORK",
    )
    assert case.current_state == CaseState.AT_RISK

    RecoveryStateMachine.transition(case, CaseState.DIAGNOSED, reason="Diagnosis complete")
    assert case.current_state == CaseState.DIAGNOSED

    case.selected_strategy = RecoveryStrategy.RETRY_NOW
    RecoveryStateMachine.transition(case, CaseState.ACTION_SELECTED, reason="Action selected")
    assert case.current_state == CaseState.ACTION_SELECTED

    case.policy_decision = PolicyDecision.APPROVED
    RecoveryStateMachine.transition(case, CaseState.POLICY_APPROVED, reason="Policy check passed")
    assert case.current_state == CaseState.POLICY_APPROVED

    RecoveryStateMachine.transition(case, CaseState.ACTION_EXECUTED, reason="Executed via gateway")
    assert case.current_state == CaseState.ACTION_EXECUTED

    RecoveryStateMachine.transition(case, CaseState.OUTCOME_OBSERVED, reason="Outcome returned")
    assert case.current_state == CaseState.OUTCOME_OBSERVED

    RecoveryStateMachine.transition(case, CaseState.RECOVERED, reason="Payment captured")
    assert case.current_state == CaseState.RECOVERED
    assert len(case.history) == 6


def test_invalid_state_transition_raises_error():
    """Verify that illegal transitions (e.g. AT_RISK -> RECOVERED directly) raise InvalidStateTransitionError."""
    case = RecoveryCase(
        case_id="case_test_002",
        event_id="evt_test_002",
        merchant_id="mer_test",
        customer_id="cust_test",
        amount=1000.0,
        failure_reason="AUTH_FAIL",
        failure_class="AUTH_REQUIRED",
    )
    with pytest.raises(InvalidStateTransitionError):
        RecoveryStateMachine.transition(case, CaseState.RECOVERED, reason="Illegal jump")


def test_baseline_a_evaluation_on_validation_set():
    """Verify that Baseline A runs cleanly on the validation split and produces positive revenue recovery."""
    val_events_path = Path("datasets/validation/revenue_events_validation.json")
    val_gt_path = Path("datasets/validation/ground_truth_validation.json")

    with open(val_events_path, "r", encoding="utf-8") as f:
        events = [RevenueEvent.model_validate(e) for e in json.load(f)]
    with open(val_gt_path, "r", encoding="utf-8") as f:
        ground_truths = [CaseGroundTruth.model_validate(g) for g in json.load(f)]

    report = BaselineAFixedRetry.evaluate_dataset(events, ground_truths)
    assert report["total_cases"] == 200
    assert report["total_recovered_revenue"] > 0.0
    assert report["recovery_rate_pct"] > 0.0
    assert report["total_interventions"] > 0


def test_baseline_b_evaluation_on_validation_set():
    """Verify that Baseline B runs cleanly on the validation split and produces structured metrics."""
    val_events_path = Path("datasets/validation/revenue_events_validation.json")
    val_gt_path = Path("datasets/validation/ground_truth_validation.json")

    with open(val_events_path, "r", encoding="utf-8") as f:
        events = [RevenueEvent.model_validate(e) for e in json.load(f)]
    with open(val_gt_path, "r", encoding="utf-8") as f:
        ground_truths = [CaseGroundTruth.model_validate(g) for g in json.load(f)]

    report = BaselineBRuleBased.evaluate_dataset(events, ground_truths)
    assert report["total_cases"] == 200
    assert report["total_recovered_revenue"] > 0.0
    assert report["recovery_rate_pct"] > 0.0
