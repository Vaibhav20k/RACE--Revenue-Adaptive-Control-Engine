"""Unit tests for Phase 3 Revenue-at-Risk ML and statistical estimation layer."""

import json
from pathlib import Path
import pytest
from backend.domain.events import RevenueEvent
from backend.domain.ground_truth import CaseGroundTruth
from backend.models.feature_extractor import RevenueFeatureExtractor
from backend.models.risk_estimator import RevenueRiskEstimator
from backend.recovery.detection.detector import RevenueRiskDetector
from backend.core.constants import FailureClass, EventType


def test_feature_extractor_shape_and_values():
    """Verify feature extractor converts RevenueEvent into expected 1D numeric vector."""
    event = RevenueEvent(
        event_id="evt_test_feat",
        timestamp="2026-08-20T10:00:00Z",
        event_type=EventType.FAILED_PAYMENT,
        merchant_id="mer_test",
        customer_id="cust_test",
        amount=4500.0,
        currency="INR",
        payment_method="UPI",
        failure_reason="UPI_TIMEOUT",
        failure_class=FailureClass.TEMPORARY_NETWORK,
        payment_state="FAILED",
        retry_count=1,
        time_since_failure_minutes=15.0,
        customer_recovery_history_rate=0.75,
        customer_opted_out=False,
    )
    features = RevenueFeatureExtractor.extract_features(event)
    assert features.ndim == 1
    assert features.shape[0] > 10
    assert not any(features != features)  # No NaNs


def test_model_training_and_validation_performance():
    """Train estimator on train split and verify performance on validation split."""
    train_events_path = Path("datasets/train/revenue_events_train.json")
    train_gt_path = Path("datasets/train/ground_truth_train.json")
    val_events_path = Path("datasets/validation/revenue_events_validation.json")
    val_gt_path = Path("datasets/validation/ground_truth_validation.json")

    estimator = RevenueRiskEstimator.train_from_dataset(train_events_path, train_gt_path)
    assert estimator.is_fitted

    with open(val_events_path, "r", encoding="utf-8") as f:
        val_events = [RevenueEvent.model_validate(e) for e in json.load(f)]
    with open(val_gt_path, "r", encoding="utf-8") as f:
        val_gts = [CaseGroundTruth.model_validate(g) for g in json.load(f)]

    detector = RevenueRiskDetector(estimator)
    correct_recoverability = 0
    total_val = len(val_events)

    for e, gt in zip(val_events, val_gts):
        assessment = detector.assess_event(e)
        true_is_recoverable = (gt.true_recoverable_amount > 0.0)
        predicted_is_rec = assessment.is_recoverable

        if true_is_recoverable == predicted_is_rec:
            correct_recoverability += 1

        # Check safety edge cases: fraud or opt-out must have 0 probability
        if e.customer_opted_out or e.failure_class == FailureClass.FRAUD_SUSPECTED:
            assert assessment.recovery_probability == 0.0
            assert assessment.priority == "UNRECOVERABLE"

    accuracy = correct_recoverability / total_val
    assert accuracy >= 0.85, f"Validation recoverability classification accuracy was {accuracy:.2f}"
