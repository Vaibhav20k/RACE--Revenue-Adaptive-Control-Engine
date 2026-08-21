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

## Architecture Overview

```text
Revenue Event
      |
      v
Revenue-at-Risk Detection (ML / Statistical Classifier)
      |
      v
Context Aggregation & Diagnosis Engine
      |
      v
Candidate Strategy Generation & Routing
      |
      v
Expected Recovery Value (ERV) Engine
      |
      v
Deterministic Policy & Safety Gate
      |
      v
Bounded Execution Layer (Razorpay Test Mode)
      |
      v
Authoritative Outcome Observation & Verification
      |
      +---> RECOVERED / RETRY_ELIGIBLE / STOPPED / ESCALATED / FAILED
      |
      v
Closed-Loop Learning & Strategy Statistics Update
      |
      v
Audit Ledger & Merchant Operations Console
```

---

## Economic Objective: Expected Recovery Value (ERV)

Every candidate strategy is evaluated by:

$$\text{ERV}(a) = P(\text{recovery} \mid \text{context}, a) \times \text{Recoverable Amount} - \text{Cost}(a) - \text{FrictionPenalty}(a) - \text{RiskPenalty}(a)$$

Where:
- $\text{Revenue at Risk}$: Total monetary value of failed or abandoned transactions.
- $\text{Recoverable Revenue}$: Upper-bound monetary value realistically retrievable given constraints.
- $\text{Actual Recovered Revenue}$: Authoritatively verified funds captured after intervention.
- $\text{Incremental Recovered Revenue}$: Net recovery value generated above the deterministic fixed-retry baseline.

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
