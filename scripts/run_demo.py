"""RACE Interactive Demo & Live Server Launcher."""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import uvicorn
from evaluation.run_benchmark import run_benchmark_on_split
from evaluation.experiments.ablations import AblationExperimentRunner


def main():
    print("===========================================================")
    print("RACE: Revenue Adaptive Control Engine - Demonstration")
    print("===========================================================")
    print("1. Running baseline and RACE benchmark on test set...")
    run_benchmark_on_split("test")

    print("2. Running component ablation experiments...")
    AblationExperimentRunner.run_all_ablations("test")

    print("3. Starting Merchant Operations Console on http://127.0.0.1:8000 ...")
    uvicorn.run("backend.api.app:app", host="127.0.0.1", port=8000, log_level="info")


if __name__ == "__main__":
    main()
