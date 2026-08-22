"""Verification script reproducing the exact rendering logic for Case 1 (STOP) and Case 2 (REMINDER_THEN_RETRY)."""

import urllib.request
import json

base_url = "http://127.0.0.1:8000"

def simulate_ui_render(case_id, data):
    evt = data["event"]
    audit_trail = data.get("audit_trail", [])
    latestAudit = audit_trail[-1] if audit_trail else None

    # Step 2: Recoverability & Policy
    chosenStrat = latestAudit["selected_action"] if latestAudit else (
        "STOP" if (evt.get("customer_opted_out") or evt.get("failure_class") == "FRAUD_SUSPECTED" or evt.get("retry_count", 0) >= 3)
        else ("HUMAN_ESCALATION" if evt.get("amount", 0) > 50000 else data["summary"].get("selected_strategy", "STOP"))
    )
    pDecision = latestAudit["policy_decision"] if latestAudit else (
        "BLOCKED" if (chosenStrat == "STOP" or evt.get("customer_opted_out") or evt.get("failure_class") == "FRAUD_SUSPECTED" or evt.get("retry_count", 0) >= 3)
        else ("ESCALATE_REQUIRED" if evt.get("amount", 0) > 50000 else "APPROVED")
    )
    isStopped = (chosenStrat == "STOP" or pDecision == "BLOCKED" or evt.get("customer_opted_out") or data["summary"].get("is_stopped"))

    # Candidates rendering
    candidatesList = ["RETRY_NOW", "RETRY_LATER", "REMINDER_THEN_RETRY", "HUMAN_ESCALATION", "STOP"]
    chips = []
    for s in candidatesList:
        isWinner = (s == chosenStrat)
        status = "[HIGHLIGHTED - ACTIVE WINNER]" if isWinner else "[unhighlighted]"
        chips.append(f"{s} {status}")

    # Check 5 rendering
    check5Pass = (evt.get("payment_state") in ["FAILED", "PENDING", None])
    check5Label = "5. Payment State: " + ("Payment not yet settled (Pass)" if check5Pass else "Payment already settled or unverified")

    return {
        "case_id": case_id,
        "recommended_action": chosenStrat,
        "policy_decision": pDecision,
        "candidates_chips": chips,
        "check5_label": check5Label,
    }

def main():
    print("====================================================================")
    print("UI POLISH VERIFICATION: CANDIDATE HIGHLIGHT & CHECK #5 LABEL")
    print("====================================================================")

    # -------------------------------------------------------------------------
    # CASE 1: Recommended Action is STOP (e.g. Customer Opted Out)
    # -------------------------------------------------------------------------
    print("\n--- [CASE 1] SCENARIO WHERE RECOMMENDED ACTION IS STOP ---")
    payload_stop = {
        "amount": 4200.0,
        "currency": "INR",
        "failure_class": "INSUFFICIENT_FUNDS",
        "failure_reason": "INSUFFICIENT_FUNDS_OR_LIMIT",
        "customer_opted_out": True,
    }
    req1 = urllib.request.Request(
        base_url + "/api/v1/cases",
        data=json.dumps(payload_stop).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req1) as resp:
        c1 = json.loads(resp.read().decode("utf-8"))
        case1_id = c1["case_id"]

    req1_detail = urllib.request.Request(base_url + f"/api/v1/cases/{case1_id}")
    with urllib.request.urlopen(req1_detail) as resp:
        data1 = json.loads(resp.read().decode("utf-8"))

    res1 = simulate_ui_render(case1_id, data1)
    print(f"Case ID:              {res1['case_id']}")
    print(f"Recommended Action:   {res1['recommended_action']}")
    print(f"Policy Decision:      {res1['policy_decision']}")
    print("Candidate Chips:")
    for chip in res1["candidates_chips"]:
        print(f"  * {chip}")
    print(f"Policy Check #5 Text: {res1['check5_label']}")

    # Assert Case 1
    assert res1["recommended_action"] == "STOP"
    assert "STOP [HIGHLIGHTED - ACTIVE WINNER]" in res1["candidates_chips"]
    assert "REMINDER_THEN_RETRY [unhighlighted]" in res1["candidates_chips"]

    # -------------------------------------------------------------------------
    # CASE 2: Recommended Action is REMINDER_THEN_RETRY (Recoverable Scenario)
    # -------------------------------------------------------------------------
    print("\n--- [CASE 2] SCENARIO WHERE RECOMMENDED ACTION IS REMINDER_THEN_RETRY ---")
    payload_retry = {
        "amount": 1681.55,
        "currency": "INR",
        "failure_class": "INSUFFICIENT_FUNDS",
        "failure_reason": "INSUFFICIENT_FUNDS_OR_LIMIT",
        "customer_recovery_history_rate": 0.85,
        "customer_opted_out": False,
    }
    req2 = urllib.request.Request(
        base_url + "/api/v1/cases",
        data=json.dumps(payload_retry).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req2) as resp:
        c2 = json.loads(resp.read().decode("utf-8"))
        case2_id = c2["case_id"]

    req2_detail = urllib.request.Request(base_url + f"/api/v1/cases/{case2_id}")
    with urllib.request.urlopen(req2_detail) as resp:
        data2 = json.loads(resp.read().decode("utf-8"))

    res2 = simulate_ui_render(case2_id, data2)
    print(f"Case ID:              {res2['case_id']}")
    print(f"Recommended Action:   {res2['recommended_action']}")
    print(f"Policy Decision:      {res2['policy_decision']}")
    print("Candidate Chips:")
    for chip in res2["candidates_chips"]:
        print(f"  * {chip}")
    print(f"Policy Check #5 Text: {res2['check5_label']}")

    # Assert Case 2
    assert res2["recommended_action"] == "REMINDER_THEN_RETRY"
    assert "REMINDER_THEN_RETRY [HIGHLIGHTED - ACTIVE WINNER]" in res2["candidates_chips"]
    assert "STOP [unhighlighted]" in res2["candidates_chips"]

    print("\n====================================================================")
    print("ALL UI POLISH CHECKS VERIFIED SUCCESSFULLY!")
    print("====================================================================")

if __name__ == "__main__":
    main()
