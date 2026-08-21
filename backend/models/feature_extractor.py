"""Feature extraction and numerical encoding for revenue event prediction."""

import numpy as np
from typing import List, Dict, Any
from backend.domain.events import RevenueEvent

PAYMENT_METHODS = ["UPI", "CARD", "NETBANKING", "WALLET", "OTHER"]
FAILURE_CLASSES = [
    "TEMPORARY_NETWORK",
    "INSUFFICIENT_FUNDS",
    "AUTH_REQUIRED",
    "GATEWAY_DEGRADATION",
    "EXPIRED_CARD",
    "FRAUD_SUSPECTED",
    "CUSTOMER_ABANDONMENT",
    "UNKNOWN",
]
GATEWAY_HEALTH = ["UP", "DEGRADED", "DOWN"]
MERCHANT_TIERS = ["low", "medium", "high"]


class RevenueFeatureExtractor:
    """Transforms raw RevenueEvents into normalized numerical feature vectors."""

    @classmethod
    def extract_features(cls, event: RevenueEvent) -> np.ndarray:
        """Extracts a 1D numpy array of features for a single event."""
        features = []

        # 1. Amount features (log transformed and standard scale)
        log_amount = np.log1p(max(0.0, event.amount))
        features.append(log_amount)
        features.append(1.0 if event.amount > 50000.0 else 0.0)
        features.append(1.0 if event.amount < 50.0 else 0.0)

        # 2. Retry history & temporal features
        features.append(float(event.retry_count))
        features.append(min(120.0, float(event.time_since_failure_minutes)) / 120.0)

        # 3. Customer historical recovery rate
        features.append(float(event.customer_recovery_history_rate))
        features.append(1.0 if event.customer_opted_out else 0.0)

        # 4. Payment method one-hot encoding
        for pm in PAYMENT_METHODS:
            features.append(1.0 if event.payment_method.upper() == pm else 0.0)

        # 5. Failure class one-hot encoding
        fc_val = event.failure_class.value if hasattr(event.failure_class, "value") else str(event.failure_class)
        for fc in FAILURE_CLASSES:
            features.append(1.0 if fc_val == fc else 0.0)

        # 6. Gateway route health one-hot encoding
        for gh in GATEWAY_HEALTH:
            features.append(1.0 if event.gateway_route_health.upper() == gh else 0.0)

        # 7. Merchant tier one-hot encoding
        for mt in MERCHANT_TIERS:
            features.append(1.0 if event.merchant_mcc_tier.lower() == mt else 0.0)

        return np.array(features, dtype=np.float32)

    @classmethod
    def extract_batch(cls, events: List[RevenueEvent]) -> np.ndarray:
        """Extracts a 2D numpy array for a batch of events."""
        return np.vstack([cls.extract_features(e) for e in events])
