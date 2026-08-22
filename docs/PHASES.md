# AI Revenue Recovery Decision Engine
## Hackathon Implementation Plan — Phase-by-Phase

> **Project:** AI Revenue Recovery Decision Engine
>
> **Track:** Razorpay Track 03 — AI Revenue Recovery
>
> **Purpose:** Build an AI system that identifies revenue at risk, diagnoses why it is slipping away, chooses among bounded recovery interventions using expected recovery value, executes permitted Razorpay test-mode actions, observes the actual outcome, and learns from measured recovery results.
>
> **Source of truth:** This document is the implementation plan. The product/architecture contract is defined in the project README. The phase plan must remain aligned with that product contract.
>
> **Critical Git rule:** Every completed phase must be tested, verified, documented, and committed. **Never use `git add .` or `git add -A`.**

---

# 0. Project Scope in Short

The system is not:

```text
payment_failed → retry
```

It is:

```text
Revenue Event
      ↓
Revenue-at-Risk Detection
      ↓
Context + Diagnosis
      ↓
Candidate Recovery Strategies
      ↓
Expected Recovery Value
      ↓
Policy / Safety Gate
      ↓
Bounded Action
      ↓
Outcome Observation
      ↓
Recovered / Retry / Stop / Escalate
      ↓
Measure Actual Recovery
      ↓
Update Strategy Statistics
```

The core product is a **closed-loop revenue recovery decision engine**.

The primary business outcome is:

> **Incremental recovered revenue over a defensible baseline.**

The primary engineering outcome is:

> **Safe, auditable, idempotent and policy-bounded financial workflow execution.**

---

# 1. Non-Negotiable Product Principles

## 1.1 Revenue outcome comes first

Do not optimize for:

- number of agent calls,
- number of retries,
- number of automated actions,
- model complexity.

Optimize for:

```text
useful recovered revenue
− unnecessary action cost
− customer friction
− policy/risk cost
```

## 1.2 Revenue at risk is not recovered revenue

Always distinguish:

```text
Revenue at risk
Recoverable revenue
Actual recovered revenue
Incremental recovered revenue
```

## 1.3 Start with a deterministic baseline

The AI system must have something measurable to beat.

Build fixed recovery rules before introducing advanced AI.

## 1.4 AI does not own financial truth

The LLM must never become the source of truth for:

- payment state,
- amount,
- authorization,
- retry count,
- idempotency,
- stopping rules,
- audit records.

Those belong to deterministic system components.

## 1.5 Every money action is gated

The agent can recommend an action.

The policy layer decides whether that action is allowed.

The execution layer performs only validated actions.

## 1.6 Every action has an observable outcome

Do not count an action as successful because the agent returned a success message.

Measure the resulting payment/recovery state.

## 1.7 Stop is a valid decision

The system must be willing to say:

```text
STOP
```

when further intervention is not justified.

## 1.8 Escalation is a valid decision

The system must support:

```text
HUMAN_REVIEW_REQUIRED
```

for ambiguous, high-value, high-risk, or policy-restricted cases.

## 1.9 No fabricated business metrics

No recovery number, recovery rate, model score or uplift may be claimed until measured by the benchmark.

---

# 2. Technology Baseline

Use the stack defined by the product specification unless implementation evidence requires a documented change.

## Backend

- Python
- FastAPI
- PostgreSQL
- Redis where genuinely useful

## Event Processing

- Kafka or equivalent event layer where justified

## ML / Statistical

- scikit-learn
- XGBoost where useful
- Pandas
- NumPy

## Agent

- LangGraph or equivalent stateful workflow orchestration
- structured tool calling
- permitted LLM provider

## Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS
- Recharts or equivalent

## Payments

- Razorpay test-mode APIs only

## Testing / Evaluation

- pytest
- custom benchmark harness
- baseline runners
- ablation runners

## Containers

- Docker Compose initially

Do not add infrastructure simply for appearance.

---

# 3. Repository Contract

The final implementation should roughly follow:

```text
revenue-recovery-agent/
├── backend/
│   ├── api/
│   ├── domain/
│   ├── recovery/
│   │   ├── detection/
│   │   ├── diagnosis/
│   │   ├── ranking/
│   │   ├── policies/
│   │   ├── routing/
│   │   └── execution/
│   ├── agents/
│   ├── models/
│   ├── state_machine/
│   ├── audit/
│   └── storage/
├── frontend/
├── datasets/
│   ├── train/
│   ├── validation/
│   └── test/
├── evaluation/
│   ├── metrics/
│   ├── baselines/
│   ├── experiments/
│   └── reports/
├── scripts/
├── docs/
│   ├── README.md
│   ├── PHASES.md
│   ├── architecture.md
│   ├── policies.md
│   ├── evaluation.md
│   └── decisions.md
├── tests/
├── docker-compose.yml
└── README.md
```

The actual structure may evolve, but changes must preserve the logical separation between:

```text
detection
diagnosis
strategy selection
policy
execution
state
audit
evaluation
```

---

# 4. High-Level Phase Map

```text
Phase 0  → Repository + economic/research contract
Phase 1  → Synthetic revenue dataset + ground truth
Phase 2  → Deterministic baseline recovery system
Phase 3  → Revenue-at-risk ML/statistical layer
Phase 4  → Dynamic recovery router + competing strategies
Phase 5  → AI investigation agent
Phase 6  → Expected Recovery Value engine
Phase 7  → Policy gate + stopping rules + escalation
Phase 8  → Razorpay test-mode execution
Phase 9  → State machine + idempotency + audit
Phase 10 → Outcome observation + recovery verification
Phase 11 → Closed-loop outcome learning
Phase 12 → Benchmark harness + baselines
Phase 13 → Ablation + fixed-budget experiments
Phase 14 → Merchant recovery dashboard
Phase 15 → Reliability, security + failure testing
Phase 16 → Final held-out evaluation + demo + release
```

Do not move forward simply because the code runs. Use the phase exit criteria.

---

# PHASE 0 — Repository, Economic Objective, and Architecture Contract

## Objective

Initialize a reproducible project and define exactly what "recovery" means before implementing the intelligence layer.

## Tasks

### Repository

Create or validate:

```text
README.md
docs/README.md
docs/PHASES.md
docs/architecture.md
docs/policies.md
docs/evaluation.md
docs/decisions.md
.env.example
.gitignore
```

### Define Economic Terms

Formalize:

```text
revenue_at_risk
recoverable_revenue
actual_recovered_revenue
incremental_recovered_revenue
intervention_cost
friction_penalty
risk_penalty
```

### Define Success Metrics

At minimum:

```text
revenue-at-risk precision
revenue-at-risk recall
recovery rate
incremental recovered revenue
average recovered amount
cost per recovered rupee
wrong intervention rate
unnecessary intervention rate
policy violations
duplicate actions
audit completeness
```

### Architecture

Document:

```text
Ingestion
→ Detection
→ Diagnosis
→ Strategy Selection
→ ERV
→ Policy
→ Execution
→ Outcome
→ Learning
→ Audit
```

## Testing

Verify:

- Python environment
- project installation
- test runner
- Docker Compose validation
- documentation structure

## Exit Criteria

The project can be cloned and understood without implementation ambiguity.

## Git Commit

Before staging:

```bash
git status
git diff
git diff --check
```

Stage only phase files:

```bash
git add README.md docs/ .env.example .gitignore pyproject.toml
```

Commit:

```bash
git commit -m "feat: initialize revenue recovery architecture"
```

---

# PHASE 1 — Synthetic Revenue Dataset and Ground Truth

## Objective

Create a realistic, reproducible merchant/payment dataset with hidden ground truth.

## Supported Event Classes

Start with:

```text
failed_payment
checkout_abandonment
recurring_payment_failure
```

Add more only if they materially improve the benchmark.

## Required Features

Each event should contain appropriate fields such as:

```text
event_id
timestamp
merchant_id
customer_id
payment/order/subscription_id
amount
currency
payment_method
failure_reason
payment_state
retry_count
time_since_failure
customer_history
merchant_context
gateway/payment-route context
prior recovery outcomes
```

## Ground Truth

Every synthetic case should define:

```text
true_revenue_at_risk
true_recoverable_amount
true_recovery_outcome
allowed_actions
optimal_or_reference_strategy
policy_constraints
```

Ground truth must remain inaccessible to the production agent.

## Dataset Splits

Strictly separate:

```text
datasets/train/
datasets/validation/
datasets/test/
```

The test set must remain untouched until final evaluation.

## Scenarios

Include:

- easily recoverable cases,
- ambiguous cases,
- low-value cases,
- non-recoverable cases,
- policy-stopped cases,
- failed action cases,
- cases requiring escalation.

## Testing

- schema validation
- deterministic generation with fixed seed
- no test leakage
- ground-truth integrity
- class distribution checks

## Exit Criteria

A full synthetic batch can be generated reproducibly and independently evaluated.

## Git Commit

```bash
git status
git diff
git diff --check
git add datasets/ scripts/ tests/ docs/
git commit -m "feat: add synthetic revenue recovery dataset"
```

---

# PHASE 2 — Deterministic Baseline Recovery System

## Objective

Build the simplest defensible recovery system before AI.

This is the baseline that the final system must beat.

## Baseline Policies

Implement:

```text
fixed retry
cooldown
simple escalation
stop conditions
```

Example:

```text
temporary failure
→ retry after fixed delay

retry limit reached
→ stop

high-value ambiguous case
→ escalate
```

## State

At minimum:

```text
AT_RISK
DIAGNOSED
ACTION_SELECTED
POLICY_APPROVED
ACTION_EXECUTED
OUTCOME_OBSERVED
RECOVERED
RETRY_ELIGIBLE
ESCALATE
STOPPED
```

## Metrics

Run the baseline over the validation set.

Record:

```text
recovery rate
recovered revenue
intervention count
unnecessary intervention
stopped cases
```

## Exit Criteria

There is a functioning baseline with reproducible metrics.

## Git Commit

```bash
git status
git diff
git diff --check
git add backend/recovery/ backend/state_machine/ tests/ evaluation/baselines/ docs/
git commit -m "feat: add deterministic recovery baseline"
```

---

# PHASE 3 — Revenue-at-Risk ML / Statistical Layer

## Objective

Estimate whether a revenue event is worth pursuing and how much recovery is plausible.

## Model Outputs

Potentially:

```text
P(recovery)
expected_recoverable_amount
failure_class
time_to_recovery
```

## Features

Use only appropriate features from the dataset:

- failure reason
- amount
- payment method
- retry history
- time since failure
- customer history
- merchant history
- recent payment-route health
- historical strategy outcomes

## Model Baselines

Compare simple approaches before using complex models:

```text
rule-based probability
logistic regression
tree-based model / XGBoost
```

Choose based on measured validation performance, not complexity.

## Evaluation

Measure:

- precision
- recall
- calibration where appropriate
- expected monetary error
- recoverability estimation error

## Important

Do not use the held-out test set for tuning.

## Exit Criteria

A validated risk/recoverability layer exists with reproducible validation metrics.

## Git Commit

```bash
git status
git diff
git diff --check
git add backend/models/ backend/recovery/detection/ evaluation/ tests/
git commit -m "feat: add revenue risk estimation layer"
```

---

# PHASE 4 — Dynamic Recovery Router and Competing Strategies

## Objective

Replace one universal recovery action with context-aware strategy selection.

## Candidate Strategies

Implement a controlled set such as:

```text
RETRY_NOW
RETRY_LATER
REMINDER_THEN_RETRY
ESCALATE
STOP
```

The exact available actions must correspond to the synthetic scenario and test-mode capabilities.

## Routing

Use:

```text
routine case
→ deterministic strategy

ambiguous / high-value case
→ AI strategy evaluation

high-risk case
→ human escalation
```

## Strategy Context

The router should consider:

- failure class
- amount
- retry count
- customer history
- merchant context
- payment state
- recovery window
- historical strategy outcome

## Testing

Create cases where the best strategy changes based on context.

## Exit Criteria

The system can select different permitted strategies for different contexts.

## Git Commit

```bash
git status
git diff
git diff --check
git add backend/recovery/routing/ backend/recovery/ranking/ tests/ docs/
git commit -m "feat: add dynamic recovery strategy routing"
```

---

# PHASE 5 — AI Investigation Agent

## Objective

Introduce meaningful agentic reasoning for diagnosis and strategy explanation.

The AI should not directly execute money actions.

## Agent Responsibilities

The agent may:

- aggregate relevant context,
- interpret failure evidence,
- identify likely cause,
- compare candidate strategies,
- explain why a strategy is preferable,
- identify ambiguity,
- recommend escalation.

## Tools

Potential read-only tools:

```text
get_payment_context()
get_customer_history()
get_merchant_context()
get_retry_history()
get_payment_route_health()
get_similar_recovery_cases()
get_strategy_outcomes()
```

Each tool must have:

```text
input schema
output schema
timeout
failure mode
permission
```

## Agent State

Use explicit structured state:

```text
recovery_case
diagnosis
context
candidate_strategies
strategy_reasons
confidence
selected_strategy
```

Do not implement the agent as one giant prompt.

## Exit Criteria

The AI adds measurable decision value beyond static routing on the validation set.

## Git Commit

```bash
git status
git diff
git diff --check
git add backend/agents/ backend/recovery/diagnosis/ tests/ docs/
git commit -m "feat: add AI recovery investigation agent"
```

---

# PHASE 6 — Expected Recovery Value Engine

## Objective

Turn strategy selection into an explicit economic decision.

## Formula

Implement the documented concept:

```text
ERV(action)
=
P(recovery | context, action)
× recoverable_amount
− action_cost
− friction_penalty
− risk_penalty
```

Keep individual components explicit.

## Candidate Evaluation

For each allowed strategy:

```text
predicted_recovery_probability
recoverable_amount
action_cost
friction_penalty
risk_penalty
expected_recovery_value
```

## Decision

Select the highest-value strategy **among policy-eligible candidates**.

Policy eligibility must happen before financial execution.

## Testing

Test:

- higher probability winning when other factors equal,
- lower-value action losing when cost is high,
- stop winning when action value is negative,
- escalation winning when automated action is too risky.

## Exit Criteria

The final action can be explained numerically through structured decision data.

## Git Commit

```bash
git status
git diff
git diff --check
git add backend/recovery/ranking/ backend/models/ tests/ docs/
git commit -m "feat: add expected recovery value engine"
```

---

# PHASE 7 — Policy Gate, Stopping Rules, and Escalation

## Objective

Make the financial control layer authoritative.

## Mandatory Checks

Implement:

```text
maximum retry count
maximum automated amount
minimum time between attempts
customer opt-out
action eligibility
payment state validity
idempotency eligibility
escalation threshold
recovery window expiry
```

## Action Levels

```text
READ_ONLY
RECOMMEND
APPROVAL_REQUIRED
CONTROLLED_EXECUTION
```

## Stopping Conditions

Stop when:

```text
retry limit reached
customer opted out
payment non-recoverable
recovery window expired
ERV below threshold
repeated interventions failed
policy condition failed
```

## Escalation

Support:

```text
HUMAN_REVIEW_REQUIRED
```

for ambiguous or restricted cases.

## Testing

Build explicit tests for every policy constraint.

## Exit Criteria

No money action can bypass the policy engine.

## Git Commit

```bash
git status
git diff
git diff --check
git add backend/recovery/policies/ backend/recovery/state_machine/ tests/ docs/
git commit -m "feat: add recovery policy and stopping controls"
```

---

# PHASE 8 — Razorpay Test-Mode Execution

## Objective

Connect the validated recovery workflow to Razorpay test-mode APIs.

## Integration Requirements

Use environment variables for:

```text
Razorpay test credentials
```

Never hard-code secrets.

## Flow

```text
Strategy Selected
      ↓
Policy Pass
      ↓
Prepare Test Action
      ↓
Idempotency Validation
      ↓
Razorpay Test API
      ↓
Request / Transaction Reference
      ↓
Outcome Reconciliation
```

## Integration Layer

Keep Razorpay-specific code isolated.

For example:

```text
integrations/
└── razorpay/
    ├── client
    ├── schemas
    ├── errors
    └── reconciliation
```

The rest of the system should depend on internal interfaces, not raw SDK calls everywhere.

## Failure Cases

Test:

- timeout
- malformed response
- rejected action
- duplicate request
- unknown payment state

## Exit Criteria

At least one complete test-mode recovery workflow can be executed safely.

## Git Commit

```bash
git status
git diff
git diff --check
git add integrations/razorpay/ backend/recovery/execution/ tests/ docs/
git commit -m "feat: integrate Razorpay test-mode recovery actions"
```

---

# PHASE 9 — State Machine, Idempotency, and Audit

## Objective

Make every money-related workflow explicitly stateful, deterministic and auditable.

## State Machine

Implement:

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
├── RECOVERED
├── RETRY_ELIGIBLE
├── ESCALATE
└── STOPPED
```

Additional failure state:

```text
EXECUTION_FAILED
```

## Idempotency

Every action should have a stable key based on relevant case/action identity.

Prevent duplicates caused by:

- duplicate events,
- retries,
- timeout ambiguity,
- agent retries,
- callback duplication,
- concurrency.

## Audit

Record:

```text
workflow_id
merchant_id
customer_id
revenue_at_risk
recoverable_estimate
failure_reason
context_reference
candidate_actions
selected_action
selection_reason
policy_checks
authorization
timestamp
Razorpay reference
outcome
recovered_amount
next_state
```

## Exit Criteria

Every financial workflow can be replayed from audit state without relying on hidden application state.

## Git Commit

```bash
git status
git diff
git diff --check
git add backend/state_machine/ backend/recovery/execution/ backend/audit/ tests/ docs/
git commit -m "feat: add recovery state machine and audit controls"
```

---

# PHASE 10 — Outcome Observation and Recovery Verification

## Objective

Determine whether the selected recovery intervention actually worked.

## Observe

Track:

```text
payment state
order state
subscription state
recovery completion
amount recovered
time to recovery
```

## Before / After

Record relevant state before action.

Then observe after action.

## Outcome Categories

```text
RECOVERED
FAILED
PENDING
RETRY_ELIGIBLE
STOPPED
ESCALATED
UNKNOWN
```

## Critical Rule

Never turn:

```text
API returned successfully
```

into:

```text
money recovered
```

unless the actual payment/recovery outcome confirms it.

## Exit Criteria

The system can independently verify successful and failed recovery.

## Git Commit

```bash
git status
git diff
git diff --check
git add backend/recovery/verification/ backend/audit/ tests/ evaluation/
git commit -m "feat: add recovery outcome verification"
```

---

# PHASE 11 — Closed-Loop Outcome Learning

## Objective

Allow future strategy selection to use actual observed outcomes.

## Store Strategy Outcomes

Store structured statistics such as:

```text
failure_type
strategy
customer/merchant context bucket
attempt_number
sample_count
success_rate
average_recovered_amount
observed_cost
```

## Learning Loop

```text
Prediction
 ↓
Action
 ↓
Actual Outcome
 ↓
Compare Expected vs Actual
 ↓
Update Strategy Statistics
```

## Do Not Implement

Do not implement:

```text
experience
→ model rewrites itself
```

The intended adaptation is:

```text
experience
→ better strategy selection
```

## Optional Reward Signal

If useful:

```text
predicted recovery value
→ actual recovery
→ reward / penalty
→ strategy update
```

The reward must come from observable outcome data.

## Evaluation

Compare:

```text
without outcome learning
vs
with outcome learning
```

Measure:

- recovery rate,
- incremental recovery,
- intervention count,
- cost,
- unnecessary actions.

## Exit Criteria

Outcome learning improves at least one business metric without violating reliability constraints.

## Git Commit

```bash
git status
git diff
git diff --check
git add backend/agents/ backend/recovery/ backend/models/ evaluation/ tests/ docs/
git commit -m "feat: add outcome-based recovery learning"
```

---

# PHASE 12 — Benchmark Harness and Baselines

## Objective

Build the complete evaluation system before final tuning.

## Baseline A — Fixed Retry

```text
failed payment
→ fixed retry
```

## Baseline B — Rule-Based

```text
failure class
→ predefined intervention
```

## Baseline C — ML Strategy Ranking

```text
context
→ predicted recovery probability
→ best static strategy
```

## Proposed System

```text
detect
→ diagnose
→ generate candidates
→ ERV
→ policy
→ execute
→ observe
→ learn/stop/escalate
```

## Required Metrics

### Detection

- revenue-at-risk precision
- revenue-at-risk recall
- false-positive rate
- missed-recovery rate

### Decision Quality

- intervention success rate
- wrong-intervention rate
- unnecessary intervention
- stopping-rule compliance
- escalation appropriateness

### Business

- revenue at risk
- recoverable revenue
- actual recovered revenue
- incremental recovery vs baseline
- recovery rate
- average recovered amount
- cost per recovered rupee

### Reliability

- duplicate-action rate
- policy violations
- execution failures
- graceful failures
- audit completeness

## Exit Criteria

One command runs the complete benchmark against all baselines.

## Git Commit

```bash
git status
git diff
git diff --check
git add evaluation/ datasets/test/ tests/ docs/
git commit -m "test: add revenue recovery benchmark and baselines"
```

---

# PHASE 13 — Ablation and Fixed-Budget Experiments

## Objective

Prove which parts of the system actually create value.

## Ablations

Compare:

```text
Full system

Full - dynamic routing

Full - AI diagnosis

Full - outcome learning

Full - ERV decision layer

Full - historical context
```

## Fixed Budgets

Keep equal:

```text
LLM/token budget
agent calls
interventions per case
recovery window
automated monetary limit
```

## Experiments

Measure:

1. incremental recovered revenue
2. recovery rate
3. unnecessary interventions
4. action cost
5. tool/agent usage
6. policy violations
7. reliability

## Exit Criteria

The results identify which components materially improve business outcome.

## Git Commit

```bash
git status
git diff
git diff --check
git add evaluation/experiments/ evaluation/reports/ docs/ tests/
git commit -m "test: add recovery ablation and budget experiments"
```

---

# PHASE 14 — Merchant Recovery Dashboard

## Objective

Build a frontend that explains decisions and business value.

## Dashboard

Show:

```text
Revenue at risk
Expected recoverable revenue
Recovered revenue
Incremental recovery
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
recoverable_estimate
failure_reason
current_state
selected_action
expected_recovery_value
policy_status
outcome
```

## Decision View

Show:

```text
Context
Diagnosis
Candidate strategies
Expected values
Selected action
Policy checks
Execution result
Recovered amount
```

## Audit View

Show complete chronological state transitions.

## Revenue Recovery Index

Optional UI signal:

```text
Today
7-day average
Revenue at risk
Expected recovery
Recovered revenue
```

Only use measured inputs.

## Exit Criteria

A judge can understand:

```text
what was lost
why it was lost
what the system chose
why it chose it
what happened
how much was recovered
```

without inspecting code.

## Git Commit

```bash
git status
git diff
git diff --check
git add frontend/ backend/api/ tests/ docs/
git commit -m "feat: add merchant recovery dashboard"
```

---

# PHASE 15 — Reliability, Security, and Failure Testing

## Objective

Prove the system behaves safely when things go wrong.

## Required Failures

### Razorpay timeout

Expected:

```text
do not duplicate
→ reconcile
→ defer/retry/escalate
```

### Unknown payment state

Expected:

```text
no second payment action
→ reconcile first
```

### Duplicate event

Expected:

```text
idempotency protection
```

### Retry limit reached

Expected:

```text
STOP
```

### Customer opt-out

Expected:

```text
STOP
```

### Low ERV

Expected:

```text
STOP
```

### AI unavailable

Expected:

```text
deterministic fallback
```

or:

```text
ESCALATE
```

### Policy rejection

Expected:

```text
ACTION_BLOCKED
```

No execution.

## Security

Test:

- secret handling
- unauthorized tool use
- policy bypass attempts
- malformed financial parameters
- audit tampering
- prompt injection at tool boundaries
- duplicate financial actions

## Exit Criteria

No tested failure causes:

- fake success,
- duplicate money action,
- policy bypass,
- fabricated recovery,
- missing audit record.

## Git Commit

```bash
git status
git diff
git diff --check
git add tests/ backend/ integrations/ docs/
git commit -m "test: harden recovery workflow and financial controls"
```

---

# PHASE 16 — Final Held-Out Evaluation, Demo, and Release

## Objective

Freeze the benchmark and produce the final hackathon submission.

## Freeze

Do not change after opening the final test set:

```text
test dataset
ground truth
evaluation metrics
baseline definitions
scoring logic
budget limits
```

## Final Batch

Run the complete held-out batch.

Produce:

```text
Cases evaluated
Revenue at risk
Recoverable revenue
Recovered revenue
Incremental recovery vs baseline
Recovery rate
Interventions
Successful interventions
Unnecessary interventions
Escalations
Stopped cases
Execution failures
Duplicate actions
Policy violations
Audit completeness
```

All values must be actual measured results.

## Final Demo

### Demo 1 — Successful recovery

```text
Payment failed
→ revenue at risk
→ diagnosis
→ candidate actions
→ ERV comparison
→ policy gate
→ Razorpay test-mode action
→ payment success
→ recovered revenue
```

### Demo 2 — Graceful failure

```text
Recovery selected
→ Razorpay timeout
→ no blind duplicate
→ state reconciliation
→ defer/retry/escalate
→ complete audit
```

### Demo 3 — Batch results

Show:

```text
₹X at risk
₹Y recoverable
₹Z recovered
+₹N incremental recovery vs baseline
0 duplicate actions
0 policy violations
100% audit completeness
```

## Documentation

Finalize:

```text
README.md
docs/architecture.md
docs/policies.md
docs/evaluation.md
docs/decisions.md
```

## CI

Verify:

- tests pass
- lint/type checks pass where configured
- Docker build works
- API starts
- benchmark smoke test passes
- test-mode integration configuration is valid

## Final Git Commit

```bash
git status
git diff
git diff --check
git add README.md docs/ evaluation/reports/ .github/ docker-compose.yml
git commit -m "docs: finalize revenue recovery hackathon release"
```

---

# 5. Git Commit Sequence

The intended history is:

```text
feat: initialize revenue recovery architecture
feat: add synthetic revenue recovery dataset
feat: add deterministic recovery baseline
feat: add revenue risk estimation layer
feat: add dynamic recovery strategy routing
feat: add AI recovery investigation agent
feat: add expected recovery value engine
feat: add recovery policy and stopping controls
feat: integrate Razorpay test-mode recovery actions
feat: add recovery state machine and audit controls
feat: add recovery outcome verification
feat: add outcome-based recovery learning
test: add revenue recovery benchmark and baselines
test: add recovery ablation and budget experiments
feat: add merchant recovery dashboard
test: harden recovery workflow and financial controls
docs: finalize revenue recovery hackathon release
```

Never use:

```bash
git add .
git add -A
```

Always inspect:

```bash
git status
git diff
git diff --check
```

before each commit.

---

# 6. Code Quality Contract

Write professional production-oriented code.

## General

- clear module boundaries
- single responsibility
- explicit interfaces
- strong typing
- validated inputs
- structured errors
- deterministic financial controls
- reusable components
- minimal duplication

## Python

Use:

- type hints
- Pydantic/dataclasses
- pytest
- structured logging
- explicit exceptions

Avoid:

- wildcard imports
- `print()` for production logging
- swallowed exceptions
- hidden global state
- unnecessary async
- magic constants

## Agent

Do not create one giant prompt.

Use explicit structured state:

```text
recovery_case
context
diagnosis
candidate_actions
expected_values
policy_result
selected_action
execution_result
outcome
next_state
```

## Comments and logs

**No emojis anywhere in code or code-adjacent technical content.**

No emojis in:

- comments,
- docstrings,
- identifiers,
- log messages,
- commit messages.

Comments should explain why non-obvious decisions exist.

---

# 7. Financial Safety Contract

The deterministic system owns:

```text
payment state
authorization
amount limits
retry limits
idempotency
stopping rules
policy
audit
```

The agent may recommend:

```text
RETRY_NOW
RETRY_LATER
REMINDER_THEN_RETRY
ESCALATE
STOP
```

but cannot bypass policy.

High-impact actions require explicit approval.

No unrestricted shell commands.

No real-money execution.

---

# 8. Evaluation Integrity Contract

Never fabricate:

- recovered revenue,
- model metrics,
- recovery rates,
- uplift,
- policy compliance,
- audit completeness.

Use:

```text
X
```

or:

```text
TBD
```

until measured.

The held-out test set must not influence tuning.

The strongest headline metric is:

> **Incremental recovered revenue over the deterministic baseline.**

Support it with:

- recovery rate,
- cost per recovered rupee,
- intervention quality,
- reliability,
- audit completeness.

---

# 9. Phase Completion Report

After every phase, report:

```text
Phase completed:
<phase number + name>

Implemented:
- ...

Tests:
- command
- result

Verification:
- ...

Files changed:
- ...

Commit:
<commit hash> <commit message>

Next phase:
<next phase + name>
```

If any exit criterion fails, do not claim completion.

---

# 10. Final Definition of Done

The project is complete only when:

- [x] Revenue at risk is detected.
- [x] Recoverable revenue is distinguished from revenue at risk.
- [x] Deterministic baseline exists.
- [x] ML/statistical recoverability layer exists.
- [x] Multiple recovery strategies exist.
- [x] Dynamic routing exists.
- [x] AI diagnosis and strategy reasoning are meaningful.
- [x] ERV is calculated explicitly.
- [x] Policy gating is authoritative.
- [x] Stopping rules exist.
- [x] Human escalation exists.
- [x] Razorpay test-mode workflow works (authenticated orders, payment links, and HMAC webhooks).
- [x] Idempotency is enforced.
- [x] Payment state reconciliation exists.
- [x] Every money action is auditable.
- [x] Outcome verification exists.
- [x] Outcome-based learning is evaluated.
- [x] Baselines are evaluated.
- [x] Ablations are evaluated.
- [x] Fixed-budget experiments are evaluated.
- [x] Merchant dashboard explains decisions.
- [x] Graceful failure is demonstrated.
- [x] Security and safety tests pass.
- [x] Final held-out batch is evaluated.
- [x] Incremental recovery vs baseline is measured.
- [x] No benchmark claims are fabricated.
- [x] Final documentation is synchronized.

---

# 11. Phase 18 Log: Razorpay Test Mode & Webhook Architecture

- **Test Mode Client**: Authenticated HTTP Basic Auth calls to `https://api.razorpay.com/v1/orders` and `/payment_links`. Graceful deterministic fallback to mock mode if credentials absent.
- **Webhook Ingestion**: HMAC-SHA256 signature verification on `POST /api/v1/webhooks/razorpay` with event deduplication in SQLite.
- **Authoritative Outcome Verification**: Resolves gateway state (`RECOVERED`, `FAILED`, `UNKNOWN`) through `RecoveryOutcomeVerifier` before committing audit entries or updating Bayesian statistics.
- **Persistent Bayesian Learning**: Stores `StrategyPerformanceBucket` aggregates in SQLite table `strategy_learning_stats` to persist across restarts.
- **Security Invariants**: 0 secrets exposed in logs or UI; policy gate checked before external API calls; idempotency locks enforced.
- **Tests**: 80/80 passing pytest suite.

---

# 12. One-Sentence Goal

> **Build an AI-native revenue recovery controller that identifies recoverable revenue, understands why it is slipping away, selects the safest high-value intervention, executes bounded Razorpay test-mode recovery actions, and learns from measured outcomes to recover more revenue with fewer unnecessary actions.**
