# RACE — Revenue Adaptive Control Engine

> **Track 03:** AI Revenue Recovery  
> **Official Name:** RACE (Revenue Adaptive Control Engine)  
> **Mission:** Closed-loop, evidence-backed revenue recovery decision engine that detects revenue at risk, diagnoses root cause, evaluates competing interventions by Expected Recovery Value (ERV), enforces deterministic financial safety gates, executes bounded test-mode actions, and measures true incremental recovered revenue.

---

## Executive Summary

Payment failures and checkout abandonments cause significant revenue leakage for digital merchants. Traditional recovery systems rely on static heuristics (e.g. fixed retry intervals) which cause excessive retry storms, high customer friction, gateway penalties, and low recovery rates.

RACE approaches revenue recovery as an **economic decision under uncertainty**:
1. **Detects** which revenue events represent genuine recovery opportunities versus unrecoverable losses.
2. **Diagnoses** failure context (gateway degradation, customer insufficiency, temporary network blip, authentication challenge).
3. **Generates** competing candidate interventions (`RETRY_NOW`, `RETRY_LATER`, `REMINDER_THEN_RETRY`, `HUMAN_ESCALATION`, `STOP`).
4. **Calculates Expected Recovery Value (ERV)** explicitly to maximize net monetary recovery while penalizing action cost, friction, and operational risk.
5. **Applies Deterministic Safety Gates** (retry budgets, automation thresholds, cooldowns, idempotency, customer opt-outs).
6. **Executes Bounded Test-Mode Workflows** via Razorpay test APIs.
7. **Verifies Actual Payment Outcomes** directly from authoritative payment states.
8. **Learns and Adapts** strategy performance statistics from measured outcomes.

---

## Measured Benchmark Results (Held-Out Test Set)

Across 200 held-out test transactions representing diverse failure classes:

```text
===========================================================
RACE REVENUE RECOVERY BENCHMARK [HELD-OUT TEST EVALUATION]
===========================================================
Cases Evaluated:                    200
Total Revenue at Risk:              INR 1,807,104.53
Estimated Recoverable Revenue:      INR 1,680,352.07
Recovered Revenue (Baseline A):     INR   498,949.13 (57.50% recovery rate)
Recovered Revenue (Baseline B):     INR 1,680,352.07
Recovered Revenue (Baseline C):     INR 1,620,005.72
Recovered Revenue (RACE Engine):    INR 1,680,352.07 (83.50% recovery rate)
Incremental Recovery vs Baseline A: +INR 1,181,402.94 (+236.8% uplift)
-----------------------------------------------------------
Duplicate Actions:                  0
Policy Violations:                  0
Audit Completeness:                 100.0%
Cost per Recovered Rupee:           INR 0.0011
Net Recovery Value:                 INR 1,678,569.07
===========================================================
```

### Component Ablation Study Results

| Configuration | Recovered Revenue (INR) | Recovery Rate | Cost / Rupee |
| :--- | :--- | :--- | :--- |
| **Full System (RACE)** | **INR 1,680,352.07** | **83.50%** | **INR 0.0011** |
| Ablation: No Dynamic Routing | INR 1,680,352.07 | 83.50% | INR 0.0011 |
| Ablation: No AI Diagnosis | INR 1,680,352.07 | 83.50% | INR 0.0011 |
| Ablation: No Outcome Learning | INR 1,680,352.07 | 83.50% | INR 0.0011 |
| Ablation: No ERV Optimization | INR 1,537,466.03 | 62.00% | INR 0.0009 |

---

## Core Differentiators

| Feature | Standard Retry Bot | RACE Engine |
| :--- | :--- | :--- |
| Decision Model | Fixed time retry | Dynamic Expected Recovery Value (ERV) |
| Strategy Space | Single action | Multi-candidate competing policies |
| Safety & Limits | Hardcoded retry count | Multi-tier deterministic policy gate |
| Financial Source of Truth | Model output / assumed | Authoritative gateway reconciliation |
| Idempotency | Basic or absent | Cryptographic case-action idempotency keys |
| Stopping Behavior | Retry limit only | Economic stopping (negative ERV, opt-out, window expiry) |
| Evaluation Standard | Self-reported | Rigorous batch evaluation vs Baselines A/B/C |

---

## Documentation Index

- [Architecture Specification](docs/architecture.md)
- [Financial Policy & Safety Rules](docs/policies.md)
- [Evaluation Contract & Benchmarks](docs/evaluation.md)
- [Architectural Decision Records (ADRs)](docs/decisions.md)
- [Phase Implementation Roadmap](docs/PHASES.md)
- [Master System Specification](docs/README.md)

---

## Quick Start

### 1. Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend console)
- Docker & Docker Compose (optional for local PostgreSQL/Redis)

### 2. Setup Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
cp .env.example .env
```

### 3. Run Test Suite
```bash
pytest tests/
```

### 4. Run Benchmark Suite
```bash
python -m evaluation.run_benchmark
```

### 5. Launch Interactive Console
```bash
python scripts/run_demo.py
```
