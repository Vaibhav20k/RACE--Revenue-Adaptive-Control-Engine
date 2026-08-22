"""Comprehensive test suite for Phase 18: Razorpay Test Mode Integration, Webhooks, and Security Invariants."""

import json
import hmac
import hashlib
from fastapi.testclient import TestClient
from backend.api.app import app
from integrations.razorpay import RazorpayTestClient, RazorpayWebhookHandler
from integrations.razorpay.schemas import RazorpayOrderRequest, RazorpayPaymentLinkRequest
from backend.domain.events import RevenueEvent
from backend.domain.ground_truth import CaseGroundTruth
from backend.core.constants import FailureClass, RecoveryStrategy, CaseState
from backend.recovery.state_machine.states import RecoveryCase
from backend.recovery.state_machine.machine import RecoveryStateMachine
from backend.recovery.execution.executor import BoundedRecoveryExecutor
from backend.recovery.verification.verifier import RecoveryOutcomeVerifier

client = TestClient(app)


def test_req_a_no_credentials_fallback_to_mock():
    """A. No credentials: mock adapter is cleanly selected."""
    mock_client = RazorpayTestClient(key_id="", key_secret="", use_mock_adapter=True)
    assert mock_client.integration_mode == "MOCK"
    assert mock_client.key_id_prefix == "rzp_test_mock"
    
    req = RazorpayOrderRequest(amount=5000, currency="INR", receipt="test_rec_mock")
    resp = mock_client.create_order(req)
    assert resp.status == "created"
    assert "mock" in resp.id.lower()


def test_req_b_test_credentials_selects_test_mode():
    """B. Test credentials configured: TEST_MODE is cleanly selected."""
    test_client = RazorpayTestClient(key_id="rzp_test_samplekey123", key_secret="sample_secret456", use_mock_adapter=False)
    assert test_client.integration_mode == "TEST_MODE"
    assert test_client.key_id_prefix.startswith("rzp_test_")


def test_req_c_policy_rejection_prevents_api_call():
    """C. Policy rejection: when customer opted out, STOP is enforced and no API order created."""
    res = client.post("/api/v1/cases", json={
        "amount": 2500.0,
        "currency": "INR",
        "failure_class": "CUSTOMER_ABANDONMENT",
        "failure_reason": "MODAL_CLOSED_BY_USER",
        "customer_opted_out": True,
    })
    assert res.status_code == 201
    case_id = res.json()["case_id"]

    exec_res = client.post(f"/api/v1/cases/{case_id}/execute")
    assert exec_res.status_code == 200
    data = exec_res.json()
    assert data["executed"] is False
    assert data["status"] == "STOPPED"
    assert data["final_state"] == "STOPPED"
    assert data["post_action_captured"] == 0.0
    assert data["reference_id"] is None


def test_req_d_successful_test_mode_interaction_verified():
    """D. Successful Test Mode interaction: response passed to verifier and recovered."""
    res = client.post("/api/v1/cases", json={
        "amount": 3200.0,
        "currency": "INR",
        "failure_class": "TEMPORARY_NETWORK",
        "failure_reason": "GATEWAY_TIMEOUT",
        "gateway_route_health": "UP",
        "customer_opted_out": False,
    })
    assert res.status_code == 201
    case_id = res.json()["case_id"]

    exec_res = client.post(f"/api/v1/cases/{case_id}/execute")
    assert exec_res.status_code == 200
    data = exec_res.json()
    assert data["is_recovered"] is True
    assert data["final_state"] == "RECOVERED"
    assert data["post_action_captured"] == 3200.0
    assert data["reference_id"] is not None


def test_req_e_failed_payment_outcome():
    """E. Failed payment: verifier transitions state to FAILED/STOPPED rather than RECOVERED."""
    case = RecoveryCase(
        case_id="case_fail_01",
        event_id="evt_fail_01",
        merchant_id="m_01",
        customer_id="c_01",
        amount=1500.0,
        currency="INR",
        failure_reason="DECLINED",
        failure_class="EXPIRED_CARD",
        max_retries=1,
        retry_count=1,
        current_state=CaseState.ACTION_EXECUTED,
    )
    verifier = RecoveryOutcomeVerifier(razorpay_client=RazorpayTestClient(use_mock_adapter=True))
    result = verifier.verify_payment_outcome(case, simulated_status="FAILED", simulated_amount=0.0)
    assert result.is_fully_recovered is False
    assert result.verified_state == "FAILED"
    assert case.current_state == CaseState.STOPPED


def test_req_f_unknown_outcome_reconciliation():
    """F. Unknown outcome: case is placed in reconciliation without premature capture."""
    case = RecoveryCase(
        case_id="case_unknown_01",
        event_id="evt_unknown_01",
        merchant_id="m_01",
        customer_id="c_01",
        amount=1500.0,
        currency="INR",
        failure_reason="TIMEOUT",
        failure_class="UNKNOWN",
        current_state=CaseState.ACTION_EXECUTED,
    )
    verifier = RecoveryOutcomeVerifier(razorpay_client=RazorpayTestClient(use_mock_adapter=True))
    result = verifier.verify_payment_outcome(case, simulated_status="UNKNOWN", simulated_amount=0.0)
    assert result.is_fully_recovered is False
    assert result.verified_state == "UNKNOWN"
    assert case.current_state == CaseState.EXECUTION_FAILED


def test_req_h_invalid_webhook_signature_rejected():
    """H. Invalid webhook signature: rejected with HTTP 400."""
    payload = {"event": "payment.captured", "id": "wh_invalid_sig_01"}
    body_bytes = json.dumps(payload).encode("utf-8")
    
    res = client.post(
        "/api/v1/webhooks/razorpay",
        content=body_bytes,
        headers={"Content-Type": "application/json", "X-Razorpay-Signature": "invalid_hex_signature"},
    )
    assert res.status_code == 400
    assert "Invalid or missing Razorpay webhook signature" in res.json()["detail"]


def test_req_i_j_valid_and_duplicate_webhook_handling():
    """I & J. Valid webhook processed and duplicate webhook handled idempotently."""
    # 1. Create a custom case to correlate with
    case_res = client.post("/api/v1/cases", json={
        "amount": 4500.0,
        "currency": "INR",
        "failure_class": "INSUFFICIENT_FUNDS",
        "failure_reason": "INSUFFICIENT_FUNDS_OR_LIMIT",
    })
    assert case_res.status_code == 201
    case_id = case_res.json()["case_id"]

    webhook_secret = "rzp_test_whsec_race_2026"
    event_id = f"evt_wh_test_{case_id.lower().replace('-', '_')}"
    payload = {
        "event_id": event_id,
        "event": "payment.captured",
        "contains": ["payment"],
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_test_wh_123",
                    "amount": 450000,
                    "currency": "INR",
                    "status": "captured",
                    "notes": {"case_id": case_id},
                }
            }
        }
    }
    raw_body = json.dumps(payload).encode("utf-8")
    signature = hmac.new(webhook_secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()

    # First delivery: Should process successfully
    res1 = client.post(
        "/api/v1/webhooks/razorpay",
        content=raw_body,
        headers={"Content-Type": "application/json", "X-Razorpay-Signature": signature},
    )
    assert res1.status_code == 200
    assert res1.json()["status"] == "processed"
    assert res1.json()["case_id"] == case_id

    # Second delivery (Duplicate): Should be gracefully acknowledged as duplicate
    res2 = client.post(
        "/api/v1/webhooks/razorpay",
        content=raw_body,
        headers={"Content-Type": "application/json", "X-Razorpay-Signature": signature},
    )
    assert res2.status_code == 200
    assert res2.json()["status"] == "ignored_duplicate"


def test_req_k_l_environment_config_and_secret_redaction():
    """K & L. Secrets never exposed in API responses and config endpoint returns safe metadata."""
    res = client.get("/api/v1/config/environment")
    assert res.status_code == 200
    data = res.json()
    assert "mode" in data
    assert data["mode"] in ["TEST_MODE", "MOCK"]
    assert "key_id_prefix" in data
    assert "key_secret" not in data
    assert "secret" not in data
    assert "RAZORPAY_KEY_SECRET" not in json.dumps(data)
