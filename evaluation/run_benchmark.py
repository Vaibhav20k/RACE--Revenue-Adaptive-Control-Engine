"""Command line runner executing evaluation across all baselines and RACE."""

import json
from pathlib import Path
from backend.domain.events import RevenueEvent
from backend.domain.ground_truth import CaseGroundTruth
from evaluation.baselines.baseline_a_fixed_retry import BaselineAFixedRetry
from evaluation.baselines.baseline_b_rule_based import BaselineBRuleBased
from evaluation.baselines.baseline_c_ml_ranking import BaselineCMLRanking
from evaluation.engine import RACEEvaluationEngine


def run_benchmark_on_split(split_name: str = "validation"):
    """Runs all baselines and RACE on the requested dataset split."""
    base_dir = Path("datasets") / split_name
    events_path = base_dir / f"revenue_events_{split_name}.json"
    gt_path = base_dir / f"ground_truth_{split_name}.json"

    with open(events_path, "r", encoding="utf-8") as f:
        events = [RevenueEvent.model_validate(e) for e in json.load(f)]
    with open(gt_path, "r", encoding="utf-8") as f:
        ground_truths = [CaseGroundTruth.model_validate(g) for g in json.load(f)]

    # 1. Run Baseline A
    res_a = BaselineAFixedRetry.evaluate_dataset(events, ground_truths)

    # 2. Run Baseline B
    res_b = BaselineBRuleBased.evaluate_dataset(events, ground_truths)

    # 3. Run Baseline C
    res_c = BaselineCMLRanking.evaluate_dataset(events, ground_truths)

    # 4. Run Proposed RACE Engine
    race_engine = RACEEvaluationEngine()
    report_race = race_engine.evaluate_batch(events, ground_truths, baseline_a_recovered=res_a["total_recovered_revenue"])

    print("\n===========================================================")
    print(f"RACE REVENUE RECOVERY BENCHMARK [{split_name.upper()} SET]")
    print("===========================================================")
    print(f"Cases evaluated:                    {len(events)}")
    print(f"Total Revenue at Risk:              INR {report_race.total_revenue_at_risk:,.2f}")
    print(f"Estimated Recoverable Revenue:      INR {report_race.estimated_recoverable_revenue:,.2f}")
    print(f"Recovered Revenue (Baseline A):     INR {res_a['total_recovered_revenue']:,.2f}")
    print(f"Recovered Revenue (Baseline B):     INR {res_b['total_recovered_revenue']:,.2f}")
    print(f"Recovered Revenue (Baseline C):     INR {res_c['total_recovered_revenue']:,.2f}")
    print(f"Recovered Revenue (RACE Engine):    INR {report_race.actual_recovered_revenue:,.2f}")
    print(f"Incremental Recovery vs Baseline A: INR {report_race.incremental_revenue_vs_baseline_a:+,.2f}")
    print("-----------------------------------------------------------")
    print(f"Recovery Rate (RACE):               {report_race.recovery_rate_pct:.2f}% (vs Base A {res_a['recovery_rate_pct']:.2f}%)")
    print(f"Successful Interventions:           {report_race.successful_interventions}")
    print(f"Unnecessary Interventions:          {report_race.unnecessary_interventions}")
    print(f"Escalated Cases:                    {report_race.escalated_cases}")
    print(f"Stopped by Policy:                  {report_race.stopped_cases}")
    print(f"Execution Failures:                 {report_race.execution_failures}")
    print("-----------------------------------------------------------")
    print(f"Duplicate Actions:                  {report_race.duplicate_actions}")
    print(f"Policy Violations:                  {report_race.policy_violations}")
    print(f"Audit Completeness:                 {report_race.audit_completeness_pct:.1f}%")
    print(f"Cost per Recovered Rupee:           INR {report_race.cost_per_recovered_rupee:.4f}")
    print(f"Net Recovery Value:                 INR {report_race.net_recovery_value:,.2f}")
    print("===========================================================\n")

    return {
        "baseline_a": res_a,
        "baseline_b": res_b,
        "baseline_c": res_c,
        "race": report_race.to_dict(),
    }


if __name__ == "__main__":
    run_benchmark_on_split("validation")
