# RACE Financial Policy & Safety Specification

## 1. Core Principle

Financial operations in RACE are governed by deterministic invariant rules. Machine learning and AI agents provide proposals, diagnoses, and ranking scores, but execution authority rests strictly with the Policy Gate.

## 2. Mandatory Policy Rules

### 2.1 Maximum Retry Limit
- Default limit: 3 automated retry attempts per recovery case.
- Once `retry_count >= MAX_RETRY_COUNT`, no further automated payment attempts may be scheduled. The policy transitions the case to `STOPPED` or `ESCALATE`.

### 2.2 Maximum Automated Monetary Threshold
- Default limit: INR 50,000.00.
- Any transaction where `amount > MAX_AUTOMATED_AMOUNT_INR` requires human approval (`HUMAN_REVIEW_REQUIRED`).

### 2.3 Mandatory Cooldown Intervals
- Minimum interval between automated payment actions on the same customer/order: 30 minutes (configurable by merchant).
- Action requested within cooldown window is rejected with `COOLDOWN_VIOLATION`.

### 2.4 Customer Opt-Out / Dispute
- If `customer_opted_out == True` or an active chargeback/dispute is registered, all automated actions are immediately blocked and the state is set to `STOPPED`.

### 2.5 Recovery Window Expiration
- Maximum lifetime for a recovery opportunity: 72 hours from initial failure event.
- Expired cases cannot trigger automated payments.

### 2.6 Idempotency Key Enforcement
- Every action must construct a deterministic idempotency key:
  `idempotency_key = sha256(merchant_id:customer_id:payment_id:action_type:attempt_number)`
- Duplicate keys within the active TTL are rejected immediately without executing backend calls.

### 2.7 Payment State Pre-condition
- Before executing a payment retry, the current payment state must be verified as `FAILED` or `PENDING_RETRY`.
- If payment is already `PAID` or `RECOVERED`, action is cancelled.
- If payment state is `UNKNOWN` (e.g. following an upstream timeout), no retry is permitted until payment state is authoritatively reconciled.

## 3. Stopping Conditions

The engine automatically halts interventions (`STOPPED`) under any of the following conditions:
1. Hard retry limit reached without success.
2. Estimated Expected Recovery Value (ERV) is non-positive ($ERV \le 0$).
3. Explicit customer opt-out received.
4. Recovery window exceeded.
5. Non-recoverable failure code (e.g. `FRAUD_SUSPECTED`, `CARD_EXPIRED_PERMANENT`, `ACCOUNT_CLOSED`).
