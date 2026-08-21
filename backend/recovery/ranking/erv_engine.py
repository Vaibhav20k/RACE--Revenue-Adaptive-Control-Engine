"""Expected Recovery Value (ERV) Engine for numerical strategy evaluation and selection."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from backend.core.constants import RecoveryStrategy
from backend.core.economics import ERVCalculation
from backend.domain.events import RevenueEvent
from backend.recovery.ranking.strategy_scorer import StrategyScorer
from backend.recovery.ranking.candidate_generator import CandidateStrategyGenerator


@dataclass(frozen=True)
class ERVDecision:
    """Structured decision output from the ERV engine."""
    best_strategy: RecoveryStrategy
    highest_erv: float
    candidate_calculations: List[ERVCalculation]
    decision_rationale: str


class ERVEngine:
    """Evaluates candidate recovery actions using Expected Recovery Value optimization."""

    @classmethod
    def evaluate_candidates(
        cls,
        event: RevenueEvent,
        candidates: Optional[List[RecoveryStrategy]] = None,
    ) -> ERVDecision:
        """Calculates ERV for all candidate strategies and selects the highest-value option."""
        if candidates is None:
            candidates = CandidateStrategyGenerator.generate_candidates(event)

        calculations: List[ERVCalculation] = []
        recoverable_base = event.amount

        for strat in candidates:
            if strat == RecoveryStrategy.STOP:
                calc = ERVCalculation.calculate(
                    strategy=strat.value,
                    recovery_probability=0.0,
                    recoverable_amount=0.0,
                    action_cost=0.0,
                    friction_penalty=0.0,
                    risk_penalty=0.0,
                )
                calculations.append(calc)
                continue

            p_rec = StrategyScorer.estimate_strategy_probability(event, strat)
            params = StrategyScorer.get_action_parameters(strat, recoverable_base)

            calc = ERVCalculation.calculate(
                strategy=strat.value,
                recovery_probability=p_rec,
                recoverable_amount=recoverable_base,
                action_cost=params["action_cost"],
                friction_penalty=params["friction_penalty"],
                risk_penalty=params["risk_penalty"],
            )
            calculations.append(calc)

        # Sort candidates descending by ERV
        calculations.sort(key=lambda c: c.expected_recovery_value, reverse=True)
        top_calc = calculations[0]

        # If top ERV is non-positive, fallback to STOP
        if top_calc.expected_recovery_value <= 0.0 and top_calc.strategy != RecoveryStrategy.STOP.value:
            best_strat = RecoveryStrategy.STOP
            highest_erv = 0.0
            rationale = (
                f"All candidate interventions yielded non-positive net expected value "
                f"(best was {top_calc.strategy} with ERV INR {top_calc.expected_recovery_value:.2f}). STOP chosen."
            )
        else:
            best_strat = RecoveryStrategy(top_calc.strategy)
            highest_erv = top_calc.expected_recovery_value
            rationale = (
                f"Strategy {top_calc.strategy} selected with highest ERV of INR {highest_erv:.2f} "
                f"(P(rec)={top_calc.recovery_probability:.2f}, Cost=INR {top_calc.action_cost:.2f}, "
                f"Friction=INR {top_calc.friction_penalty:.2f}, Risk=INR {top_calc.risk_penalty:.2f})."
            )

        return ERVDecision(
            best_strategy=best_strat,
            highest_erv=highest_erv,
            candidate_calculations=calculations,
            decision_rationale=rationale,
        )
