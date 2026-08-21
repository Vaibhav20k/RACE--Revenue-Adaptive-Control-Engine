"""Unit tests for Phase 13 Ablation and Fixed-Budget Experiments."""

import pytest
from evaluation.experiments.ablations import AblationExperimentRunner
from evaluation.experiments.budget_controlled import FixedBudgetExperiment
from backend.domain.events import RevenueEvent
from backend.domain.ground_truth import CaseGroundTruth
import json
from pathlib import Path


def test_ablations_run_and_prove_erv_contribution():
    """Verify that all ablations execute and removing ERV reduces recovered revenue."""
    reports = AblationExperimentRunner.run_all_ablations("validation")
    
    assert "Full System (RACE)" in reports
    assert "Ablation: No ERV Optimization" in reports
    assert "Ablation: No Dynamic Routing" in reports

    full_rec = reports["Full System (RACE)"]["actual_recovered_revenue"]
    no_erv_rec = reports["Ablation: No ERV Optimization"]["actual_recovered_revenue"]

    # Full system must beat the ablated fixed strategy system
    assert full_rec > no_erv_rec


def test_fixed_budget_compliance():
    """Verify budget limits are strictly satisfied."""
    val_events_path = Path("datasets/validation/revenue_events_validation.json")
    val_gt_path = Path("datasets/validation/ground_truth_validation.json")

    with open(val_events_path, "r", encoding="utf-8") as f:
        events = [RevenueEvent.model_validate(e) for e in json.load(f)]
    with open(val_gt_path, "r", encoding="utf-8") as f:
        gts = [CaseGroundTruth.model_validate(g) for g in json.load(f)]

    res = FixedBudgetExperiment.run_budget_check(events, gts)
    assert res["budget_compliance"] is True
    assert res["race_recovered_revenue"] > res["baseline_a_recovered_revenue"]
