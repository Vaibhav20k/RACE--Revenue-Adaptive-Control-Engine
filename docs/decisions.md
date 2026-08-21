# Architecture Decision Records (ADRs)

This document records the architectural and design decisions established during the development of RACE (Revenue Adaptive Control Engine).

---

## ADR-001: Separation of Deterministic Policy Gate and AI Reasoning Layer
* **Status**: Accepted
* **Context**: Generative models and statistical classifiers produce probabilistic outputs that can drift or hallucinate parameters under rare edge cases. In financial workflows, executing unauthorized transactions or violating retry limits carries severe legal and economic penalties.
* **Decision**: All financial and state-mutating actions must pass through an immutable, deterministic software policy gate before execution. The AI reasoning layer functions exclusively as an advisory and diagnostic engine.
* **Consequences**: Guarantees 100% compliance with merchant limits, eliminates rogue programmatic actions, and provides a clear audit boundary.

---

## ADR-002: Expected Recovery Value (ERV) as the Primary Objective Function
* **Status**: Accepted
* **Context**: Traditional retry systems optimize for attempt count or recovery rate without factoring in marginal execution fees, communication costs, cardholder friction, or chargeback penalties.
* **Decision**: Evaluate candidate recovery actions via explicit financial ERV:
  $$\text{ERV}(a) = P(\text{recovery} \mid \mathbf{x}, a) \times \text{Amount} - \text{Cost}(a) - \text{Friction}(a) - \text{Risk}(a)$$
  If $\max_{a} \text{ERV}(a) \le 0$, the engine halts automated actions (`STOP`).
* **Consequences**: Maximizes net recovered currency, prevents customer annoyance on low-value transactions, and avoids wasteful gateway calls.

---

## ADR-003: Authoritative Gateway Ledger Outcome Observation
* **Status**: Accepted
* **Context**: An API returning HTTP 200 on an action dispatch only confirms the request was accepted; it does not prove money was captured. Network timeouts can leave payment states ambiguous.
* **Decision**: Revenue is never classified as recovered based on action dispatch responses. Outcomes are recorded exclusively when the authoritative payment gateway ledger confirms a definitive `captured`/`paid` status.
* **Consequences**: Guarantees accounting integrity and eliminates false positive recovery claims.

---

## ADR-004: Strict Cryptographic Idempotency Key Architecture
* **Status**: Accepted
* **Context**: Network retries, concurrent webhook deliveries, or overlapping recovery triggers can cause duplicate payment debits.
* **Decision**: Every action must generate a deterministic SHA-256 idempotency key:
  $$\text{Key} = \text{SHA256}(\text{merchant\_id} : \text{customer\_id} : \text{payment\_id} : \text{action} : \text{attempt})$$
  Duplicate keys within the TTL window return cached execution results without re-dispatching.
* **Consequences**: Eliminates double-charge risk under upstream timeouts or concurrent webhook bursts.

---

## ADR-005: Closed-Loop Bayesian Prior Smoothing
* **Status**: Accepted
* **Context**: Empirical recovery success rates for specific failure-strategy pairs can fluctuate wildly with small sample sizes, leading to premature strategy abandonment.
* **Decision**: Implement Bayesian pseudo-count smoothing ($w = 3.0$) combining empirical observation counts with historical baseline priors:
  $$P_{\text{smoothed}} = \frac{\text{SuccessCount} + (\text{PriorRate} \times 3.0)}{\text{SampleCount} + 3.0}$$
* **Consequences**: Stabilizes dynamic ERV calculations and allows adaptive learning as gateway conditions evolve.

---

## ADR-006: Persistent SQLite Storage for Custom Scenarios with Benchmark Isolation
* **Status**: Accepted
* **Context**: Merchants require the capability to test custom failure scenarios, while researchers require reproducible, unpolluted scientific validation benchmarks.
* **Decision**: Store user-injected test cases in a persistent SQLite database (`data/race_cases.db`) tagged with `source = "CUSTOM"`. Strictly isolate the frozen validation dataset (`datasets/validation/`) from custom database insertions.
* **Consequences**: Enables interactive test-case creation without contaminating the frozen scientific benchmark.

---

## ADR-007: 8-State Unidirectional Recovery Lifecycle Machine
* **Status**: Accepted
* **Context**: Unstructured state management leads to race conditions, zombie retries, and invalid state jumps.
* **Decision**: Enforce an explicit 8-state recovery finite state machine (`AT_RISK` $\to$ `DIAGNOSED` $\to$ `ACTION_SELECTED` $\to$ `POLICY_APPROVED` / `ESCALATED` / `STOPPED` $\to$ `ACTION_EXECUTED` $\to$ `OUTCOME_OBSERVED` $\to$ `RECOVERED`).
* **Consequences**: Eliminates invalid transitions and ensures every lifecycle step is tracked in the immutable audit ledger.

---

## ADR-008: Dedicated Scientific Benchmark and Specification Routing
* **Status**: Accepted
* **Context**: Overloading the operational console with research papers and benchmark tables creates visual clutter for merchant operators.
* **Decision**: Separate the application into dedicated routes: `/` (Operational Console), `/benchmarks` (Scientific Validation & Research), and `/about` (Technical Specification).
* **Consequences**: Provides clean ergonomics for both merchant operators and research evaluators.
