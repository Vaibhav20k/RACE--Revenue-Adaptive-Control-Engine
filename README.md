# RACE — Revenue Adaptive Control Engine

[![RACE CI](https://github.com/Vaibhav20k/RACE--Revenue-Adaptive-Control-Engine/actions/workflows/ci.yml/badge.svg)](https://github.com/Vaibhav20k/RACE--Revenue-Adaptive-Control-Engine/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/Tests-85%20passing-emerald.svg)](tests/)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue.svg)](pyproject.toml)
[![Razorpay Test Mode](https://img.shields.io/badge/Razorpay-Test%20Mode%20Integrated-blueviolet.svg)](docs/RAZORPAY_INTEGRATION.md)
[![License](https://img.shields.io/badge/License-MIT-slate.svg)](LICENSE)

> **Autonomous Closed-Loop Revenue Recovery Decision Engine**  
> **Track:** Track 03 — AI Revenue Recovery  
> **Status:** Hackathon Release / Fully Validated (85/85 Tests Passing)  
> **Repository:** [GitHub](https://github.com/Vaibhav20k/RACE--Revenue-Adaptive-Control-Engine)  
> **Local Development Console:** `http://127.0.0.1:8000/`

---

## Executive Summary

**RACE (Revenue Adaptive Control Engine)** is an intelligent, closed-loop revenue recovery decision engine that detects revenue at risk, diagnoses root causes from failure telemetry, evaluates competing interventions via **Expected Recovery Value (ERV)**, enforces **deterministic financial safety constraints**, executes bounded actions, and authoritatively verifies real payment settlement.

Traditional payment recovery mechanisms rely on naive fixed-interval retry loops or static rule tables. These approaches cause severe customer friction, gateway retry penalties, elevated processing fees, and poor recovery rates. RACE reframes revenue recovery as an **economic optimization problem under uncertainty**:

```text
Revenue Event ──► Diagnosis ──► ERV Ranking ──► Policy Gate ──► Bounded Action ──► Ledger Verification ──► Bayesian Learning
```

On the 200-case frozen held-out synthetic validation benchmark, RACE achieved a **92.99% revenue-weighted recovery rate** (matching the strongest rule-based baseline and substantially outperforming Baseline A's 27.61%), an **83.50% transaction-count recovery rate** (INR 1,680,352.07 recovered out of INR 1,807,104.53 at risk), and delivered **+INR 1,181,402.94 (+236.8%) incremental revenue uplift** over naive fixed retries with **0 policy violations**, **0 duplicate charges**, and **100% audit completeness**.

---

## The Problem: The High Cost of Uncalibrated Retries

Digital merchants lose billions annually to payment failures, checkout dropoffs, and recurring billing declines. When a payment fails, it is rarely a single static event:

1. **Card Balance & Limit Deficits**: Retrying immediately fails with 85%+ probability; sending a proactive customer notification and deferring retry yields 80%+ success.
2. **Gateway Switch Degradation**: Blasting retries against a degraded banking switch causes immediate failure cascades and acquirer rate-limiting.
3. **Authentication & 3DS Dropoffs**: Automated retries without cardholder involvement are rejected by the card network.
4. **Permanent Fraud & Hard Declines**: Retrying stolen or canceled cards triggers chargeback penalties and processing fines.
5. **Uncertain Payment States**: Retrying after an upstream gateway timeout without ledger reconciliation risks double-charging the cardholder.

The fundamental operational question is not merely *"Did the payment fail?"*, but:

> **Is this revenue economically recoverable, which intervention maximizes net recovery value, is that intervention safe to execute, and did the ledger authoritatively capture the funds?**

---

## The RACE Approach: Closed-Loop Decision Control

RACE replaces uncalibrated retry scripts with a unidirectional, failure-safe control plane.

```mermaid
flowchart TD
    A[Payment Failure / Dropoff Event] --> B[Revenue-at-Risk & Recoverability Filter]
    B --> C[Context Enrichment & Root Cause Diagnosis]
    C --> D[Candidate Strategy Generation]
    D --> E[Expected Recovery Value Engine]
    E --> F{Deterministic Policy Gate}
    F -->|Blocked / Limit Exceeded| G[STOP / Escalation Queue]
    F -->|Approved & Cleared| H[Bounded Test-Mode Execution]
    H --> I[Authoritative Ledger Outcome Verification]
    I --> J[Closed-Loop Bayesian Learning]
    J --> K[Immutable State Audit Ledger]
```

### Core Pipeline Stages:
1. **Detect**: Ingests failed payment webhooks and flags revenue at risk.
2. **Recoverability**: Filters hard declines (fraud, permanent stops) from recoverable opportunities.
3. **Diagnose**: Synthesizes issuer decline codes, gateway switch health, and customer history.
4. **Candidate Generation**: Spawns admissible strategies (`RETRY_NOW`, `RETRY_LATER`, `REMINDER_THEN_RETRY`, `HUMAN_ESCALATION`, `STOP`).
5. **ERV Optimization**: Ranks strategies by net monetary recovery minus marginal costs, friction, and downside risk.
6. **Safety Gate**: Deterministically validates retry caps ($\le 3$), amount thresholds ($\le 50\text{K}$), cooldowns, and opt-outs.
7. **Bounded Execution**: Dispatches test-mode action locked with a deterministic SHA-256 idempotency key.
8. **Outcome Verification**: Queries authoritative gateway ledger to verify definitive settlement.
9. **Bayesian Learning**: Smooths and updates empirical priors for subsequent recovery cycles.

---

## Decision Logic: Expected Recovery Value (ERV)

RACE evaluates every candidate intervention $a \in \mathcal{A}$ using an explicit financial objective function:

$$\text{ERV}(a) = P(\text{recovery} \mid \text{context}, a) \times \text{Amount} - \text{Cost}(a) - \text{Friction}(a) - \text{Risk}(a)$$

```text
┌───────────────────────────────────────────────────────────────────────────┐
│                           ERV FORMULA BREAKDOWN                           │
├───────────────────────────────────────────────────────────────────────────┤
│  P(recovery | context, a) : Probability of settlement given failure context│
│  Amount                   : Gross transaction value at risk (INR)        │
│  Cost(a)                  : Marginal communication or gateway processing fee│
│  Friction(a)              : Churn penalty for intrusive customer contacts │
│  Risk(a)                  : Operational/compliance penalty for chargebacks│
└───────────────────────────────────────────────────────────────────────────┘
```

If $\max_{a} \text{ERV}(a) \le 0$, the engine halts automated attempts (`STOP`) to preserve merchant capital and avoid customer harassment.

---

## First-Class Safety: Engine Proposes, Deterministic Policy Authorizes

RACE enforces a strict architectural boundary: **RACE's decision engine proposes recovery actions using recoverability estimation, ERV optimization, contextual reasoning, and adaptive empirical/Bayesian statistics. Only deterministic policy controls can authorize execution.**

```mermaid
flowchart LR
    subgraph Reasoning Layer
        ML[Diagnostic & ERV Engine] -->|Proposes Strategy + ERV| Prop[Proposed Action]
    end
    
    subgraph Policy Layer
        Prop --> Gate{Deterministic Policy Gate}
        Gate -->|Retry Count > 3| Block1[REJECT: RETRY_LIMIT_EXCEEDED]
        Gate -->|Amount > 50K| Block2[ESCALATE: HUMAN_REVIEW_REQUIRED]
        Gate -->|Customer Opt-Out| Block3[HALT: OPT_OUT_HARD_STOP]
        Gate -->|Cooldown Active| Block4[DEFER: COOLDOWN_VIOLATION]
        Gate -->|Payment State Unknown| Block5[HOLD: RECONCILIATION_REQUIRED]
        Gate -->|All 6 Invariants Pass| Exec[Authorize Test-Mode Dispatch]
    end
```

### Deterministic Invariants Enforced on Every Action:
1. **Retry Cap ($\le 3$)**: Prevents infinite retry storms against failed payment instruments.
2. **Monetary Threshold ($\le \text{INR } 50,000$)**: High-value transactions automatically divert to human escalation.
3. **Mandatory Cooldowns**: Enforces time buffers (default: 30 mins) between consecutive payment attempts.
4. **Customer Opt-Out Hard Stop**: If a customer opts out or files a dispute, automated recovery halts immediately.
5. **Cryptographic Idempotency**: Derived via $\text{SHA256}(\text{merchant} : \text{customer} : \text{payment} : \text{action} : \text{attempt})$. Duplicate requests return cached results without re-executing.
6. **Authoritative Pre-Condition Check**: Prevents retrying transactions that are already captured or in an ambiguous state.

---

## Architectural Differentiators

| Dimension | Naive Retry Loop | Static Rule Engine | RACE Control Engine |
| :--- | :--- | :--- | :--- |
| **Objective** | Attempt count | Code-to-action match | Net Expected Recovery Value (ERV) |
| **Context Awareness** | None | Static mapping table | Route health, customer prior, decline reason |
| **Intervention Space** | Single fixed retry | Hardcoded branching | 5 competing multi-channel strategies |
| **Safety Governance** | Basic counter | Config file rules | Deterministic 6-invariant immutable gate |
| **Settlement Truth** | Assumed on HTTP 200 | Assumed on dispatch | Authoritative gateway ledger verification |
| **Idempotency** | Absent / partial | Header-dependent | Deterministic SHA-256 case-action lock |
| **Learning Feedback** | Static | Manual rule review | Closed-loop Bayesian prior smoothing |

---

## Measured Scientific Benchmark Results

RACE was benchmarked across a frozen held-out validation suite of **200 synthetic payment failure cases** (`datasets/validation/`) representing 8 failure archetypes (insufficient funds, gateway degradation, network timeout, 3DS authentication drops, expired cards, suspected fraud, user dropoff, unknown gateway errors).

> **Synthetic Dataset Disclosure**: Benchmark evaluation is conducted on a reproducible, held-out suite of 200 synthetic test cases constructed with empirical ground-truth counterfactuals. Live Razorpay Test Mode transactions and operational custom scenarios are strictly isolated and excluded from benchmark metrics.

### Benchmark Comparison (200 Held-Out Synthetic Validation Cases)

| System / Model | Tx Recovery Rate | Revenue-Weighted Rate | Gross Recovered | Total Fees | Cost / Rupee | Net Uplift vs Baseline A |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline A (Fixed Retry)** | 57.50% (115/200) | **27.61%** | INR 498,949.13 | INR 1,850.00 | INR 0.0037 | — |
| **Baseline B (Rule-Based)** | 83.50% (167/200) | **92.99%** | INR 1,680,352.07 | INR 1,750.00 | INR 0.0010 | +INR 1,181,402.94 |
| **Baseline C (ML Ranking)** | 70.50% (141/200) | **89.65%** | INR 1,620,005.72 | INR 1,450.00 | INR 0.0009 | +INR 1,121,056.59 |
| **RACE (Full Engine)** | **83.50% (167/200)** | **92.99% (~93.0%)** | **INR 1,680,352.07** | **INR 1,693.00** | **INR 0.0010** | **+INR 1,181,402.94 (+236.8%)** |

```text
========================================================================
KEY SCIENTIFIC PERFORMANCE METRICS (200 VALIDATION CASES)
========================================================================
Total Revenue at Risk:              INR 1,807,104.53 (~INR 18.07L)
Total Revenue Recovered:            INR 1,680,352.07 (~INR 16.80L)
Revenue-Weighted Recovery Rate:     92.9859% (~93.0%)
Transaction-Count Recovery Rate:    83.50% (167 / 200 cases)
Incremental Uplift vs Baseline A:   +INR 1,181,402.94 (+236.8%)
Baseline A Revenue Recovery Rate:   27.6104% (INR 498,949.13)
Baseline A Tx Recovery Rate:        57.50% (115 / 200 cases)
Fee Efficiency:                     INR 0.0010 per rupee recovered
Policy Violations:                  0 (100% compliant)
Duplicate Payment Dispatches:       0 (Zero duplicates)
Graceful Timeout Recovery:          100%
========================================================================
```

### Component Ablation Study (Independent Audit)

| Configuration | Recovered Revenue | Tx Recovery Rate | Rev-Weighted Rate | Action Cost | Scientific Finding / Caveat |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Full System (RACE)** | **INR 1,680,352.07** | **83.50%** | **92.99%** | **INR 1,693.00** | **Optimal multi-candidate balance & fee efficiency.** |
| **Ablation: No Dynamic Routing** | INR 1,680,352.07 | 83.50% | 92.99% | INR 1,693.00 | *Finding*: The No Dynamic Routing ablation did not materially change terminal recovery performance on this validation split; its primary contribution is in bypassing agent diagnostic overhead and routing latency on deterministic cases. |
| **Ablation: No AI Diagnosis** | INR 1,680,352.07 | 83.50% | 92.99% | INR 1,693.00 | Terminal recovery unchanged when downstream ERV engine & policy gate evaluate complete feature sets. |
| **Ablation: No Outcome Learning** | INR 1,680,352.07 | 83.50% | 92.99% | INR 1,783.00 | Higher action cost (+INR 90) because priors remain static without closed-loop Bayesian smoothing. |
| **Ablation: No ERV Optimization** | INR 1,537,466.03 | 62.00% | 85.08% | INR 1,370.00 | **-21.5% recovery drop** (-INR 142.88K) when defaulting to unoptimized single actions. |

---

## Razorpay Test Mode Integration

RACE integrates directly with Razorpay's API in **Test Mode** to validate real external payment lifecycles:

* **Authenticated API Execution**: Dispatches real server-side requests to Razorpay's Orders (`/v1/orders`) and Payment Links (`/v1/payment_links`) APIs using test keys (`rzp_test_...`).
* **Authoritative Outcome Verification**: Queries the live payment status directly from Razorpay's gateway to verify settlement (`captured` vs `failed`/`unpaid`).
* **Webhook Processing**: Receives and validates Razorpay webhooks (`payment.captured`, `payment.failed`, `order.paid`) using cryptographic HMAC-SHA256 signature verification.
* **Resilient Mock Fallback**: In the absence of API credentials, the system automatically falls back to an offline deterministic mock adapter.

> **Environment Disclosure**: RACE uses Razorpay Test Mode for integration validation; no live-money transactions are used. Credentials are read securely from environment variables and redacted in all logs.

---

## User-Created Custom Test Scenarios

RACE provides an interactive scenario injector enabling merchants to test arbitrary failure events:

1. **Persistent SQLite Storage**: Custom cases are permanently persisted in `data/race_cases.db` with 27-column event schemas.
2. **Identical Decision Pipeline**: Custom cases flow through the exact same ERV ranking, policy gates, bounded execution, and outcome ledger.
3. **Scientific Benchmark Isolation**: Custom cases receive `source = "CUSTOM"` and are strictly excluded from the frozen 200-case scientific validation benchmark dataset.

---

## Quick Start & Local Verification

### 1. Prerequisites
- Python 3.11+
- Virtual environment (`venv`)

### 2. Installation & Server Launch
```bash
# Clone the repository
git clone https://github.com/Vaibhav20k/RACE--Revenue-Adaptive-Control-Engine.git
cd RACE--Revenue-Adaptive-Control-Engine

# Create virtual environment & install dependencies
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .

# Launch local FastAPI uvicorn server
python -m uvicorn backend.api.app:app --host 127.0.0.1 --port 8000
```

### 3. Running Automated Tests
```bash
# Execute full 85-test verification suite
python -m pytest -v
```

---

## Optional Live Demo & Walkthrough

> **Demo Tunnel Note**: The optional public link uses an ephemeral Cloudflare tunnel connected to the local RACE development server and is accessible only while the local service and tunnel are actively running. The authoritative submission and evaluation artifact is this GitHub repository.

* **Optional Live Demo**: [https://valuation-simon-receives-broad.trycloudflare.com/](https://valuation-simon-receives-broad.trycloudflare.com/)
* **Local Development Console**: `http://127.0.0.1:8000/`

### Step-by-Step Operator Journey:
1. Open the console (`http://127.0.0.1:8000/`) in your browser.
2. In the dark **TEST A SCENARIO** panel, select `case_0601` (Card Limit Deficit) or click **+ Add Custom Scenario** to inject a novel failure event.
3. The **Payment Incident** card renders center-aligned with the gross amount and failure telemetry.
4. Click **Investigate Case**:
   - The Payment Incident smoothly transitions to the left.
   - The **Organic Neural Canvas** animates with a synchronized `03` $\to$ `02` $\to$ `01` countdown.
   - The decision centerpiece reveals `REMINDER THEN RETRY` with **INR 901.03 Net ERV**.
   - The 6 deterministic policy invariants verify green checkmarks.
5. Click **Execute Recovery Action** to dispatch test-mode settlement and observe authoritative gateway verification (`PAID` / `captured`).
6. Navigate to **`/benchmarks`** for full scientific validation tables and live benchmark execution.
7. Navigate to **`/about`** for comprehensive architectural documentation and mathematical formulas.

---

## Continuous Integration & Container Verification

RACE enforces automated verification on every pull request and push to `main` via GitHub Actions (`.github/workflows/ci.yml`).

```mermaid
flowchart LR
    A[Git Push / PR] --> B[Static Compilation Check]
    B --> C[Pytest 85 Test Suite]
    C --> D[Scientific Benchmark Reproducibility]
    D --> E[Docker Build & Health Probe Check]
    E --> F[Release Validation Ready]
```

### 1. Automated CI Pipeline Stages
* **Static Verification**: `python -m compileall` across all engine modules.
* **Test Suite Execution**: Full 85-test verification across matrix Python 3.11 & 3.12.
* **Benchmark Validation**: Executes `evaluation/run_benchmark.py --split validation` to verify zero drift in recovery rates.
* **Container Health Verification**: Builds the multi-stage `Dockerfile` and executes health probes against `http://localhost:8000/health`.

### 2. Containerized Deployment (Docker & Compose)
```bash
# Build and launch container
docker compose up --build -d

# Verify container health probe
curl http://localhost:8000/health
```

### 3. Operational Health Probes
* **Root Health Check**: `GET /health` — Returns service status, version, and UTC timestamp.
* **API Health Check**: `GET /api/v1/health` — Returns REST router operational state.

---

## Documentation Map

| Document | Purpose & Technical Scope |
| :--- | :--- |
| **[System Vision](docs/VISION.md)** | Long-term control plane roadmap, merchant autonomy, and core engineering principles |
| **[System Architecture](docs/ARCHITECTURE.md)** | Modular topology, component specifications, 8-state recovery FSM, and boundary constraints |
| **[Decision Engine](docs/DECISION_ENGINE.md)** | Probabilistic recoverability, candidate generation, ERV derivation, and Bayesian smoothing |
| **[Safety & Financial Policy](docs/SAFETY_AND_POLICY.md)** | Deterministic 6-invariant policy gate, retry caps, 50K thresholds, and SHA-256 idempotency |
| **[Scientific Evaluation](docs/EVALUATION.md)** | 200 held-out cases, Baselines A/B/C comparisons, ablation studies, and benchmark provenance |
| **[Razorpay Test Mode & Webhooks](docs/RAZORPAY_INTEGRATION.md)** | Authenticated test-mode execution, HMAC-SHA256 webhooks, and ledger reconciliation |
| **[Implementation Phases](docs/PHASES.md)** | Chronological 18-phase implementation log and test suite expansion |
| **[Architecture Decisions (ADRs)](docs/DECISIONS.md)** | Architectural decision records justifying ERV, policy separation, and ledger reconciliation |

---

## System License

RACE is released under the **MIT License**. Engineered for transparent, auditable, closed-loop revenue operations.
