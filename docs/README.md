# AI Revenue Recovery Decision Engine
## Track 03 — AI Revenue Recovery

> **Hackathon Track:** AI Revenue Recovery  
> **Core goal:** Find revenue that is slipping away, determine why it is at risk, choose the right recovery intervention, execute a bounded recovery workflow, and prove how much money was actually recovered.
>
> **Primary product:** An evidence-backed, context-aware **Revenue Recovery Decision Engine**.
>
> **Core evaluation principle:** The project is successful only when it can demonstrate measurable recovered revenue across a batch, with compliant escalation, stopping rules, safe money actions, and a complete audit trail.

---

# 1. Project in Short

Revenue loss rarely happens in one clean step.

A merchant may experience:

- payment failures,
- temporary bank or gateway degradation,
- checkout abandonment,
- failed recurring payments,
- overdue receivables,
- repeated retry failures,
- customers who need a different intervention,
- or recovery opportunities where taking action is not worth the cost or customer friction.

A weak system only says:

```text
Revenue at risk = ₹X
```

This project must go further:

```text
Revenue Event
     ↓
Detect Revenue at Risk
     ↓
Understand Why
     ↓
Estimate Recoverability
     ↓
Generate Candidate Interventions
     ↓
Estimate Expected Recovery Value
     ↓
Apply Safety / Policy Rules
     ↓
Execute Bounded Recovery Action
     ↓
Observe Actual Outcome
     ↓
Recover / Retry / Stop / Escalate
     ↓
Measure ₹ Recovered
     ↓
Learn From Outcome
```

The system is therefore a **closed-loop revenue recovery decision system**, not a dashboard, chatbot, or simple payment retry script.

---

# 2. Hackathon Track Requirement

The system must satisfy Track 03's core requirements:

1. Detect revenue at risk.
2. Determine the appropriate intervention.
3. Execute a bounded recovery workflow.
4. Show measured money recovered across a batch.
5. Use compliant escalation.
6. Apply explicit stopping rules.
7. Maintain a complete audit trail.
8. Handle at least one failure gracefully.

The final implementation must use **Razorpay test-mode APIs** for the money-related workflow where the selected recovery action requires a payment/test transaction operation.

No real customer money should be used.

---

# 3. Product Thesis

## Revenue Recovery Decision Engine

Treat each recovery opportunity as a **decision under uncertainty**.

Do not use a static policy such as:

```text
payment_failed → retry_after_1_hour
```

Instead:

```text
Current context
      ↓
Candidate recovery strategies
      ↓
Estimate expected recovery value
      ↓
Apply policy and safety constraints
      ↓
Select best allowed action
      ↓
Execute
      ↓
Observe outcome
      ↓
Update strategy statistics
```

The decision should consider:

- probability of recovery,
- recoverable amount,
- intervention cost,
- customer friction,
- action risk,
- retry history,
- timing,
- payment state,
- merchant context,
- historical outcomes.

---

# 4. Core Differentiator

A generic implementation looks like:

```text
Failed payment
     ↓
Retry
```

Our system asks:

```text
What failed?
Why did it fail?
Is the money actually recoverable?
How much is realistically recoverable?
Which action is most likely to succeed?
Is that action permitted?
Has the customer already received enough attempts?
What happened after the action?
Should we continue, change strategy, stop, or escalate?
```

The product should behave like a **revenue decision controller**, not a retry bot.

---

# 5. Product Scope

## 5.1 Primary Scope

The first competitive version should focus on a defined batch of synthetic merchant/payment events.

The initial supported recovery classes should be selected from:

### A. Failed payment recovery

```text
payment failure
→ diagnose cause
→ estimate recovery probability
→ choose intervention
→ test-mode action
→ observe outcome
```

### B. Checkout abandonment

```text
checkout initiated
→ no payment completion
→ estimate recoverability
→ bounded reminder / retry workflow
→ observe conversion
```

### C. Failed recurring payment

```text
subscription payment fails
→ identify failure context
→ choose retry/recovery strategy
→ bounded retry sequence
→ stop/escalate when appropriate
```

The final MVP does not need to support every possible revenue-loss category.

One complete workflow with strong evaluation is better than many incomplete workflows.

---

# 6. Recommended MVP Focus

The recommended initial focus is:

## Failed Payment Recovery

because it gives the cleanest measurable closed loop:

```text
Payment failed
     ↓
Revenue at risk identified
     ↓
Failure diagnosed
     ↓
Recovery candidates generated
     ↓
Expected recovery value calculated
     ↓
Policy gate
     ↓
Razorpay test-mode recovery action
     ↓
Payment state observed
     ↓
Recovered / retry / stop / escalate
```

After this is stable, add one secondary class such as checkout abandonment or recurring payment failure.

---

# 7. End-to-End Architecture

```text
                         MERCHANT / PAYMENT EVENTS
                                  |
                                  v
                         Event Ingestion Layer
                                  |
                                  v
                         Revenue Risk Detector
                                  |
                                  v
                       Revenue Opportunity Store
                                  |
                                  v
                     Context + Diagnosis Engine
                                  |
                 +----------------+----------------+
                 |                                 |
                 v                                 v
           Customer Context                  Payment Context
           Merchant Context                 Historical Outcomes
           Temporal Context                 Gateway / Failure State
                 |                                 |
                 +----------------+----------------+
                                  |
                                  v
                       Recovery Strategy Router
                                  |
                +-----------------+-------------------+
                |                 |                   |
                v                 v                   v
        Deterministic Path   AI Reasoning Path   Human Escalation
                |                 |                   |
                +-----------------+-------------------+
                                  |
                                  v
                       Candidate Strategy Set
                                  |
                                  v
                    Expected Recovery Value Engine
                                  |
                                  v
                         Policy / Safety Gate
                                  |
                                  v
                         Razorpay Test Action
                                  |
                                  v
                         Outcome Observation
                                  |
                +-----------------+------------------+
                |                 |                  |
                v                 v                  v
             RECOVERED       RETRY_ELIGIBLE       STOP/ESCALATE
                |                 |                  |
                +-----------------+------------------+
                                  |
                                  v
                         Outcome Measurement
                                  |
                                  v
                       Strategy Statistics / Learning
                                  |
                                  v
                           Audit + Dashboard
```

---

# 8. System Layers

## 8.1 Event Ingestion Layer

Responsible for receiving:

- payment events,
- checkout events,
- subscription events,
- invoice events,
- customer context,
- merchant context.

Every event must have:

```text
event_id
timestamp
merchant_id
customer_id
payment/order/subscription reference
amount
currency
event_type
payment_state
metadata
```

Events must be idempotently ingested.

---

# 9. Revenue-at-Risk Detection

The detector should identify which events represent meaningful recovery opportunities.

Potential outputs:

```text
revenue_at_risk
recoverability_probability
failure_class
time_since_failure
recovery_window
priority
```

The model can be ML/statistical/rule-based depending on the experiment.

The first version can use a combination of:

- failure type,
- historical success,
- amount,
- retry history,
- timing,
- customer response history,
- payment state.

Later phases can compare a baseline model with a learned estimator.

---

# 10. Revenue-at-Risk vs Recoverable Revenue

These are not the same.

### Revenue at risk

Amount that may be lost if the event is not recovered.

### Recoverable revenue

Amount the system reasonably expects to be recoverable through allowed interventions.

Example:

```text
Revenue at risk:       ₹5,000
Estimated recoverable: ₹3,200
```

The system must not assume that all revenue at risk is recoverable.

This distinction is important for honest evaluation.

---

# 11. Context and Diagnosis Engine

Before selecting an action, the system should determine why the revenue opportunity exists.

Possible context:

```text
Failure reason
Payment method
Gateway state
Previous attempts
Customer response history
Merchant history
Transaction amount
Time since failure
Recent payment behaviour
Similar historical cases
```

The AI layer can synthesize the context into structured diagnostic categories such as:

```text
TEMPORARY_PAYMENT_FAILURE
CUSTOMER_NON_RESPONSE
RETRY_EXHAUSTED
GATEWAY_DEGRADATION
AUTHORIZATION_REQUIRED
RECOVERY_WINDOW_EXPIRING
UNRECOVERABLE
UNKNOWN
```

The system must preserve the evidence supporting the diagnosis.

---

# 12. Recovery Strategies as Competing Policies

Do not define only one recovery action.

For a failed payment:

```text
Candidate A:
Retry immediately

Candidate B:
Retry after cooldown

Candidate C:
Send permitted reminder, then retry

Candidate D:
Escalate to human

Candidate E:
Stop
```

The system evaluates candidate actions using current context.

The goal is:

> **Choose the best allowed intervention for this case, not the same intervention for every case.**

---

# 13. Intelligent Recovery Router

The system should have an explicit recovery router.

```text
                    Recovery Router
                         |
          +--------------+---------------+
          |              |               |
          v              v               v
    Deterministic    AI Reasoning    Human Escalation
       Path              Path             Path
          |              |               |
          +--------------+---------------+
                         |
                         v
                    Policy Gate
                         |
                         v
                      Execute
```

## Routing principles

1. Use deterministic logic when it is sufficient.
2. Escalate ambiguous or high-value cases.
3. Never allow AI reasoning to bypass policy.
4. Record why the route was selected.
5. Measure whether the selected route worked.

The agent should not be called for every event.

---

# 14. Complexity and Ambiguity Routing

A lightweight router can classify cases:

```text
LOW COMPLEXITY
     ↓
Deterministic recovery policy

MEDIUM COMPLEXITY
     ↓
Structured ML/statistical strategy ranking

HIGH COMPLEXITY
     ↓
AI reasoning + evidence aggregation

HIGH IMPACT / HIGH UNCERTAINTY
     ↓
Human escalation
```

This improves:

- cost,
- latency,
- predictability,
- auditability,
- safety.

---

# 15. Expected Recovery Value

A key decision score is:

```text
ERV(action)
=
P(recovery | context, action)
× recoverable_amount
− action_cost
− friction_penalty
− risk_penalty
```

Example:

| Action | Recovery probability | Recoverable amount | Approx. value |
|---|---:|---:|---:|
| Retry now | 0.30 | ₹4,500 | ₹1,350 minus costs |
| Retry later | 0.46 | ₹4,500 | ₹2,070 minus costs |
| Reminder + retry | 0.62 | ₹4,500 | ₹2,790 minus costs |
| Human escalation | 0.55 | ₹4,500 | lower net value due to higher cost |

These values are illustrative.

The actual system must calculate them from measured or explicitly modelled data.

---

# 16. Economic Decision Objective

The system should optimize:

```text
maximize:
expected recovered revenue

while minimizing:
unnecessary interventions
customer friction
action cost
policy risk
duplicate actions
```

The system should not maximize the number of retries.

It should maximize **net useful recovery**.

---

# 17. Policy and Safety Layer

This layer is mandatory.

The AI cannot directly control unrestricted payment actions.

Every money-related action must pass a policy gate.

Example:

```text
Agent proposes:
RETRY_PAYMENT

             ↓

Policy Gate

retry_count < limit            ✓
payment still recoverable      ✓
cooldown satisfied             ✓
amount within automation limit ✓
customer not opted out        ✓
payment state valid            ✓
idempotency validated          ✓
recovery window active         ✓

             ↓

EXECUTE
```

Mandatory controls include:

- maximum retry count,
- maximum automated amount,
- minimum time between attempts,
- customer opt-out/stop condition,
- action-specific eligibility,
- duplicate-action protection,
- payment-state validation,
- idempotency validation,
- escalation threshold,
- recovery-window expiry,
- merchant-level configuration.

---

# 18. Stopping Rules

Stopping rules are first-class product logic.

Examples:

```text
STOP if:
- retry limit reached
- customer opted out
- recovery probability below threshold
- recovery window expired
- expected recovery value falls below action cost
- payment state becomes non-recoverable
- repeated intervention failure occurs
- policy condition fails
```

The system must prefer:

```text
STOP
```

over endless automation.

---

# 19. Human Escalation

Human intervention should be explicit.

Escalate when:

- expected value is high but confidence is low,
- multiple strategies have similar expected value,
- recovery actions are exhausted,
- policy requires approval,
- customer dispute exists,
- payment state is ambiguous,
- automated action is outside configured limits.

Example:

```text
Revenue at risk: ₹45,000
Confidence: 0.51

Decision:
HUMAN_REVIEW_REQUIRED

Reason:
Two recovery strategies have statistically similar
expected value and the amount exceeds the
automatic execution threshold.
```

---

# 20. Deterministic vs AI Responsibilities

## ML / Statistical Layer

Potential responsibilities:

- revenue-at-risk probability,
- recoverability probability,
- failure-type classification,
- customer response probability,
- time-to-recovery estimation,
- intervention ranking.

## AI Agent Layer

Potential responsibilities:

- root-cause synthesis,
- context aggregation,
- strategy selection among allowed actions,
- exception handling,
- explanation generation,
- escalation reasoning.

## Deterministic Layer

Must own:

- amount limits,
- retry limits,
- idempotency,
- payment-state validation,
- stopping rules,
- policy enforcement,
- authorization,
- audit records.

The LLM should reason **inside the system**.

It must not become the source of truth for payment state or financial permissions.

---

# 21. Razorpay Test-Mode Integration

The payment execution layer should use Razorpay's test environment only.

The system should support the relevant test-mode operations required for the selected recovery scenario.

Potential flow:

```text
Recovery Decision
      ↓
Policy Gate
      ↓
Prepare test-mode action
      ↓
Idempotency / state validation
      ↓
Razorpay test action
      ↓
Capture request/result reference
      ↓
Observe payment state
      ↓
Recovery outcome
```

No real-money execution.

All test credentials must be supplied through environment variables.

Never hard-code credentials.

---

# 22. Payment State Machine

Recovery must be driven by explicit state.

Example:

```text
AT_RISK
   ↓
DIAGNOSED
   ↓
ACTION_SELECTED
   ↓
POLICY_APPROVED
   ↓
ACTION_EXECUTED
   ↓
OUTCOME_OBSERVED
   |
   +--> RECOVERED
   |
   +--> RETRY_ELIGIBLE
   |
   +--> ESCALATE
   |
   +--> STOPPED
   |
   +--> EXECUTION_FAILED
```

Every state transition must be auditable.

---

# 23. Idempotency and Duplicate Protection

Money-related workflows must be idempotent.

Every recovery action needs a stable idempotency identity.

Example:

```text
merchant_id
customer_id
payment_id
action_type
attempt_number
```

The same recovery action must not accidentally execute twice due to:

- duplicate events,
- retries,
- timeouts,
- callback duplication,
- agent retries,
- race conditions.

The system should record:

```text
idempotency_key
action_status
request_reference
result_reference
```

---

# 24. Graceful Failure Handling

At least one failure path must be demonstrated.

Recommended example:

```text
Agent selects:
RETRY_PAYMENT

        ↓

Razorpay test-mode request times out

        ↓

Execution state:
RECOVERY_EXECUTION_FAILED

        ↓

Confirm payment state before retrying

        ↓

If state is unknown:
DO NOT duplicate action

        ↓

Defer / reconcile / escalate
```

Structured failure example:

```json
{
  "status": "RECOVERY_EXECUTION_FAILED",
  "action": "RETRY_PAYMENT",
  "reason": "UPSTREAM_TIMEOUT",
  "next_action": "RECONCILE_PAYMENT_STATE",
  "attempt": 2,
  "idempotency_protected": true
}
```

The system must never hide a failure by emitting a fake success response.

---

# 25. Audit Trail

Every money-related action must be explainable.

Each audit event should include:

```text
workflow_id
merchant_id
customer_id
revenue_at_risk
recoverable_amount_estimate
failure_reason
context_snapshot_reference
candidate_actions
selected_action
selection_reason
policy_checks
authorization_state
action_time
Razorpay request/reference
outcome
recovered_amount
next_state
```

Example human-readable explanation:

> Recovery decision: delay retry by 30 minutes because the selected failure class has a higher historical recovery rate after cooldown, the customer has previously recovered successfully after delayed retries, and the configured retry budget permits one additional attempt.

The human explanation must be backed by the structured decision record.

---

# 26. Outcome Observation

After every action, observe the actual result.

Examples:

```text
PAYMENT_SUCCESS
PAYMENT_FAILED
PAYMENT_PENDING
NO_RESPONSE
CUSTOMER_COMPLETED
ACTION_REJECTED
UNKNOWN_PAYMENT_STATE
```

Never infer recovery solely from the agent's response.

---

# 27. Closed-Loop Learning

The learning loop is:

```text
Observe
   ↓
Estimate
   ↓
Act
   ↓
Measure outcome
   ↓
Compare expected vs actual recovery
   ↓
Update strategy statistics
   ↓
Next decision
```

The system can maintain strategy performance such as:

```text
failure_type
customer_segment
payment_method
action
attempt_number
success_rate
average_recovered_amount
observed_cost
```

The learning objective is:

> **Increase expected recovered revenue while reducing unnecessary interventions.**

Do not implement unrestricted recursive self-modification.

The adaptation should be controlled strategy selection based on observed outcomes.

---

# 28. Optional Self-Evaluation / Reward Signal

This concept may be included only if it improves measurable recovery performance.

A safe form:

```text
Predicted recovery value
        ↓
Actual recovery outcome
        ↓
Reward / penalty
        ↓
Update strategy statistics
```

This is preferable to:

```text
LLM judges itself
        ↓
LLM says it did well
        ↓
Trust the reward
```

For financial actions:

- external outcome is authoritative,
- payment state is authoritative,
- policy engine is authoritative,
- benchmark evaluator is authoritative.

Self-evaluation must never authorize money movement.

---

# 29. Revenue Recovery Index

The system may expose a merchant-facing operational signal:

```text
REVENUE RECOVERY INDEX

Today                 71.0
7-day average         58.2
Revenue at risk       ₹12.4L
Expected recovery     ₹8.1L
Recovered today       ₹2.7L
```

Possible underlying signals:

- failed-payment rate,
- estimated recoverability,
- recovery probability,
- intervention success,
- recovery rate,
- customer response,
- recovered revenue.

The index is valid only if its components are measurable and it helps drive decisions.

It must not become a vanity metric.

---

# 30. Batch Evaluation

The hackathon submission must demonstrate performance across a batch.

Recommended benchmark shape:

```text
1,000 synthetic revenue events
```

Containing multiple loss types, for example:

```text
failed payments
checkout abandonments
recurring-payment failures
```

The exact distribution should be documented.

The benchmark should include:

- recoverable cases,
- non-recoverable cases,
- ambiguous cases,
- policy-stopped cases,
- execution failures,
- cases requiring escalation.

Do not cherry-pick only easy cases.

---

# 31. Evaluation Harness

The evaluation harness must be designed before tuning the agent.

## Detection Metrics

- revenue-at-risk precision,
- revenue-at-risk recall,
- false-positive rate,
- missed-recovery rate.

## Decision Metrics

- intervention success rate,
- wrong-intervention rate,
- unnecessary-intervention rate,
- stopping-rule compliance,
- escalation appropriateness.

## Business Metrics

- total revenue at risk,
- estimated recoverable revenue,
- total recovered revenue,
- recovery rate,
- average recovered amount per intervention,
- cost per recovered rupee,
- net recovery value.

## Reliability Metrics

- duplicate-action rate,
- policy-violation rate,
- execution failure rate,
- graceful-failure rate,
- audit completeness,
- payment-state reconciliation accuracy.

---

# 32. Baselines

The final system should be compared against meaningful baselines.

### Baseline A — Fixed Retry

```text
payment failed
→ retry after fixed interval
```

### Baseline B — Rule-Based Recovery

```text
failure_type
→ predefined recovery strategy
```

### Baseline C — ML Ranking Without Agentic Diagnosis

```text
context
→ strategy score
→ best fixed strategy
```

### Proposed System

```text
detect
→ diagnose
→ generate candidates
→ expected recovery value
→ policy gate
→ execute
→ observe
→ learn/stop/escalate
```

This lets us establish whether the additional agentic decision layer actually creates measurable value.

---

# 33. Ablation Study

Run controlled ablations.

Compare:

```text
Full system

Full - dynamic strategy routing

Full - AI diagnosis

Full - outcome learning

Full - policy-aware expected value

Full - historical outcome context
```

Measure:

- recovered revenue,
- intervention success,
- unnecessary intervention,
- cost per recovered rupee,
- policy violations,
- recovery latency.

This establishes which components actually matter.

---

# 34. Fixed-Budget Experiments

The system should be evaluated under controlled budgets.

Examples:

```text
Maximum interventions/customer
Maximum agent calls/case
Maximum LLM tokens/case
Maximum recovery window
Maximum automated amount
```

Compared systems must operate under equivalent budgets.

This prevents the proposed system from winning simply by spending more compute or attempting more interventions.

---

# 35. Honest Business Accounting

Do not equate:

```text
successful payment
=
AI-created revenue
```

The evaluation should distinguish:

### Revenue at risk

Potentially lost.

### Recoverable revenue

Revenue for which the benchmark says a valid recovery path existed.

### Recovered revenue

Revenue actually recovered after an intervention.

### Incremental recovery

Recovery attributable to the intervention relative to the baseline.

The strongest business metric is:

> **Incremental recovered revenue over baseline.**

---

# 36. Counterfactual / Control Evaluation

Where feasible, use a control comparison.

Example:

```text
Control:
fixed rule-based recovery

Treatment:
Recovery Decision Engine
```

Compare:

```text
Recovery rate
Recovered revenue
Intervention count
Customer friction
Cost
```

This prevents the system from claiming credit for payments that would have happened anyway.

---

# 37. Synthetic Data Requirements

The data should include meaningful causal relationships.

Avoid a dataset where:

```text
failure_code = FRAUD
```

or another single field trivially identifies the correct action.

Use realistic combinations such as:

```text
failure reason
amount
merchant
customer behaviour
payment method
retry history
time
gateway state
response history
```

Include noise and ambiguous cases.

Document all synthetic generation assumptions.

---

# 38. Merchant-Level Context

Recovery actions can depend on merchant behaviour.

Possible merchant features:

```text
merchant size
average transaction value
historical recovery rate
payment method mix
failure distribution
retry tolerance
business hours
recovery performance
```

The system should not assume every merchant has the same optimal policy.

---

# 39. Customer-Level Context

Potential context:

```text
historical successful payments
failure frequency
response to reminders
average transaction amount
recent attempts
preferred payment method
time-of-day behaviour
customer opt-out
```

Use context only where justified by the benchmark and policy.

Avoid unnecessary sensitive attributes.

---

# 40. Payment-Route Context

The system may use payment infrastructure context such as:

```text
payment method
gateway state
failure code
latency
recent success rate
temporary degradation signal
```

This helps distinguish:

```text
"retry now"
```

from:

```text
"wait until the payment route recovers"
```

---

# 41. Strategy Statistics

Maintain strategy performance by relevant context.

Example:

```text
Strategy:
DELAYED_RETRY

Failure class:
TEMPORARY_BANK_FAILURE

Attempt number:
1

Historical samples:
N

Observed recovery rate:
X%

Average recovered amount:
₹Y
```

Do not expose fabricated historical probabilities.

All strategy statistics must come from benchmark or simulated outcomes.

---

# 42. Frontend

The UI should focus on revenue decisions, not generic AI chat.

## Merchant Overview

Show:

```text
Revenue at risk
Expected recoverable
Recovered revenue
Recovery rate
Active cases
Escalations
Stopped cases
Failed actions
```

## Recovery Queue

Each case:

```text
case_id
revenue_at_risk
recoverable_amount
failure_reason
current_state
recommended_action
expected_recovery_value
policy_status
```

## Decision View

Show:

```text
Context
Diagnosis
Candidate strategies
Expected values
Selected strategy
Policy checks
Action
Outcome
Recovered amount
```

## Audit View

Show the complete state-transition history.

---

# 43. Example Decision View

```text
CASE: RR-1042

Revenue at risk:
₹4,500

Estimated recoverable:
₹3,200

Failure:
Temporary upstream failure

Candidate actions:

A. Retry now
   Expected value: ₹1,050

B. Retry after 30 min
   Expected value: ₹1,620

C. Reminder + retry
   Expected value: ₹2,040

D. Human escalation
   Expected value: ₹1,400

Selected:
C. Reminder + retry

Policy:
PASS

Authorization:
PASS

Action:
EXECUTED

Outcome:
PAYMENT_SUCCESS

Recovered:
₹4,500

Final state:
RECOVERED
```

The displayed explanation must originate from structured decision data.

---

# 44. Failure Scenarios

At minimum test:

## Failure 1 — Payment API timeout

Expected:

```text
do not duplicate
→ reconcile state
→ defer/retry/escalate
```

## Failure 2 — Payment state unknown

Expected:

```text
do not attempt a second money action
→ reconcile
```

## Failure 3 — Retry limit reached

Expected:

```text
STOP
```

## Failure 4 — Customer opts out

Expected:

```text
STOP
```

## Failure 5 — Expected recovery value falls below cost

Expected:

```text
STOP
```

## Failure 6 — AI unavailable

Expected:

```text
fall back to deterministic policy
```

or:

```text
escalate
```

depending on the case.

---

# 45. Security and Safety

The system must be defensive and revenue-recovery oriented.

Do not implement anything intended to:

- exploit payment systems,
- bypass payment authorization,
- manipulate financial state,
- evade safeguards,
- perform offensive security activity.

Protect:

- API keys,
- test credentials,
- customer identifiers,
- transaction references,
- payment metadata.

Use environment variables and secure logging.

---

# 46. Technology Stack

## Backend

- Python
- FastAPI
- PostgreSQL
- Redis where useful

## Event Processing

- Kafka where required for realistic event-driven processing
- otherwise a simpler queue is acceptable for the MVP if the evaluation remains valid

## ML / Statistical Layer

- Python
- scikit-learn
- XGBoost where useful
- Pandas / NumPy

## Agent Layer

- LangGraph or equivalent stateful orchestration
- structured tool calling
- permitted LLM provider

## Payments

- Razorpay test-mode APIs

## Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS

## Observability

- Prometheus
- structured logs
- Grafana optional

## Evaluation

- Pytest
- custom benchmark harness
- reproducible synthetic dataset
- baseline runners
- ablation runners

## Containers

- Docker Compose initially

Keep the stack intentionally minimal.

---

# 47. Proposed Repository Structure

```text
ai-revenue-recovery/
│
├── agent/
│   ├── diagnosis/
│   ├── router/
│   ├── strategy/
│   ├── explanation/
│   └── state/
│
├── models/
│   ├── revenue_risk/
│   ├── recoverability/
│   └── intervention/
│
├── recovery/
│   ├── policies/
│   ├── actions/
│   ├── state_machine/
│   ├── idempotency/
│   └── verification/
│
├── integrations/
│   └── razorpay/
│
├── ingestion/
│   ├── events/
│   └── generators/
│
├── database/
│   ├── migrations/
│   └── seeds/
│
├── benchmark/
│   ├── datasets/
│   ├── scenarios/
│   ├── baselines/
│   ├── evaluators/
│   ├── ablations/
│   └── reports/
│
├── backend/
│   ├── api/
│   ├── cases/
│   ├── merchants/
│   ├── audit/
│   └── metrics/
│
├── frontend/
│   ├── dashboard/
│   ├── recovery-queue/
│   ├── decision-view/
│   └── audit/
│
├── observability/
│   ├── prometheus/
│   └── grafana/
│
├── docs/
│   ├── README.md
│   ├── PHASES.md
│   ├── architecture.md
│   ├── evaluation.md
│   ├── safety.md
│   └── decisions.md
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

# 48. Implementation Phase Alignment

The detailed implementation plan will be maintained separately, but this README is intentionally structured so the phase plan maps directly to the product architecture.

The planned execution sequence is:

```text
Phase 0  → Repository + product contract + evaluation contract
Phase 1  → Event/data model + synthetic dataset
Phase 2  → Revenue-at-risk detection
Phase 3  → Context + diagnosis engine
Phase 4  → Recovery strategies + router
Phase 5  → Expected Recovery Value engine
Phase 6  → Policy + stopping + escalation
Phase 7  → Razorpay test-mode execution
Phase 8  → State machine + idempotency + audit
Phase 9  → Outcome observation + recovery verification
Phase 10 → Closed-loop strategy learning
Phase 11 → Benchmark + baselines
Phase 12 → Ablation + fixed-budget experiments
Phase 13 → Merchant recovery dashboard
Phase 14 → Failure/security/reliability testing
Phase 15 → Final batch evaluation
Phase 16 → Final demo + documentation + release
```

The later phase document must preserve this product architecture unless a measured implementation constraint requires a documented change.

---

# 49. Phase Discipline

For every phase:

```text
Read phase requirements
        ↓
Inspect current repository state
        ↓
Implement only phase scope
        ↓
Write tests
        ↓
Run tests
        ↓
Verify exit criteria
        ↓
Update documentation
        ↓
Review diff
        ↓
Focused Git commit
        ↓
Only then start next phase
```

Every phase must end with:

- implementation,
- tests,
- verification,
- documentation,
- focused Git commit.

Never use:

```bash
git add .
git add -A
```

Stage exact files only.

---

# 50. Code Quality Contract

The implementation must be professional and production-oriented.

## General

- small modules,
- explicit interfaces,
- type safety,
- structured errors,
- testable components,
- minimal duplication,
- deterministic financial control logic.

## Python

Use:

- type hints,
- Pydantic/dataclasses,
- pytest,
- structured logging,
- explicit exceptions.

Avoid:

- wildcard imports,
- print() for application logging,
- hidden global state,
- swallowed exceptions,
- magic constants.

## Agent

Do not create one giant prompt.

Use explicit state for:

```text
recovery case
context
diagnosis
candidate actions
expected values
policy result
selected action
execution result
outcome
next state
```

## Comments

**No emojis anywhere in code or code-adjacent technical content.**

No emoji in:

- comments,
- docstrings,
- identifiers,
- log messages,
- commit messages.

Comments should explain why a non-obvious decision exists.

---

# 51. Financial Correctness Contract

The LLM is never the source of truth for:

- payment state,
- authorization,
- amount,
- retry count,
- idempotency,
- stopping rules,
- audit records.

Those are deterministic system responsibilities.

The AI may recommend:

```text
RETRY_LATER
SEND_PERMITTED_REMINDER
ESCALATE
STOP
```

The policy layer decides whether that recommendation is allowed.

The execution layer performs the validated action.

The outcome layer verifies what actually happened.

---

# 52. Data Integrity

Every recovery case must have a stable identity.

Suggested:

```text
recovery_case_id
merchant_id
customer_id
payment_id / order_id / subscription_id
```

Use timestamps and immutable event IDs.

Do not overwrite historical financial events.

State transitions should append audit events rather than mutate history invisibly.

---

# 53. Honest Measurement Rules

Never claim:

```text
₹X recovered
```

unless the benchmark proves that amount was actually recovered.

Never claim:

```text
AI increased recovery by X%
```

unless compared against a defined baseline/control.

Never claim:

```text
AI prevented X loss
```

unless the evaluation has a defensible counterfactual.

Placeholder outputs must be clearly labelled as examples.

---

# 54. Final Benchmark Output

The final benchmark should resemble:

```text
===========================================================
AI REVENUE RECOVERY EVALUATION
===========================================================

Cases evaluated:                    N

Revenue at risk:                    ₹X
Estimated recoverable revenue:      ₹X
Recovered revenue:                  ₹X
Incremental recovery vs baseline:  ₹X

-----------------------------------------------------------

Recovery rate:                      X%
Successful interventions:           X
Unnecessary interventions:          X
Escalated cases:                    X
Stopped by policy:                  X
Execution failures:                 X

-----------------------------------------------------------

Duplicate actions:                  0
Policy violations:                  0
Audit completeness:                 100%

===========================================================
```

All numbers must be generated from the final benchmark.

---

# 55. Core Demo Story

The final demo should follow one complete case and then show the batch results.

## Case

```text
Payment failed
      ↓
₹4,500 revenue at risk
      ↓
System diagnoses temporary failure
      ↓
Evaluates recovery strategies
      ↓
Reminder + delayed retry has highest expected value
      ↓
Policy passes
      ↓
Razorpay test action executes
      ↓
Payment succeeds
      ↓
₹4,500 recovered
      ↓
Audit recorded
```

Then demonstrate a failure:

```text
Recovery action times out
      ↓
Payment state becomes uncertain
      ↓
System does NOT duplicate the action
      ↓
State reconciliation
      ↓
Defer / retry / escalate
      ↓
Audit records failure
```

Finally show:

```text
1,000 cases
₹X at risk
₹Y recoverable
₹Z recovered
X% recovery rate
0 duplicate actions
0 policy violations
100% audit coverage
```

The actual values must come from the final benchmark.

---

# 56. What We Are Explicitly NOT Building

This project is not:

- a generic chatbot,
- a fixed payment retry script,
- an LLM that directly controls payments,
- an unrestricted autonomous spending system,
- a dashboard that only predicts revenue loss,
- an SMS/email bot with no recovery measurement,
- an artificial demo with no real test-mode payment workflow,
- a system evaluated on cherry-picked examples,
- a system that maximizes retries,
- a system that fabricates recovered revenue.

The system must close the loop from:

**detection → diagnosis → decision → action → outcome → measurement.**

---

# 57. Success Criteria

The project is successful only if it can demonstrate:

### Product

- real recovery workflow,
- real Razorpay test-mode interaction,
- bounded actions,
- policy gates,
- stopping rules,
- human escalation,
- graceful failure,
- complete audit trail.

### AI

- meaningful diagnosis,
- context-aware strategy selection,
- expected-value-based action selection,
- outcome-aware strategy improvement.

### Measurement

- batch evaluation,
- baseline comparison,
- actual recovered revenue,
- incremental recovery,
- intervention quality,
- reliability metrics.

### Engineering

- idempotency,
- deterministic payment control,
- reproducibility,
- observable state transitions,
- clean architecture,
- automated tests.

---

# 58. Final Product Definition

## Working Name

**AI Revenue Recovery Decision Engine**

## One-line description

> **An evidence-backed AI decision engine that finds revenue at risk, diagnoses why it is slipping away, dynamically selects the highest-value permitted recovery intervention, executes it safely through Razorpay test-mode workflows, and proves the money actually recovered.**

## Core differentiator

Normal recovery system:

> "Payment failed. Retry."

This system:

> **"₹X is at risk because of Y. Given the current context, strategy Z has the highest expected recovery value within policy. Execute it, observe the payment state, stop or escalate when required, and report the actual recovered revenue."**

## Technical differentiator

```text
Revenue-at-risk detection
+
Contextual diagnosis
+
Dynamic recovery routing
+
Competing intervention policies
+
Expected Recovery Value
+
Policy-gated execution
+
Idempotency
+
Stopping rules
+
Outcome-based strategy learning
+
Batch-level measurable recovery
+
Complete auditability
```

---

# 59. Final Architecture Principle

```text
FIND REVENUE AT RISK
        ↓
UNDERSTAND WHY
        ↓
ESTIMATE RECOVERABILITY
        ↓
GENERATE CANDIDATE ACTIONS
        ↓
CHOOSE BY EXPECTED RECOVERY VALUE
        ↓
APPLY POLICY + SAFETY GATES
        ↓
EXECUTE BOUNDED ACTION
        ↓
OBSERVE ACTUAL PAYMENT OUTCOME
        ↓
RECOVER / RETRY / STOP / ESCALATE
        ↓
MEASURE ₹ RECOVERED
        ↓
UPDATE STRATEGY STATISTICS
```

The system should always answer four questions:

> **How much money was at risk?**

> **Why was it at risk?**

> **Why did we choose this intervention?**

> **How much money did we actually recover?**
