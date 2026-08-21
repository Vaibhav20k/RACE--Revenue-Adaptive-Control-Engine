"""Unit tests for Phase 1 synthetic dataset generation and schema validation."""

import json
from pathlib import Path
from backend.domain.events import RevenueEvent
from backend.domain.ground_truth import CaseGroundTruth
from backend.core.constants import FailureClass, RecoveryStrategy, EventType


def test_dataset_files_exist():
    """Verify all expected split files exist on disk."""
    base = Path("datasets")
    for split in ["train", "validation", "test"]:
        events_file = base / split / f"revenue_events_{split}.json"
        gt_file = base / split / f"ground_truth_{split}.json"
        assert events_file.exists(), f"Missing {events_file}"
        assert gt_file.exists(), f"Missing {gt_file}"


def test_dataset_schema_and_counts():
    """Verify schema integrity and exact split counts (600 train, 200 val, 200 test)."""
    base = Path("datasets")
    splits = {"train": 600, "validation": 200, "test": 200}
    all_event_ids = set()
    all_case_ids = set()

    for split, expected_count in splits.items():
        events_path = base / split / f"revenue_events_{split}.json"
        gt_path = base / split / f"ground_truth_{split}.json"

        with open(events_path, "r", encoding="utf-8") as f:
            events_data = json.load(f)
        with open(gt_path, "r", encoding="utf-8") as f:
            gt_data = json.load(f)

        assert len(events_data) == expected_count
        assert len(gt_data) == expected_count

        for e_dict, g_dict in zip(events_data, gt_data):
            event = RevenueEvent.model_validate(e_dict)
            gt = CaseGroundTruth.model_validate(g_dict)

            assert event.event_id == gt.event_id
            assert event.amount > 0.0
            assert gt.true_revenue_at_risk > 0.0
            assert gt.true_optimal_strategy in gt.allowed_actions

            # Check uniqueness across entire dataset
            assert event.event_id not in all_event_ids
            assert gt.case_id not in all_case_ids
            all_event_ids.add(event.event_id)
            all_case_ids.add(gt.case_id)

    assert len(all_event_ids) == 1000
    assert len(all_case_ids) == 1000


def test_dataset_archetype_coverage():
    """Verify that dataset covers required failure classes and edge scenarios."""
    base = Path("datasets")
    classes_found = set()
    has_escalation = False
    has_opt_out = False
    has_low_value = False
    has_checkout_abandonment = False
    has_recurring = False

    for split in ["train", "validation"]:
        events_path = base / split / f"revenue_events_{split}.json"
        gt_path = base / split / f"ground_truth_{split}.json"

        with open(events_path, "r", encoding="utf-8") as f:
            events_data = json.load(f)
        with open(gt_path, "r", encoding="utf-8") as f:
            gt_data = json.load(f)

        for e, g in zip(events_data, gt_data):
            classes_found.add(e["failure_class"])
            if g.get("requires_escalation"):
                has_escalation = True
            if e.get("customer_opted_out"):
                has_opt_out = True
            if e["amount"] < 50.0:
                has_low_value = True
            if e["event_type"] == EventType.CHECKOUT_ABANDONMENT.value:
                has_checkout_abandonment = True
            if e["event_type"] == EventType.RECURRING_PAYMENT_FAILURE.value:
                has_recurring = True

    assert FailureClass.TEMPORARY_NETWORK.value in classes_found
    assert FailureClass.INSUFFICIENT_FUNDS.value in classes_found
    assert FailureClass.FRAUD_SUSPECTED.value in classes_found
    assert has_escalation
    assert has_opt_out
    assert has_low_value
    assert has_checkout_abandonment
    assert has_recurring
