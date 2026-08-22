"""Live production-like verification script testing the live running uvicorn server on port 8000."""

import json
import urllib.request

base_url = "http://127.0.0.1:8000"

def run_live_verification():
    print("============================================================")
    print("LIVE PRODUCTION-LIKE VERIFICATION ON PORT 8000")
    print("============================================================")

    # 1. Check Root HTML
    print("\n[STEP 1] Checking HTML DOM template...")
    req_html = urllib.request.Request(base_url + "/")
    with urllib.request.urlopen(req_html) as resp:
        html_content = resp.read().decode("utf-8")
        assert 'badge-recovered">ACTION APPROVED' not in html_content
        print("[PASS] HTML verified: No static ACTION APPROVED badge.")

    # 2. Check Environment Config
    print("\n[STEP 2] Checking runtime environment config...")
    req_env = urllib.request.Request(base_url + "/api/v1/config/environment")
    with urllib.request.urlopen(req_env) as resp:
        env_data = json.loads(resp.read().decode("utf-8"))
        print(f"[PASS] Mode: {env_data.get('mode')} | Key Prefix: {env_data.get('key_id_prefix')}")

    # 3. Create Live Custom Case
    print("\n[STEP 3] Creating brand new opt-out scenario...")
    payload = {
        "amount": 4200.0,
        "currency": "INR",
        "failure_class": "INSUFFICIENT_FUNDS",
        "failure_reason": "INSUFFICIENT_FUNDS_OR_LIMIT",
        "payment_method": "CARD",
        "gateway_route_health": "UP",
        "customer_recovery_history_rate": 0.5,
        "customer_opted_out": True,
        "retry_count": 0,
        "time_since_failure_minutes": 0.0,
        "merchant_mcc_tier": "STANDARD_COMMERCE",
    }

    req_create = urllib.request.Request(
        base_url + "/api/v1/cases",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req_create) as resp:
        created = json.loads(resp.read().decode("utf-8"))
        case_id = created["case_id"]
        print(f"[PASS] Case ID: {case_id}")
        print(f"[PASS] Policy Decision: {created['policy_decision']}")
        print(f"[PASS] Selected Strategy: {created['selected_strategy']}")
        print(f"[PASS] Current State: {created['current_state']}")
        print(f"[PASS] Is Stopped: {created['is_stopped']}")
        print(f"[PASS] Is Recovered: {created['is_recovered']}")

    # 4. Fetch Case Detail (What JavaScript receives)
    print(f"\n[STEP 4] Fetching case detail for {case_id}...")
    req_detail = urllib.request.Request(base_url + f"/api/v1/cases/{case_id}")
    with urllib.request.urlopen(req_detail) as resp:
        detail = json.loads(resp.read().decode("utf-8"))
        latest_audit = detail["audit_trail"][-1]
        print(f"[PASS] Latest Action: {latest_audit['selected_action']}")
        print(f"[PASS] Latest Policy Decision: {latest_audit['policy_decision']}")
        print(f"[PASS] Latest Outcome: {latest_audit['outcome']}")
        print(f"[PASS] Summary Final State: {detail['summary']['final_state']}")
        print(f"[PASS] Summary is_recovered: {detail['summary']['is_recovered']}")
        print(f"[PASS] Summary is_stopped: {detail['summary']['is_stopped']}")

    # 5. Attempt Execution
    print(f"\n[STEP 5] Attempting POST /api/v1/cases/{case_id}/execute...")
    req_exec = urllib.request.Request(
        base_url + f"/api/v1/cases/{case_id}/execute",
        data=b"",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req_exec) as resp:
        exec_res = json.loads(resp.read().decode("utf-8"))
        print("[PASS] Execute Response Body:")
        print(json.dumps(exec_res, indent=2))

    # 6. Verify Invariants
    print("\n[STEP 6] Verifying strict safety invariants...")
    assert exec_res["executed"] is False, "Execution occurred when it should be False"
    assert exec_res["status"] == "STOPPED", "Status is not STOPPED"
    assert exec_res["final_state"] == "STOPPED", "Final state is not STOPPED"
    assert exec_res["post_action_captured"] == 0.0, "Captured amount is not 0.0"
    assert exec_res["authoritative_payment_status"] == "unpaid", "Payment status is not unpaid"
    assert exec_res["is_recovered"] is False, "is_recovered is True"
    assert exec_res["is_stopped"] is True, "is_stopped is False"
    assert exec_res["reference_id"] is None, "reference_id is not None"

    # 7. Fetch Case Detail After Execution
    print(f"\n[STEP 7] Fetching case detail post-execution for {case_id}...")
    req_post_detail = urllib.request.Request(base_url + f"/api/v1/cases/{case_id}")
    with urllib.request.urlopen(req_post_detail) as resp:
        post_detail = json.loads(resp.read().decode("utf-8"))
        print(f"[PASS] Post-execution state: {post_detail['summary']['final_state']}")
        print(f"[PASS] Post-execution recovered amount: INR {post_detail['summary']['recovered_amount']:.2f}")
        print(f"[PASS] Post-execution is_recovered: {post_detail['summary']['is_recovered']}")
        assert post_detail["summary"]["final_state"] == "STOPPED"
        assert post_detail["summary"]["recovered_amount"] == 0.0
        assert post_detail["summary"]["is_recovered"] is False

    print("\n============================================================")
    print("[PASS] ALL LIVE PRODUCTION CHECKS COMPLETED & PASSED!")
    print("============================================================")

if __name__ == "__main__":
    run_live_verification()
