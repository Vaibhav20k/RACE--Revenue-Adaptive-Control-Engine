"""Empirical strategy performance store tracking observed recovery success rates."""

from dataclasses import dataclass
from typing import Dict, Tuple, Optional, Any
from pydantic import BaseModel, Field
from backend.core.constants import RecoveryStrategy


class StrategyPerformanceBucket(BaseModel):
    """Aggregate statistics for a specific failure class and strategy combination."""
    failure_class: str
    strategy: str
    sample_count: int = 0
    success_count: int = 0
    total_recovered_amount: float = 0.0
    total_expected_value: float = 0.0

    @property
    def empirical_success_rate(self) -> float:
        if self.sample_count <= 0:
            return 0.0
        return round(self.success_count / self.sample_count, 4)

    @property
    def average_recovered_amount(self) -> float:
        if self.success_count <= 0:
            return 0.0
        return round(self.total_recovered_amount / self.success_count, 2)


class StrategyStatisticsStore:
    """In-memory and persistent storage for empirical recovery outcomes."""

    def __init__(self, repository: Optional[Any] = None):
        # Key: (failure_class, strategy_name) -> StrategyPerformanceBucket
        self._store: Dict[Tuple[str, str], StrategyPerformanceBucket] = {}
        self.repository = repository
        self._rehydrate_from_db()

    def _rehydrate_from_db(self) -> None:
        """Loads persistent buckets from SQLite database if repository is configured."""
        if self.repository is not None and hasattr(self.repository, "load_all_learning_buckets"):
            try:
                records = self.repository.load_all_learning_buckets()
                for r in records:
                    key = (r["failure_class"].upper(), r["strategy"].upper())
                    self._store[key] = StrategyPerformanceBucket(
                        failure_class=r["failure_class"].upper(),
                        strategy=r["strategy"].upper(),
                        sample_count=r["sample_count"],
                        success_count=r["success_count"],
                        total_recovered_amount=r["total_recovered_amount"],
                        total_expected_value=r["total_expected_value"],
                    )
            except Exception:
                pass

    def record_outcome(
        self,
        failure_class: str,
        strategy: str,
        expected_value: float,
        actual_recovered_amount: float,
        is_success: bool,
    ) -> Optional[StrategyPerformanceBucket]:
        """Records an observed intervention outcome and updates aggregate statistics."""
        # Defense in depth: STOP is not an intervention and must never be tracked in learning statistics
        if strategy.upper() == "STOP":
            return None

        key = (failure_class.upper(), strategy.upper())
        if key not in self._store:
            self._store[key] = StrategyPerformanceBucket(
                failure_class=failure_class.upper(),
                strategy=strategy.upper(),
            )

        bucket = self._store[key]
        bucket.sample_count += 1
        if is_success:
            bucket.success_count += 1
            bucket.total_recovered_amount += actual_recovered_amount
        bucket.total_expected_value += expected_value

        # Persist to database if repository is configured
        if self.repository is not None and hasattr(self.repository, "save_learning_bucket"):
            try:
                self.repository.save_learning_bucket(
                    failure_class=bucket.failure_class,
                    strategy=bucket.strategy,
                    sample_count=bucket.sample_count,
                    success_count=bucket.success_count,
                    total_recovered=bucket.total_recovered_amount,
                    total_expected=bucket.total_expected_value,
                )
            except Exception:
                pass

        return bucket

    def get_empirical_rate(self, failure_class: str, strategy: str, default: float = 0.5) -> float:
        """Retrieves observed success rate or returns default if insufficient samples."""
        key = (failure_class.upper(), strategy.upper())
        bucket = self._store.get(key)
        if not bucket or bucket.sample_count < 3:
            return default
        # Bayesian smoothing with prior
        prior_weight = 3.0
        smoothed_rate = (bucket.success_count + (default * prior_weight)) / (bucket.sample_count + prior_weight)
        return round(smoothed_rate, 4)

    def get_all_buckets(self) -> Dict[str, Dict[str, Any]]:
        """Returns JSON-serializable snapshot of all strategy statistics."""
        return {
            f"{k[0]}:{k[1]}": {
                "failure_class": v.failure_class,
                "strategy": v.strategy,
                "sample_count": v.sample_count,
                "success_count": v.success_count,
                "empirical_success_rate": v.empirical_success_rate,
                "total_recovered_amount": v.total_recovered_amount,
                "average_recovered_amount": v.average_recovered_amount,
            }
            for k, v in self._store.items()
        }
