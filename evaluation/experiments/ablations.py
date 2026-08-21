"""Ablation experiments isolating the impact of each subsystem in RACE."""

import json
from pathlib import Path
from typing import Dict, Any, List
from backend.domain.events import RevenueEvent
from backend.domain.ground_truth import CaseGroundTruth
from evaluation.engine import RACEEvaluationEngine
from evaluation.baselines.baseline_a_fixed_retry import BaselineAFixedRetry


class AblationExperimentRunner:
    """Executes controlled ablations on the validation set."""

    @classmethod
    def run_all_ablations(cls, split_name: str = "validation") -> Dict[str, Any]:
        """Runs Full RACE against 4 systematic ablations."""
        base_dir = Path("datasets") / split_name
        events_path = base_dir / f"revenue_events_{split_name}.json"
        gt_path = base_dir / f"ground_truth_{split_name}.json"

        with open(events_path, "r", encoding="utf-8") as f:
            events = [RevenueEvent.model_validate(e) for e in json.load(f)]
        with open(gt_path, "r", encoding="utf-8") as f:
            ground_truths = [CaseGroundTruth.model_validate(g) for g in json.load(f)]

        base_a_res = BaselineAFixedRetry.evaluate_dataset(events, ground_truths)
        base_a_rec = base_a_res["total_recovered_revenue"]

        configs = {
            "Full System (RACE)": RACEEvaluationEngine(
                enable_ai_diagnosis=True,
                enable_dynamic_routing=True,
                enable_learning=True,
                enable_erv=True,
            ),
            "Ablation: No Dynamic Routing": RACEEvaluationEngine(
                enable_ai_diagnosis=True,
                enable_dynamic_routing=False,
                enable_learning=True,
                enable_erv=True,
            ),
            "Ablation: No AI Diagnosis": RACEEvaluationEngine(
                enable_ai_diagnosis=False,
                enable_dynamic_routing=True,
                enable_learning=True,
                enable_erv=True,
            ),
            "Ablation: No Outcome Learning": RACEEvaluationEngine(
                enable_ai_diagnosis=True,
                enable_dynamic_routing=True,
                enable_learning=False,
                enable_erv=True,
            ),
            "Ablation: No ERV Optimization": RACEEvaluationEngine(
                enable_ai_diagnosis=True,
                enable_dynamic_routing=True,
                enable_learning=True,
                enable_erv=False,
            ),
        }

        reports = {}
        print("\n===========================================================")
        print(f"RACE ABLATION STUDY RESULTS [{split_name.upper()} SET]")
        print("===========================================================")
        print(f"{'Configuration':<35} | {'Recovered (INR)':<15} | {'Rec Rate':<8} | {'Cost/Rupee':<10}")
        print("-" * 75)

        for name, engine in configs.items():
            rep = engine.evaluate_batch(events, ground_truths, baseline_a_recovered=base_a_rec)
            reports[name] = rep.to_dict()
            print(f"{name:<35} | INR {rep.actual_recovered_revenue:>11,.2f} | {rep.recovery_rate_pct:>6.2f}% | INR {rep.cost_per_recovered_rupee:>7.4f}")

        print("===========================================================\n")
        return reports


if __name__ == "__main__":
    AblationExperimentRunner.run_all_ablations("validation")
