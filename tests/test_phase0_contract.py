"""Unit tests verifying Phase 0 repository contract and economic model definitions."""

import pytest
from backend.core.constants import EventType, FailureClass, RecoveryStrategy, CaseState
from backend.core.economics import ERVCalculation, RevenueAccounting
from backend.core.errors import PolicyViolationError, IdempotencyConflictError


def test_constants_and_enums_defined():
    """Verify that all core event types, states, strategies, and failure classes exist."""
    assert EventType.FAILED_PAYMENT == "failed_payment"
    assert FailureClass.TEMPORARY_NETWORK == "TEMPORARY_NETWORK"
    assert RecoveryStrategy.RETRY_LATER == "RETRY_LATER"
    assert CaseState.AT_RISK == "AT_RISK"
    assert CaseState.RECOVERED == "RECOVERED"


def test_erv_calculation_positive():
    """Test standard positive ERV calculation."""
    erv_res = ERVCalculation.calculate(
        strategy="RETRY_LATER",
        recovery_probability=0.6,
        recoverable_amount=5000.0,
        action_cost=5.0,
        friction_penalty=10.0,
        risk_penalty=5.0,
    )
    # Expected: 0.6 * 5000 - 5 - 10 - 5 = 3000 - 20 = 2980.0
    assert erv_res.expected_recovery_value == 2980.0
    assert erv_res.recovery_probability == 0.6
    assert erv_res.recoverable_amount == 5000.0


def test_erv_calculation_negative():
    """Test negative ERV when cost and penalties exceed expected return."""
    erv_res = ERVCalculation.calculate(
        strategy="RETRY_NOW",
        recovery_probability=0.01,
        recoverable_amount=100.0,
        action_cost=5.0,
        friction_penalty=10.0,
        risk_penalty=5.0,
    )
    # Expected: 0.01 * 100 - 20 = 1.0 - 20 = -19.0
    assert erv_res.expected_recovery_value == -19.0


def test_revenue_accounting_metrics():
    """Verify revenue accounting formulas for recovery rate and incremental revenue."""
    ledger = RevenueAccounting(
        revenue_at_risk=100000.0,
        estimated_recoverable_revenue=70000.0,
        actual_recovered_revenue=55000.0,
        baseline_recovered_revenue=40000.0,
    )
    assert ledger.recovery_rate == 55.0
    assert ledger.incremental_recovered_revenue == 15000.0


def test_custom_exceptions():
    """Verify structured exceptions contain expected metadata."""
    err = PolicyViolationError("Retry limit reached", rule="MAX_RETRIES_EXCEEDED")
    assert err.code == "POLICY_VIOLATION"
    assert err.rule == "MAX_RETRIES_EXCEEDED"

    idemp_err = IdempotencyConflictError("Duplicate action", idempotency_key="key_123")
    assert idemp_err.code == "IDEMPOTENCY_CONFLICT"
    assert idemp_err.idempotency_key == "key_123"
