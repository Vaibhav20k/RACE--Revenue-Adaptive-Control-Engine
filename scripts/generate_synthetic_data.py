"""Deterministic synthetic revenue event and ground-truth generator for RACE."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import random
import uuid
from datetime import datetime, timezone, timedelta
from typing import Tuple, List, Dict, Any

from backend.core.constants import EventType, FailureClass, RecoveryStrategy
from backend.domain.events import RevenueEvent
from backend.domain.ground_truth import CaseGroundTruth


def generate_single_scenario(
    index: int,
    rng: random.Random,
    base_time: datetime,
) -> Tuple[RevenueEvent, CaseGroundTruth]:
    """Generates a single paired synthetic revenue event and hidden ground truth."""
    event_id = f"evt_{uuid.UUID(int=rng.getrandbits(128)).hex[:12]}"
    case_id = f"case_{index:04d}"
    
    archetype = rng.choices(
        population=[
            "network_glitch_upi",
            "insufficient_balance_card",
            "gateway_outage",
            "auth_challenge_sms",
            "checkout_dropoff_cart",
            "subscription_mandate_fail",
            "unrecoverable_fraud",
            "unrecoverable_expired_card",
            "customer_opted_out_case",
            "high_value_ambiguous",
            "low_value_uneconomic",
            "upstream_timeout_failure",
        ],
        weights=[0.18, 0.16, 0.12, 0.12, 0.10, 0.08, 0.05, 0.05, 0.04, 0.04, 0.03, 0.03],
        k=1,
    )[0]

    merchant_id = f"mer_{rng.choice(['retail_prime', 'saas_cloud', 'quick_commerce', 'edtech_plus', 'fintech_hub'])}"
    customer_id = f"cust_{rng.randint(1000, 9999)}"
    timestamp = (base_time + timedelta(minutes=index * 3 + rng.randint(0, 5))).isoformat()
    customer_recovery_rate = round(rng.uniform(0.2, 0.9), 2)
    retry_count = 0
    customer_opted_out = False
    payment_state = "FAILED"
    amount = round(rng.uniform(250.0, 8500.0), 2)
    currency = "INR"

    if archetype == "network_glitch_upi":
        event_type = EventType.FAILED_PAYMENT
        failure_class = FailureClass.TEMPORARY_NETWORK
        failure_reason = "UPI_TIMED_OUT_SWITCH_BLIP"
        payment_method = "UPI"
        gateway_route_health = "UP"
        true_revenue_at_risk = amount
        true_recoverable_amount = amount
        true_optimal = RecoveryStrategy.RETRY_NOW
        allowed_actions = [RecoveryStrategy.RETRY_NOW, RecoveryStrategy.RETRY_LATER, RecoveryStrategy.STOP]
        cf_outcomes = {
            "RETRY_NOW": {"outcome": "RECOVERED", "recovered_amount": amount, "p_success": 0.88},
            "RETRY_LATER": {"outcome": "RECOVERED", "recovered_amount": amount, "p_success": 0.82},
            "REMINDER_THEN_RETRY": {"outcome": "RECOVERED", "recovered_amount": amount, "p_success": 0.75},
            "HUMAN_ESCALATION": {"outcome": "RECOVERED", "recovered_amount": amount, "p_success": 0.70},
            "STOP": {"outcome": "STOPPED", "recovered_amount": 0.0, "p_success": 0.0},
        }
        requires_escalation = False
        is_policy_blocked = False

    elif archetype == "insufficient_balance_card":
        event_type = EventType.FAILED_PAYMENT
        failure_class = FailureClass.INSUFFICIENT_FUNDS
        failure_reason = "INSUFFICIENT_FUNDS_OR_LIMIT"
        payment_method = "CARD"
        gateway_route_health = "UP"
        true_revenue_at_risk = amount
        true_recoverable_amount = amount
        true_optimal = RecoveryStrategy.REMINDER_THEN_RETRY
        allowed_actions = [RecoveryStrategy.REMINDER_THEN_RETRY, RecoveryStrategy.RETRY_LATER, RecoveryStrategy.STOP]
        cf_outcomes = {
            "RETRY_NOW": {"outcome": "FAILED", "recovered_amount": 0.0, "p_success": 0.15},
            "RETRY_LATER": {"outcome": "RECOVERED", "recovered_amount": amount, "p_success": 0.45},
            "REMINDER_THEN_RETRY": {"outcome": "RECOVERED", "recovered_amount": amount, "p_success": 0.85},
            "HUMAN_ESCALATION": {"outcome": "RECOVERED", "recovered_amount": amount, "p_success": 0.60},
            "STOP": {"outcome": "STOPPED", "recovered_amount": 0.0, "p_success": 0.0},
        }
        requires_escalation = False
        is_policy_blocked = False

    elif archetype == "gateway_outage":
        event_type = EventType.FAILED_PAYMENT
        failure_class = FailureClass.GATEWAY_DEGRADATION
        failure_reason = "ISSUER_GATEWAY_503_UNAVAILABLE"
        payment_method = "NETBANKING"
        gateway_route_health = "DEGRADED"
        true_revenue_at_risk = amount
        true_recoverable_amount = amount
        true_optimal = RecoveryStrategy.RETRY_LATER
        allowed_actions = [RecoveryStrategy.RETRY_LATER, RecoveryStrategy.STOP]
        cf_outcomes = {
            "RETRY_NOW": {"outcome": "FAILED", "recovered_amount": 0.0, "p_success": 0.05},
            "RETRY_LATER": {"outcome": "RECOVERED", "recovered_amount": amount, "p_success": 0.82},
            "REMINDER_THEN_RETRY": {"outcome": "RECOVERED", "recovered_amount": amount, "p_success": 0.50},
            "HUMAN_ESCALATION": {"outcome": "RECOVERED", "recovered_amount": amount, "p_success": 0.65},
            "STOP": {"outcome": "STOPPED", "recovered_amount": 0.0, "p_success": 0.0},
        }
        requires_escalation = False
        is_policy_blocked = False

    elif archetype == "auth_challenge_sms":
        event_type = EventType.FAILED_PAYMENT
        failure_class = FailureClass.AUTH_REQUIRED
        failure_reason = "CUSTOMER_3DS_OTP_TIMEOUT"
        payment_method = "CARD"
        gateway_route_health = "UP"
        true_revenue_at_risk = amount
        true_recoverable_amount = amount
        true_optimal = RecoveryStrategy.REMINDER_THEN_RETRY
        allowed_actions = [RecoveryStrategy.REMINDER_THEN_RETRY, RecoveryStrategy.STOP]
        cf_outcomes = {
            "RETRY_NOW": {"outcome": "FAILED", "recovered_amount": 0.0, "p_success": 0.08},
            "RETRY_LATER": {"outcome": "FAILED", "recovered_amount": 0.0, "p_success": 0.20},
            "REMINDER_THEN_RETRY": {"outcome": "RECOVERED", "recovered_amount": amount, "p_success": 0.78},
            "HUMAN_ESCALATION": {"outcome": "RECOVERED", "recovered_amount": amount, "p_success": 0.55},
            "STOP": {"outcome": "STOPPED", "recovered_amount": 0.0, "p_success": 0.0},
        }
        requires_escalation = False
        is_policy_blocked = False

    elif archetype == "checkout_dropoff_cart":
        event_type = EventType.CHECKOUT_ABANDONMENT
        failure_class = FailureClass.CUSTOMER_ABANDONMENT
        failure_reason = "USER_LEFT_CHECKOUT_SESSION"
        payment_method = "UPI"
        gateway_route_health = "UP"
        payment_state = "ATTEMPTED"
        true_revenue_at_risk = amount
        true_recoverable_amount = amount * 0.75
        true_optimal = RecoveryStrategy.REMINDER_THEN_RETRY
        allowed_actions = [RecoveryStrategy.REMINDER_THEN_RETRY, RecoveryStrategy.STOP]
        cf_outcomes = {
            "RETRY_NOW": {"outcome": "FAILED", "recovered_amount": 0.0, "p_success": 0.02},
            "RETRY_LATER": {"outcome": "FAILED", "recovered_amount": 0.0, "p_success": 0.10},
            "REMINDER_THEN_RETRY": {"outcome": "RECOVERED", "recovered_amount": true_recoverable_amount, "p_success": 0.68},
            "HUMAN_ESCALATION": {"outcome": "RECOVERED", "recovered_amount": true_recoverable_amount, "p_success": 0.40},
            "STOP": {"outcome": "STOPPED", "recovered_amount": 0.0, "p_success": 0.0},
        }
        requires_escalation = False
        is_policy_blocked = False

    elif archetype == "subscription_mandate_fail":
        event_type = EventType.RECURRING_PAYMENT_FAILURE
        failure_class = FailureClass.INSUFFICIENT_FUNDS
        failure_reason = "AUTO_DEBIT_MANDATE_EXECUTION_FAILED"
        payment_method = "CARD"
        gateway_route_health = "UP"
        true_revenue_at_risk = amount
        true_recoverable_amount = amount
        true_optimal = RecoveryStrategy.RETRY_LATER
        allowed_actions = [RecoveryStrategy.RETRY_LATER, RecoveryStrategy.REMINDER_THEN_RETRY, RecoveryStrategy.STOP]
        cf_outcomes = {
            "RETRY_NOW": {"outcome": "FAILED", "recovered_amount": 0.0, "p_success": 0.10},
            "RETRY_LATER": {"outcome": "RECOVERED", "recovered_amount": amount, "p_success": 0.72},
            "REMINDER_THEN_RETRY": {"outcome": "RECOVERED", "recovered_amount": amount, "p_success": 0.74},
            "HUMAN_ESCALATION": {"outcome": "RECOVERED", "recovered_amount": amount, "p_success": 0.60},
            "STOP": {"outcome": "STOPPED", "recovered_amount": 0.0, "p_success": 0.0},
        }
        requires_escalation = False
        is_policy_blocked = False

    elif archetype == "unrecoverable_fraud":
        event_type = EventType.FAILED_PAYMENT
        failure_class = FailureClass.FRAUD_SUSPECTED
        failure_reason = "RISK_ENGINE_BLOCK_SUSPECTED_STOLEN_INSTRUMENT"
        payment_method = "CARD"
        gateway_route_health = "UP"
        true_revenue_at_risk = amount
        true_recoverable_amount = 0.0
        true_optimal = RecoveryStrategy.STOP
        allowed_actions = [RecoveryStrategy.STOP]
        cf_outcomes = {
            "RETRY_NOW": {"outcome": "FAILED", "recovered_amount": 0.0, "p_success": 0.0},
            "RETRY_LATER": {"outcome": "FAILED", "recovered_amount": 0.0, "p_success": 0.0},
            "REMINDER_THEN_RETRY": {"outcome": "FAILED", "recovered_amount": 0.0, "p_success": 0.0},
            "HUMAN_ESCALATION": {"outcome": "STOPPED", "recovered_amount": 0.0, "p_success": 0.0},
            "STOP": {"outcome": "STOPPED", "recovered_amount": 0.0, "p_success": 1.0},
        }
        requires_escalation = False
        is_policy_blocked = True

    elif archetype == "unrecoverable_expired_card":
        event_type = EventType.FAILED_PAYMENT
        failure_class = FailureClass.EXPIRED_CARD
        failure_reason = "CARD_PERMANENTLY_EXPIRED_OR_INACTIVE"
        payment_method = "CARD"
        gateway_route_health = "UP"
        true_revenue_at_risk = amount
        true_recoverable_amount = 0.0
        true_optimal = RecoveryStrategy.STOP
        allowed_actions = [RecoveryStrategy.STOP]
        cf_outcomes = {
            "RETRY_NOW": {"outcome": "FAILED", "recovered_amount": 0.0, "p_success": 0.0},
            "RETRY_LATER": {"outcome": "FAILED", "recovered_amount": 0.0, "p_success": 0.0},
            "REMINDER_THEN_RETRY": {"outcome": "FAILED", "recovered_amount": 0.0, "p_success": 0.0},
            "HUMAN_ESCALATION": {"outcome": "STOPPED", "recovered_amount": 0.0, "p_success": 0.0},
            "STOP": {"outcome": "STOPPED", "recovered_amount": 0.0, "p_success": 1.0},
        }
        requires_escalation = False
        is_policy_blocked = True

    elif archetype == "customer_opted_out_case":
        event_type = EventType.FAILED_PAYMENT
        failure_class = FailureClass.CUSTOMER_ABANDONMENT
        failure_reason = "CUSTOMER_EXPLICIT_DO_NOT_CONTACT"
        payment_method = "UPI"
        gateway_route_health = "UP"
        customer_opted_out = True
        true_revenue_at_risk = amount
        true_recoverable_amount = 0.0
        true_optimal = RecoveryStrategy.STOP
        allowed_actions = [RecoveryStrategy.STOP]
        cf_outcomes = {
            "RETRY_NOW": {"outcome": "FAILED", "recovered_amount": 0.0, "p_success": 0.0},
            "RETRY_LATER": {"outcome": "FAILED", "recovered_amount": 0.0, "p_success": 0.0},
            "REMINDER_THEN_RETRY": {"outcome": "FAILED", "recovered_amount": 0.0, "p_success": 0.0},
            "HUMAN_ESCALATION": {"outcome": "STOPPED", "recovered_amount": 0.0, "p_success": 0.0},
            "STOP": {"outcome": "STOPPED", "recovered_amount": 0.0, "p_success": 1.0},
        }
        requires_escalation = False
        is_policy_blocked = True

    elif archetype == "high_value_ambiguous":
        event_type = EventType.FAILED_PAYMENT
        failure_class = FailureClass.UNKNOWN
        failure_reason = "HIGH_VALUE_TRANSACTION_MANUAL_CLEARANCE_REQUIRED"
        payment_method = "NETBANKING"
        gateway_route_health = "UP"
        amount = round(rng.uniform(60000.0, 180000.0), 2)
        true_revenue_at_risk = amount
        true_recoverable_amount = amount
        true_optimal = RecoveryStrategy.HUMAN_ESCALATION
        allowed_actions = [RecoveryStrategy.HUMAN_ESCALATION, RecoveryStrategy.STOP]
        cf_outcomes = {
            "RETRY_NOW": {"outcome": "FAILED", "recovered_amount": 0.0, "p_success": 0.15},
            "RETRY_LATER": {"outcome": "FAILED", "recovered_amount": 0.0, "p_success": 0.25},
            "REMINDER_THEN_RETRY": {"outcome": "RECOVERED", "recovered_amount": amount, "p_success": 0.50},
            "HUMAN_ESCALATION": {"outcome": "RECOVERED", "recovered_amount": amount, "p_success": 0.90},
            "STOP": {"outcome": "STOPPED", "recovered_amount": 0.0, "p_success": 0.0},
        }
        requires_escalation = True
        is_policy_blocked = True

    elif archetype == "low_value_uneconomic":
        event_type = EventType.FAILED_PAYMENT
        failure_class = FailureClass.INSUFFICIENT_FUNDS
        failure_reason = "MICRO_TRANSACTION_DROP"
        payment_method = "WALLET"
        gateway_route_health = "UP"
        amount = round(rng.uniform(10.0, 25.0), 2)
        true_revenue_at_risk = amount
        true_recoverable_amount = 0.0
        true_optimal = RecoveryStrategy.STOP
        allowed_actions = [RecoveryStrategy.STOP]
        cf_outcomes = {
            "RETRY_NOW": {"outcome": "FAILED", "recovered_amount": 0.0, "p_success": 0.30},
            "RETRY_LATER": {"outcome": "FAILED", "recovered_amount": 0.0, "p_success": 0.30},
            "REMINDER_THEN_RETRY": {"outcome": "FAILED", "recovered_amount": 0.0, "p_success": 0.30},
            "HUMAN_ESCALATION": {"outcome": "STOPPED", "recovered_amount": 0.0, "p_success": 0.0},
            "STOP": {"outcome": "STOPPED", "recovered_amount": 0.0, "p_success": 1.0},
        }
        requires_escalation = False
        is_policy_blocked = False

    elif archetype == "upstream_timeout_failure":
        event_type = EventType.FAILED_PAYMENT
        failure_class = FailureClass.GATEWAY_DEGRADATION
        failure_reason = "GATEWAY_TIMEOUT_HTTP_504"
        payment_method = "UPI"
        gateway_route_health = "DEGRADED"
        true_revenue_at_risk = amount
        true_recoverable_amount = amount
        true_optimal = RecoveryStrategy.RETRY_LATER
        allowed_actions = [RecoveryStrategy.RETRY_LATER, RecoveryStrategy.HUMAN_ESCALATION, RecoveryStrategy.STOP]
        cf_outcomes = {
            "RETRY_NOW": {"outcome": "FAILED", "recovered_amount": 0.0, "p_success": 0.02},
            "RETRY_LATER": {"outcome": "RECOVERED", "recovered_amount": amount, "p_success": 0.70},
            "REMINDER_THEN_RETRY": {"outcome": "RECOVERED", "recovered_amount": amount, "p_success": 0.40},
            "HUMAN_ESCALATION": {"outcome": "RECOVERED", "recovered_amount": amount, "p_success": 0.60},
            "STOP": {"outcome": "STOPPED", "recovered_amount": 0.0, "p_success": 0.0},
        }
        requires_escalation = False
        is_policy_blocked = False

    event = RevenueEvent(
        event_id=event_id,
        timestamp=timestamp,
        event_type=event_type,
        merchant_id=merchant_id,
        customer_id=customer_id,
        order_id=f"order_{index:04d}",
        payment_id=f"pay_{index:04d}",
        subscription_id=f"sub_{index:04d}" if event_type == EventType.RECURRING_PAYMENT_FAILURE else None,
        amount=amount,
        currency=currency,
        payment_method=payment_method,
        failure_reason=failure_reason,
        failure_class=failure_class,
        payment_state=payment_state,
        retry_count=retry_count,
        time_since_failure_minutes=round(rng.uniform(1.0, 120.0), 1),
        customer_recovery_history_rate=customer_recovery_rate,
        customer_opted_out=customer_opted_out,
        merchant_mcc_tier=rng.choice(["low", "medium", "high"]),
        gateway_route_health=gateway_route_health,
        metadata={"scenario_archetype": archetype, "case_id": case_id},
    )

    gt = CaseGroundTruth(
        case_id=case_id,
        event_id=event_id,
        true_revenue_at_risk=true_revenue_at_risk,
        true_recoverable_amount=true_recoverable_amount,
        true_optimal_strategy=true_optimal,
        true_counterfactual_outcomes=cf_outcomes,
        allowed_actions=allowed_actions,
        requires_escalation=requires_escalation,
        is_policy_blocked=is_policy_blocked,
        scenario_description=archetype,
    )

    return event, gt


def generate_dataset_split(
    count: int,
    seed: int,
    start_index: int,
    output_dir: Path,
    split_name: str,
) -> Tuple[List[RevenueEvent], List[CaseGroundTruth]]:
    """Generates and persists a reproducible dataset split."""
    rng = random.Random(seed)
    base_time = datetime(2026, 8, 20, 10, 0, 0, tzinfo=timezone.utc)
    
    events = []
    ground_truths = []
    
    for i in range(count):
        idx = start_index + i
        evt, gt = generate_single_scenario(idx, rng, base_time)
        events.append(evt)
        ground_truths.append(gt)

    output_dir.mkdir(parents=True, exist_ok=True)
    events_path = output_dir / f"revenue_events_{split_name}.json"
    gt_path = output_dir / f"ground_truth_{split_name}.json"

    with open(events_path, "w", encoding="utf-8") as f:
        json.dump([e.model_dump() for e in events], f, indent=2)

    with open(gt_path, "w", encoding="utf-8") as f:
        json.dump([g.model_dump() for g in ground_truths], f, indent=2)

    return events, ground_truths


def main():
    base_path = Path("datasets")
    generate_dataset_split(600, seed=42, start_index=1, output_dir=base_path / "train", split_name="train")
    generate_dataset_split(200, seed=43, start_index=601, output_dir=base_path / "validation", split_name="validation")
    generate_dataset_split(200, seed=44, start_index=801, output_dir=base_path / "test", split_name="test")


if __name__ == "__main__":
    main()
