import json

with open("evaluation/reports/final_benchmark_report.json", "r") as f:
    b = json.load(f)

tot_risk = b["race"]["total_revenue_at_risk"]

print("==========================================================================================")
print("CANONICAL BENCHMARK METRICS (200 Held-Out Synthetic Validation Cases)")
print("==========================================================================================")
print(f"Total Revenue at Risk: INR {tot_risk:,.2f} (~INR 18.07L)\n")

print(f"{'System / Baseline':<32} | {'Tx Count Rate':<14} | {'Revenue-Weighted':<17} | {'Recovered Revenue':<18} | {'Cost / Rupee'}")
print("-" * 105)

for key, name in [
    ("baseline_a", "Baseline A (Fixed Retry)"),
    ("baseline_b", "Baseline B (Rule-Based)"),
    ("baseline_c", "Baseline C (ML Ranking)"),
    ("race", "RACE (Full Engine)"),
]:
    data = b[key]
    tx_rate = data["recovery_rate_pct"]
    rec_rev = data.get("actual_recovered_revenue", data.get("total_recovered_revenue"))
    rev_rate = (rec_rev / tot_risk) * 100
    cost_rupee = data.get("cost_per_recovered_rupee", 0.0)
    print(f"{name:<32} | {tx_rate:>13.2f}% | {rev_rate:>16.2f}% | INR {rec_rev:>14,.2f} | INR {cost_rupee:.4f}")

print("-" * 105)
inc_rev = b["race"]["incremental_revenue_vs_baseline_a"]
print(f"Incremental Revenue Lift (RACE vs Baseline A): +INR {inc_rev:,.2f} (+236.78% over Baseline A)")
print("==========================================================================================\n")
