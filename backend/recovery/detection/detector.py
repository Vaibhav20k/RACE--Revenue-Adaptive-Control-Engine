"""Revenue-at-Risk Detector for identifying, diagnosing, and triaging recovery events."""

from dataclasses import dataclass
from typing import Optional
from backend.domain.events import RevenueEvent
from backend.models.risk_estimator import RevenueRiskEstimator


@dataclass(frozen=True)
class RiskAssessment:
    """Structured assessment produced by the detector."""
    event_id: str
    amount_at_risk: float
    recovery_probability: float
    estimated_recoverable_amount: float
    is_recoverable: bool
    priority: str  # "HIGH", "MEDIUM", "LOW", "UNRECOVERABLE"


class RevenueRiskDetector:
    """Evaluates incoming revenue events and determines recoverability potential."""

    def __init__(self, estimator: Optional[RevenueRiskEstimator] = None):
        self.estimator = estimator or RevenueRiskEstimator()

    def assess_event(self, event: RevenueEvent) -> RiskAssessment:
        """Assesses risk and recoverability for a single revenue event."""
        p_rec, recoverable_amt = self.estimator.predict_single(event)
        is_rec = p_rec >= 0.15 and recoverable_amt > 10.0

        if not is_rec or p_rec == 0.0:
            priority = "UNRECOVERABLE"
        elif event.amount >= 25000.0 or (p_rec >= 0.75 and recoverable_amt >= 5000.0):
            priority = "HIGH"
        elif p_rec >= 0.40 and recoverable_amt >= 500.0:
            priority = "MEDIUM"
        else:
            priority = "LOW"

        return RiskAssessment(
            event_id=event.event_id,
            amount_at_risk=round(event.amount, 2),
            recovery_probability=p_rec,
            estimated_recoverable_amount=recoverable_amt,
            is_recoverable=is_rec,
            priority=priority,
        )
