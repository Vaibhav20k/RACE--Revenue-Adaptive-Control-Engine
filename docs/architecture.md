# RACE Architecture Specification

## 1. System Topology

RACE is organized into modular decoupled layers with clean boundaries between statistical inference, AI reasoning, deterministic control, and external execution.

```text
+-----------------------------------------------------------------------------------+
|                                EVENT INGESTION                                    |
|   Payment Failures | Checkout Dropoffs | Subscription Retries | Webhook Events    |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                           DETECTION & DIAGNOSIS                                   |
|   - Revenue-at-Risk Classifier (ML / Statistical)                                 |
|   - Context Builder (Customer, Merchant, Payment Route, Failure Telemetry)        |
|   - AI Diagnostic Engine (Root Cause Synthesis & Ambiguity Tagging)               |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                        STRATEGY ROUTER & ERV ENGINE                               |
|   - Candidate Strategies: RETRY_NOW, RETRY_LATER, REMINDER_THEN_RETRY,            |
|                           HUMAN_ESCALATION, STOP                                  |
|   - Expected Recovery Value Evaluator: ERV = P(rec) * Amount - Cost - Friction    |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                     DETERMINISTIC SAFETY & POLICY GATE                            |
|   - Retry Limits, Cooldown Intervals, Automation Cap (INR), State Validation      |
|   - Idempotency Ledger, Customer Opt-Out Filter, Expiry Enforcement               |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                         BOUNDED EXECUTION LAYER                                   |
|   - Razorpay Test-Mode Client (Order, Payment Retry, Customer Notification)       |
|   - Timeout, Failure & State Reconciliation Handler                               |
+-----------------------------------------------------------------------------------+
                                         |
                                         v
+-----------------------------------------------------------------------------------+
|                     OUTCOME OBSERVATION & CLOSED-LOOP LEARNING                    |
|   - Gateway State Observer (RECOVERED, FAILED, PENDING, UNKNOWN)                  |
|   - Incremental Revenue Ledger                                                    |
|   - Strategy Outcome Statistics & Weight Updating                                 |
+-----------------------------------------------------------------------------------+
```

## 2. Component Specifications

### 2.1 Event Ingestion
Ingests real-time or batch events with strict schema validation. Emits immutable event envelopes with unique `event_id`, timestamps, merchant context, customer context, and transaction identifiers.

### 2.2 Revenue-at-Risk Detection
Calculates the probability $P(\text{at\_risk})$ and estimated recoverable amount. Discards noise and immediate non-recoverable terminations before compute-heavy routing.

### 2.3 Context & Diagnostic Synthesizer
Enriches the event with merchant retry tolerances, historical customer response latency, gateway health status, and historical outcome distributions.

### 2.4 Strategy Router & ERV Engine
Generates eligible recovery candidates for the specific failure class. Calculates ERV numerically for each candidate.

### 2.5 Policy & Safety Gate
Deterministic validator acting as the sole authority on whether an action is executed. Never overridden by LLM recommendations.

### 2.6 Execution & Reconciliation
Dispatches approved actions to Razorpay test-mode APIs. Handles network partitions, upstream timeouts, and ambiguous states safely by reconciling before any retry.

### 2.7 Outcome Verification & Learning
Listens for webhook updates and polls payment verification endpoints. Updates empirical strategy success tables to adapt future ERV estimates.
