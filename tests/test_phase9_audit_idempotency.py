"""Unit tests for Phase 9 State Machine, Idempotency, and Audit Controls."""

import pytest
from backend.audit.models import AuditRecord
from backend.audit.ledger import AuditLedger
from backend.recovery.idempotency.manager import IdempotencyManager
from backend.core.errors import IdempotencyConflictError


def test_idempotency_manager_duplicate_protection():
    """Verify that duplicate action execution with the same key raises IdempotencyConflictError."""
    mgr = IdempotencyManager()
    key = IdempotencyManager.generate_key(
        merchant_id="mer_101",
        customer_id="cust_202",
        payment_id="pay_303",
        action_type="RETRY_NOW",
        attempt_number=1,
    )
    # First attempt acquires lock
    entry = mgr.acquire_lock(key, case_id="case_101", action_type="RETRY_NOW", attempt_number=1)
    assert entry.action_status == "IN_FLIGHT"

    # Second attempt with identical key must fail
    with pytest.raises(IdempotencyConflictError) as exc_info:
        mgr.acquire_lock(key, case_id="case_101", action_type="RETRY_NOW", attempt_number=1)

    assert exc_info.value.idempotency_key == key


def test_idempotency_manager_completion():
    """Verify recording action completion updates status and references."""
    mgr = IdempotencyManager()
    key = IdempotencyManager.generate_key("mer_1", "cust_1", "pay_1", "RETRY_LATER", 1)
    mgr.acquire_lock(key, "case_1", "RETRY_LATER", 1)
    mgr.record_completion(key, request_reference="order_999", result_reference="pay_rec_999", status="COMPLETED")

    entry = mgr.get_entry(key)
    assert entry is not None
    assert entry.action_status == "COMPLETED"
    assert entry.request_reference == "order_999"


def test_audit_ledger_record_and_explanation():
    """Verify recording an entry in the audit ledger and generating human-readable explanations."""
    ledger = AuditLedger()
    record = AuditRecord(
        audit_id="aud_001",
        workflow_id="wf_001",
        case_id="case_001",
        event_id="evt_001",
        merchant_id="mer_prime",
        customer_id="cust_888",
        revenue_at_risk=4500.0,
        estimated_recoverable_amount=3200.0,
        failure_reason="UPI_TIMEOUT",
        failure_class="TEMPORARY_NETWORK",
        candidate_actions=["RETRY_NOW", "RETRY_LATER", "STOP"],
        selected_action="RETRY_NOW",
        selection_reason="Highest ERV on healthy gateway switch",
        policy_checks=["MAX_RETRIES_OK", "AMOUNT_OK"],
        policy_decision="APPROVED",
        action_status="EXECUTED",
        idempotency_key="key_abc_123",
        request_reference="order_12345",
        outcome="RECOVERED",
        recovered_amount=4500.0,
        from_state="ACTION_SELECTED",
        to_state="RECOVERED",
    )
    ledger.record_entry(record)
    records = ledger.get_records_for_case("case_001")
    assert len(records) == 1
    assert records[0].audit_id == "aud_001"

    explanation = ledger.generate_human_explanation(record)
    assert "Case case_001" in explanation
    assert "INR 4500.00" in explanation
    assert "RETRY_NOW" in explanation
    assert "APPROVED" in explanation
