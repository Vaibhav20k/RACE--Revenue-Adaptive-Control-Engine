# Razorpay Test Mode Integration & Webhook Architecture

> **Security Notice**: RACE uses Razorpay **Test Mode** for external payment integration testing and reconciliation validation. No live-money transactions are performed.

---

## 1. Overview

RACE integrates directly with Razorpay's Test Mode APIs to execute recovery actions (Orders, Payment Links) and listen to asynchronous lifecycle webhooks (`payment.captured`, `order.paid`, `payment.failed`) while strictly preserving deterministic policy gating and cryptographic idempotency.

```text
Revenue Event
    │
    ▼
Diagnosis & Multi-Tool Evidence
    │
    ▼
ERV Economic Optimization (Net Payoff Maximization)
    │
    ▼
Deterministic Policy Gate (Hard Retry Limits & Amount Caps)
    │
    ▼
Idempotency Lock (SHA-256 Key Acquisition)
    │
    ▼
Razorpay TEST MODE API (Authenticated Basic Auth Dispatch)
    │
    ▼
Actual Test-Mode Response (Order ID / Payment Link URL)
    │
    ▼
Outcome Verification (State Machine Authoritative Reconciliation)
    │
    ▼
Immutable Cryptographic Audit Ledger
    │
    ▼
Closed-Loop Bayesian Conjugate Update (Dirichlet/Beta Smoothing)
```

---

## 2. Environment Configuration

Razorpay Test Mode credentials are read exclusively from environment variables or local `.env` (which is gitignored):

| Environment Variable | Description | Example / Format |
| :--- | :--- | :--- |
| `RAZORPAY_KEY_ID` | Razorpay Test API Key ID | `rzp_test_...` |
| `RAZORPAY_KEY_SECRET` | Razorpay Test Key Secret | *(Secret string)* |
| `RAZORPAY_WEBHOOK_SECRET` | Secret configured for webhook HMAC-SHA256 validation | `rzp_test_whsec_...` |

### Setting Up `.env` Locally:
```bash
# Copy example configuration
cp .env.example .env

# Edit .env and configure your Test Mode keys
RAZORPAY_KEY_ID=rzp_test_your_test_key
RAZORPAY_KEY_SECRET=your_test_secret
RAZORPAY_WEBHOOK_SECRET=your_test_webhook_secret
```

---

## 3. MOCK vs. TEST_MODE Runtime Behavior

RACE dynamically resolves its execution mode on initialization:

- **TEST_MODE**: Triggered when non-placeholder `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` are present in environment variables. Authenticated HTTP requests are dispatched to `https://api.razorpay.com/v1/orders` and `/payment_links`.
- **MOCK**: Automatically selected when credentials contain `mock` or `placeholder` or are absent. Returns deterministic test adapter responses without external HTTP calls, ensuring 100% offline development and reproducible unit testing.

The active mode is queryable via `GET /api/v1/config/environment` (which returns only safe non-secret metadata such as key prefix).

---

## 4. Webhook Verification & Processing

RACE exposes a production-ready webhook endpoint at `POST /api/v1/webhooks/razorpay`.

### Signature Verification Algorithm:
1. Razorpay delivers the webhook with header `X-Razorpay-Signature`.
2. RACE computes:
   $$\text{computed\_sig} = \text{HMAC-SHA256}(\text{key}=\text{RAZORPAY\_WEBHOOK\_SECRET}, \text{msg}=\text{raw\_body})$$
3. RACE compares signatures in constant time using `hmac.compare_digest`.
4. Invalid or missing signatures return `HTTP 400 Bad Request`.

### Webhook Idempotency:
- Webhook event IDs are recorded in the `processed_webhooks` SQLite table.
- Duplicate webhook deliveries return `{ "status": "ignored_duplicate" }` without re-executing state changes or double-updating Bayesian statistics.

---

## 5. Manual Real Test Mode Verification

To verify end-to-end integration against Razorpay's live Test Mode API:

```bash
# Run the automated Test Mode verification script
python -c "
import dotenv; dotenv.load_dotenv()
from integrations.razorpay.client import RazorpayTestClient
from integrations.razorpay.schemas import RazorpayOrderRequest
client = RazorpayTestClient()
res = client.create_order(RazorpayOrderRequest(amount=10000, currency='INR', receipt='rec_test_manual'))
print('Order successfully created on Razorpay Test Mode:', res.id, 'Status:', res.status)
"
```

---

## 6. Security Invariants

1. **No Live Mode**: The client only connects to Razorpay Test Mode (`https://api.razorpay.com/v1`).
2. **Zero Secret Exposure**: Key secrets are never logged, never returned in API responses, and never rendered in frontend templates.
3. **Policy Gate Authority**: The deterministic policy gate executes *before* external API dispatch. If a strategy is `STOP` or policy is `BLOCKED`, the Razorpay API is **never called**.
4. **Authoritative Outcome Verification**: An action is marked `RECOVERED` only when verified through gateway state inspection or authoritative webhook payload, never simply on HTTP 200 order creation.
