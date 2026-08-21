"""Unit tests for Phase 11 Closed-Loop Outcome Learning."""

from backend.core.constants import CaseState, RecoveryStrategy, FailureClass, EventType
from backend.domain.events import RevenueEvent
from backend.recovery.state_machine.states import RecoveryCase
from backend.recovery.learning.statistics_store import StrategyStatisticsStore
from backend.recovery.learning.closed_loop import ClosedLoopLearningEngine
from backend.recovery.ranking.erv_engine import ERVEngine


def test_statistics_store_record_and_smoothing():
    """Verify recording multiple outcomes updates counts, revenue, and smoothed empirical rates."""
    store = StrategyStatisticsStore()
    
    for _ in range(4):
        store.record_outcome(
            failure_class="TEMPORARY_NETWORK",
            strategy="RETRY_NOW",
            expected_value=1500.0,
            actual_recovered_amount=2000.0,
            is_success=True,
        )

    bucket = store._store[("TEMPORARY_NETWORK", "RETRY_NOW")]
    assert bucket.sample_count == 4
    assert bucket.success_count == 4
    assert bucket.total_recovered_amount == 8000.0
    assert bucket.empirical_success_rate == 1.0

    rate = store.get_empirical_rate("TEMPORARY_NETWORK", "RETRY_NOW", default=0.5)
    assert rate > 0.70


def test_closed_loop_engine_updates_from_case():
    """Verify that ClosedLoopLearningEngine updates stats directly from RecoveryCase."""
    store = StrategyStatisticsStore()
    engine = ClosedLoopLearningEngine(store)

    case = RecoveryCase(
        case_id="case_learn_1",
        event_id="evt_learn_1",
        merchant_id="mer_test",
        customer_id="cust_test",
        amount=3000.0,
        failure_reason="INSUFFICIENT_FUNDS",
        failure_class="INSUFFICIENT_FUNDS",
        selected_strategy=RecoveryStrategy.REMINDER_THEN_RETRY,
        current_state=CaseState.RECOVERED,
        recovered_amount=3000.0,
    )
    engine.update_from_case(case, expected_value=2400.0)

    buckets = store.get_all_buckets()
    assert "INSUFFICIENT_FUNDS:REMINDER_THEN_RETRY" in buckets
    data = buckets["INSUFFICIENT_FUNDS:REMINDER_THEN_RETRY"]
    assert data["sample_count"] == 1
    assert data["success_count"] == 1
    assert data["total_recovered_amount"] == 3000.0


def test_closed_loop_feedback_changes_subsequent_erv_decision():
    """Verify that repeated failure observations dynamically lower ERV and change strategy ranking."""
    store = StrategyStatisticsStore()
    event = RevenueEvent(
        event_id="evt_learn_dyn",
        timestamp="2026-08-20T10:00:00Z",
        event_type=EventType.FAILED_PAYMENT,
        merchant_id="mer_test",
        customer_id="cust_dyn",
        amount=1500.0,
        currency="INR",
        payment_method="UPI",
        failure_reason="SWITCH_BLIP",
        failure_class=FailureClass.TEMPORARY_NETWORK,
        payment_state="FAILED",
        gateway_route_health="UP",
    )

    # Initial decision without prior negative feedback chooses RETRY_NOW
    initial_decision = ERVEngine.evaluate_candidates(event, stats_store=store)
    assert initial_decision.best_strategy == RecoveryStrategy.RETRY_NOW

    # Observe 5 repeated failures on RETRY_NOW for TEMPORARY_NETWORK
    for _ in range(5):
        store.record_outcome(
            failure_class="TEMPORARY_NETWORK",
            strategy="RETRY_NOW",
            expected_value=1200.0,
            actual_recovered_amount=0.0,
            is_success=False,
        )

    # Also observe 4 successes on RETRY_LATER
    for _ in range(4):
        store.record_outcome(
            failure_class="TEMPORARY_NETWORK",
            strategy="RETRY_LATER",
            expected_value=1200.0,
            actual_recovered_amount=1500.0,
            is_success=True,
        )

    # Subsequent decision with updated feedback shifts ranking to RETRY_LATER
    updated_decision = ERVEngine.evaluate_candidates(event, stats_store=store)
    assert updated_decision.best_strategy == RecoveryStrategy.RETRY_LATER
    assert updated_decision.highest_erv > 0.0
