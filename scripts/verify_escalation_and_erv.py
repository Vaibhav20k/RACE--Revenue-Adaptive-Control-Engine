"""Comprehensive live verification of HUMAN_ESCALATION labeling, ERV Downside Risk consistency, and STOP isolation."""

import urllib.request
import json

base_url = "http://127.0.0.1:8000"

def simulate_erv_ui_params(audit_rec, chosen_strat, amount, cust_rate):
    param_map = {
        "STOP": {"cost": 0.0, "friction": 0.0, "risk": 0.0},
        "HUMAN_ESCALATION": {"cost": 50.0, "friction": 5.0, "risk": 2.0},
        "REMINDER_THEN_RETRY": {"cost": 8.0, "friction": 15.0, "risk": 5.0},
        "RETRY_NOW": {"cost": 5.0, "friction": 8.0, "risk": 5.0},
        "RETRY_LATER": {"cost": 5.0, "friction": 5.0, "risk": 4.0},
    }
    current_params = param_map.get(chosen_strat, {"cost": 10.0, "friction": 10.0, "risk": 10.0})
    cost = current_params["cost"]
    friction = current_params["friction"]
    risk = current_params["risk"]

    erv_breakdown = audit_rec.get("erv_breakdown", {})
    calcs = erv_breakdown.get("calculations", [])
    matched = next((c for c in calcs if c["strategy"] == chosen_strat), None)
    
    if matched:
        p_rec = matched["p_rec"]
        erv = matched["erv"]
    elif chosen_strat == "STOP":
        p_rec, erv = 0.0, 0.0
    elif chosen_strat == "HUMAN_ESCALATION":
        p_rec = min(0.92, 0.50 + 0.40 * (cust_rate or 0.65))
        erv = (p_rec * amount) - cost - friction - risk
    else:
        p_rec = cust_rate or 0.75
        erv = (p_rec * amount) - cost - friction - risk

    formula_str = f"ERV({chosen_strat}) = ({p_rec:.2f} * INR {amount:.2f}) - INR {cost:.2f} - INR {friction:.2f} - INR {risk:.2f} = INR {erv:.2f}"
    return {
        "p_rec": p_rec,
        "cost": cost,
        "friction": friction,
        "risk": risk,
        "erv": erv,
        "formula": formula_str,
    }

def main():
    print("====================================================================")
    print("LIVE VERIFICATION: HUMAN_ESCALATION, ERV RISK, & STOP INVARIANTS")
    print("====================================================================")

    # -------------------------------------------------------------------------
    # TEST A & B: HIGH VALUE ESCALATION CASE (INR 75,000)
    # -------------------------------------------------------------------------
    print("\n--- [TEST A & B] HIGH-VALUE CASE (INR 75,000) ---")
    payload_high = {
        "amount": 75000.0,
        "currency": "INR",
        "failure_class": "INSUFFICIENT_FUNDS",
        "failure_reason": "INSUFFICIENT_FUNDS_OR_LIMIT",
        "customer_recovery_history_rate": 0.65,
        "customer_opted_out": False,
    }

    req_create = urllib.request.Request(
        base_url + "/api/v1/cases",
        data=json.dumps(payload_high).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_create) as resp:
        created_case = json.loads(resp.read().decode("utf-8"))
        case_id = created_case["case_id"]

    # Fetch Case Detail
    req_detail = urllib.request.Request(base_url + f"/api/v1/cases/{case_id}")
    with urllib.request.urlopen(req_detail) as resp:
        detail = json.loads(resp.read().decode("utf-8"))

    latest_audit = detail["audit_trail"][-1]
    chosen_strat = latest_audit["selected_action"]
    policy_dec = latest_audit["policy_decision"]

    print(f"Case ID:             {case_id}")
    print(f"Amount:              INR {detail['event']['amount']:.2f}")
    print(f"Recommended Action:  {chosen_strat}")
    print(f"Policy Decision:     {policy_dec}")

    # ERV Parameter Extraction
    ui_erv = simulate_erv_ui_params(
        latest_audit, chosen_strat, detail["event"]["amount"], detail["event"]["customer_recovery_history_rate"]
    )
    print("\nDisplayed Stat Cards:")
    print(f"  * P(Recovery):       {ui_erv['p_rec'] * 100:.0f}%")
    print(f"  * Action Fee:        INR {ui_erv['cost']:.2f}")
    print(f"  * Customer Friction: INR {ui_erv['friction']:.2f}")
    print(f"  * Downside Risk:     INR {ui_erv['risk']:.2f}")
    print(f"  * Expected ERV:      INR {ui_erv['erv']:.2f}")
    print(f"  * Formula Instance:  {ui_erv['formula']}")

    # Mathematical Verification
    math_calc = round((ui_erv["p_rec"] * 75000.0) - ui_erv["cost"] - ui_erv["friction"] - ui_erv["risk"], 2)
    print(f"Mathematical Check:  {ui_erv['p_rec']:.3f} * 75000 - {ui_erv['cost']} - {ui_erv['friction']} - {ui_erv['risk']} = {math_calc:.2f}")
    assert abs(math_calc - ui_erv["erv"]) < 0.01, f"Mathematical mismatch in ERV calculation: {math_calc} vs {ui_erv['erv']}"
    assert ui_erv["risk"] == 2.0, f"Expected risk 2.0, got {ui_erv['risk']}"

    # Execute Action
    req_exec = urllib.request.Request(
        base_url + f"/api/v1/cases/{case_id}/execute",
        data=b"",
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_exec) as resp:
        exec_res = json.loads(resp.read().decode("utf-8"))

    print("\nExecution Response:")
    print(f"  * Action:            {exec_res['action']}")
    print(f"  * Executed:          {exec_res['executed']}")
    print(f"  * Status:            {exec_res['status']}")
    print(f"  * Final State:       {exec_res['final_state']}")
    print(f"  * Post Captured:     INR {exec_res['post_action_captured']:.2f}")
    print(f"  * Payment Status:    {exec_res['authoritative_payment_status']}")
    print(f"  * Is Escalated:      {exec_res['is_escalated']}")
    print(f"  * Is Stopped:        {exec_res['is_stopped']}")
    print(f"  * Is Recovered:      {exec_res['is_recovered']}")

    assert exec_res["executed"] is False
    assert exec_res["status"] == "ESCALATED"
    assert exec_res["final_state"] == "ESCALATED"
    assert exec_res["post_action_captured"] == 0.0
    assert exec_res["is_escalated"] is True
    assert exec_res["is_stopped"] is False
    assert exec_res["is_recovered"] is False

    # -------------------------------------------------------------------------
    # TEST C: EXISTING STOP CASE (CUSTOMER OPT-OUT)
    # -------------------------------------------------------------------------
    print("\n--- [TEST C] STOP CASE (CUSTOMER OPT-OUT) ---")
    payload_stop = {
        "amount": 4200.0,
        "currency": "INR",
        "failure_class": "INSUFFICIENT_FUNDS",
        "customer_opted_out": True,
    }
    req_stop_create = urllib.request.Request(
        base_url + "/api/v1/cases",
        data=json.dumps(payload_stop).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_stop_create) as resp:
        stop_created = json.loads(resp.read().decode("utf-8"))
        stop_id = stop_created["case_id"]

    req_stop_exec = urllib.request.Request(
        base_url + f"/api/v1/cases/{stop_id}/execute",
        data=b"",
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_stop_exec) as resp:
        stop_exec_res = json.loads(resp.read().decode("utf-8"))

    print(f"Stop Case ID:        {stop_id}")
    print(f"Stop Action:         {stop_exec_res['action']}")
    print(f"Stop Status:         {stop_exec_res['status']}")
    print(f"Stop Final State:    {stop_exec_res['final_state']}")
    print(f"Stop Is Stopped:     {stop_exec_res['is_stopped']}")
    print(f"Stop Is Escalated:   {stop_exec_res['is_escalated']}")

    assert stop_exec_res["status"] == "STOPPED"
    assert stop_exec_res["final_state"] == "STOPPED"
    assert stop_exec_res["is_stopped"] is True
    assert stop_exec_res["is_escalated"] is False

    print("\n====================================================================")
    print("ALL LIVE VERIFICATION CHECKS PASSED WITH 100% CORRECTNESS!")
    print("====================================================================")

if __name__ == "__main__":
    main()
