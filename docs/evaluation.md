# RACE Evaluation & Benchmark Specification

## 1. Evaluation Philosophy

RACE evaluates revenue recovery strictly against objective financial, decision quality, and reliability metrics. No numbers are claimed without empirical benchmark measurement.

## 2. Baselines for Comparison

### Baseline A — Fixed Retry (Naive Industry Default)
- Simple policy: Retries all failed payments after a fixed time interval (e.g. 1 hour) up to 3 times.
- Ignores customer context, failure reason, and economic value.

### Baseline B — Rule-Based Recovery
- Uses heuristic lookup tables mapping failure codes to actions (e.g. network failure -> retry in 15 mins, insufficient balance -> retry in 24 hours).
- Does not compute dynamic Expected Recovery Value.

### Baseline C — ML Ranking Without Agentic Diagnosis
- Supervised ML model predicting recovery probability $P(\text{recovery})$ based on features, choosing argmax probability.
- Lacks semantic diagnostic context, ambiguity handling, and multi-step policy coordination.

### RACE (Proposed System)
- Full closed-loop decision engine: Detection -> Context Diagnosis -> ERV Evaluation -> Policy Gating -> Safe Execution -> Verification -> Closed-Loop Learning.

## 3. Key Performance Indicators (KPIs)

### 3.1 Business Impact
- **Total Revenue at Risk (INR)**: $\sum \text{amount of failed/abandoned events}$
- **Estimated Recoverable Revenue (INR)**: $\sum (\text{recoverable\_amount} \times P(\text{rec}))$
- **Actual Recovered Revenue (INR)**: $\sum \text{amount successfully captured post-intervention}$
- **Incremental Recovered Revenue (INR)**: $\text{Recovered}(\text{RACE}) - \text{Recovered}(\text{Baseline A})$
- **Recovery Rate (%)**: $\frac{\text{Cases Recovered}}{\text{Total Cases at Risk}} \times 100$
- **Cost per Recovered Rupee**: $\frac{\text{Total Intervention Cost}}{\text{Total Recovered Revenue}}$

### 3.2 Decision Quality
- **Intervention Success Rate**: $\frac{\text{Successful Interventions}}{\text{Total Actions Attempted}}$
- **Unnecessary Intervention Rate**: $\frac{\text{Actions on unrecoverable or auto-resolved cases}}{\text{Total Actions Attempted}}$
- **Stopping Rule Compliance**: Rate at which policy halts actions when $ERV \le 0$ or limit reached.
- **Escalation Appropriateness**: Percentage of escalated cases meeting threshold/uncertainty criteria.

### 3.3 Reliability & Safety
- **Duplicate Action Count**: Must be 0 (enforced via idempotency).
- **Policy Violation Count**: Must be 0 (enforced via deterministic policy gate).
- **Audit Completeness**: Must be 100% (every decision, state change, and action logged).
- **Graceful Failure Rate**: Rate at which timeouts/unknown states are safely reconciled without duplicate charge attempts.
