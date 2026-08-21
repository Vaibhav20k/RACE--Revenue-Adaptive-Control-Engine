# Architecture Decision Records (ADRs)

## ADR-001: Separation of Deterministic Policy Gate and AI Reasoning Layer
- **Status:** Accepted
- **Context:** Large language models and statistical ML models can produce unexpected outputs or hallucinated parameters. Financial workflows require absolute guarantees regarding retry limits, amount caps, and idempotency.
- **Decision:** All financial and state-mutating actions must pass through an immutable, deterministic policy gate before execution. The AI layer serves solely as an advisory and diagnostic engine.
- **Consequences:** Eliminates possibility of rogue agent spending, ensures 100% compliance with financial rules, simplifies audit verification.

## ADR-002: Expected Recovery Value (ERV) as Primary Objective Function
- **Status:** Accepted
- **Context:** Simple retry systems optimize for recovery count or attempt count without considering intervention cost, customer friction, or probability calibration.
- **Decision:** Evaluate candidate actions by explicit ERV: $ERV = P(\text{recovery}) \times \text{amount} - \text{cost} - \text{friction} - \text{risk}$. Actions with negative ERV default to `STOP`.
- **Consequences:** Maximizes net business value, prevents customer harassment, avoids wasteful gateway calls.

## ADR-003: Authoritative External State Observation
- **Status:** Accepted
- **Context:** An API returning HTTP 200 on an action dispatch does not confirm money was captured. Network timeouts can leave payment states uncertain.
- **Decision:** Never mark revenue as recovered based solely on dispatch responses. Outcome is only recorded when authoritative gateway state is verified (`PAID`/`RECOVERED`).
- **Consequences:** Guarantees audit integrity and prevents false positive recovery reporting.

## ADR-004: Strict Idempotency Key Architecture
- **Status:** Accepted
- **Context:** Retried requests or concurrent webhook events can trigger duplicate payment charges.
- **Decision:** Every execution requires a deterministic SHA-256 idempotency key derived from merchant, customer, payment, action type, and attempt number.
- **Consequences:** Prevents duplicate charges under network retry or timeout scenarios.
