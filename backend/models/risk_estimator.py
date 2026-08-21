"""Trained statistical and machine learning models for recoverability probability and amounts."""

import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from backend.domain.events import RevenueEvent
from backend.domain.ground_truth import CaseGroundTruth
from backend.models.feature_extractor import RevenueFeatureExtractor


class RevenueRiskEstimator:
    """Trained model predicting P(recovery) and expected recoverable revenue."""

    def __init__(self):
        self.clf_pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(C=1.0, max_iter=500, random_state=42)),
        ])
        self.reg_pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("reg", Ridge(alpha=1.0, random_state=42)),
        ])
        self.is_fitted = False

    def fit(self, events: List[RevenueEvent], ground_truths: List[CaseGroundTruth]) -> "RevenueRiskEstimator":
        """Fits classification and regression models on training data."""
        X = RevenueFeatureExtractor.extract_batch(events)
        
        # Target for classification: binary recoverability (true_recoverable_amount > 0)
        y_clf = np.array([1 if gt.true_recoverable_amount > 0 else 0 for gt in ground_truths], dtype=np.int32)
        
        # Target for regression: recoverable amount ratio (true_recoverable / amount)
        y_ratio = np.array([
            (gt.true_recoverable_amount / e.amount) if e.amount > 0 else 0.0
            for e, gt in zip(events, ground_truths)
        ], dtype=np.float32)

        self.clf_pipeline.fit(X, y_clf)
        self.reg_pipeline.fit(X, y_ratio)
        self.is_fitted = True
        return self

    def predict_single(self, event: RevenueEvent) -> Tuple[float, float]:
        """Predicts (recovery_probability, estimated_recoverable_amount) for a single event."""
        if not self.is_fitted:
            # Fallback heuristic if not fitted
            return self._heuristic_fallback(event)

        X = RevenueFeatureExtractor.extract_features(event).reshape(1, -1)
        p_rec = float(self.clf_pipeline.predict_proba(X)[0][1])
        
        if event.customer_opted_out or event.failure_class in ["FRAUD_SUSPECTED", "EXPIRED_CARD"]:
            p_rec = 0.0

        ratio = float(np.clip(self.reg_pipeline.predict(X)[0], 0.0, 1.0))
        recoverable_amount = round(event.amount * ratio * p_rec, 2)
        return round(p_rec, 4), recoverable_amount

    def _heuristic_fallback(self, event: RevenueEvent) -> Tuple[float, float]:
        if event.customer_opted_out or event.failure_class in ["FRAUD_SUSPECTED", "EXPIRED_CARD"]:
            return 0.0, 0.0
        p = 0.6 if event.failure_class == "TEMPORARY_NETWORK" else 0.4
        return p, round(event.amount * p, 2)

    @classmethod
    def train_from_dataset(cls, train_events_path: Path, train_gt_path: Path) -> "RevenueRiskEstimator":
        """Factory method to load train split and return fitted estimator."""
        with open(train_events_path, "r", encoding="utf-8") as f:
            events = [RevenueEvent.model_validate(e) for e in json.load(f)]
        with open(train_gt_path, "r", encoding="utf-8") as f:
            gts = [CaseGroundTruth.model_validate(g) for g in json.load(f)]

        model = cls()
        model.fit(events, gts)
        return model
