"""Unit tests for Phase 12 Benchmark Harness and Baseline comparisons."""

import pytest
from evaluation.run_benchmark import run_benchmark_on_split


def test_benchmark_runs_and_race_outperforms_baselines():
    """Verify that benchmark runs completely and RACE outperforms Baseline A in revenue recovery."""
    results = run_benchmark_on_split("validation")
    
    race_res = results["race"]
    base_a = results["baseline_a"]
    base_b = results["baseline_b"]

    assert race_res["total_cases"] == 200
    assert race_res["actual_recovered_revenue"] > base_a["total_recovered_revenue"]
    assert race_res["incremental_revenue_vs_baseline_a"] > 0.0
    assert race_res["recovery_rate_pct"] > base_a["recovery_rate_pct"]
    assert race_res["duplicate_actions"] == 0
    assert race_res["policy_violations"] == 0
    assert race_res["audit_completeness_pct"] == 100.0
