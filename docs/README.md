# RACE Documentation Index & Master Guide

Welcome to the technical documentation repository for **RACE (Revenue Adaptive Control Engine)**, an autonomous closed-loop revenue recovery decision engine developed for Track 03 (AI Revenue Recovery).

---

## Documentation Navigation

| Document | Description | Target Audience |
| :--- | :--- | :--- |
| **[System Vision](VISION.md)** | Long-term control plane roadmap, merchant autonomy, and core engineering principles | Product & Strategy Reviewers |
| **[System Architecture](ARCHITECTURE.md)** | Modular topology, component specifications, 8-state recovery FSM, and boundary constraints | System Architects & Engineers |
| **[Decision Engine](DECISION_ENGINE.md)** | Probabilistic recoverability, candidate generation, ERV derivation, and Bayesian smoothing | ML Engineers & Economists |
| **[Safety & Policy](SAFETY_AND_POLICY.md)** | Deterministic 6-invariant policy gate, retry caps, 50K thresholds, and SHA-256 idempotency | Risk, Compliance & Security |
| **[Scientific Evaluation](EVALUATION.md)** | 200 held-out cases, Baselines A/B/C comparisons, ablation studies, and benchmark provenance | Research Reviewers & Evaluators |
| **[Implementation Phases](PHASES.md)** | Chronological 17-phase implementation log and test suite expansion | Code Reviewers |
| **[Architecture Decisions (ADRs)](DECISIONS.md)** | Architectural decision records justifying ERV, policy separation, and ledger reconciliation | Technical Evaluators |

---

## Core System Highlights

1. **Economic Decision Optimization**: Replaces uncalibrated retry loops with **Expected Recovery Value (ERV)** optimization:
   $$\text{ERV}(a) = P(\text{recovery} \mid \text{context}, a) \times \text{Amount} - \text{Cost}(a) - \text{Friction}(a) - \text{Risk}(a)$$
2. **Deterministic Safety Architecture**: AI models diagnose and propose interventions, but only the deterministic **Policy Gate** can authorize financial dispatch.
3. **Authoritative Ledger Reconciliation**: Execution is never treated as equivalent to recovery; money is only booked when confirmed on the gateway ledger.
4. **Empirically Measured Uplift**: +INR 1,181,402.94 (+236.8%) recovery uplift over naive retry defaults across 200 held-out validation cases.
5. **Zero Policy Violations**: 100% compliance across retry limits, amount thresholds, and customer opt-out filters.
