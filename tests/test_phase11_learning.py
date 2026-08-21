"""Unit tests for Phase 11 Closed-Loop Outcome Learning."""

from backend.core.constants import CaseState, RecoveryStrategy
from backend.recovery.state_machine.states import RecoveryCase
from backend.recovery.learning.statistics_store import StrategyStatisticsStore
from backend.recovery.learning.closed_loop import ClosedLoopLearningEngine


def test_statistics_store_record_and_smoothing():
    """Verify recording multiple outcomes updates counts, revenue, and smoothed empirical rates."""
    store = StrategyStatisticsStore()
    
    # Record 4 successful attempts
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

    # Test smoothed retrieval
    rate = store.get_empirical_rate("TEMPORARY_NETWORK", "RETRY_NOW", default=0.5)
    # With 4 successes + (0.5 * 3 prior) / (4 + 3) = (4 + 1.5)/7 = 5.5/7 ≈ 0.7857
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
