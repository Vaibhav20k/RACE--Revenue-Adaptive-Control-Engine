"""Persistent SQLite storage layer for user-created custom test cases."""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from backend.domain.events import RevenueEvent
from backend.domain.ground_truth import CaseGroundTruth
from backend.core.constants import FailureClass, RecoveryStrategy


class CustomCaseRepository:
    """Manages persistent SQLite storage for user-created custom recovery cases."""

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_dir = Path("data")
            db_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = db_dir / "race_cases.db"
        else:
            self.db_path = Path(db_path)
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Initializes tables for custom cases, webhook deduplication, and persistent learning stats."""
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS custom_cases (
                    case_id TEXT PRIMARY KEY,
                    source TEXT DEFAULT 'CUSTOM',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    amount REAL NOT NULL,
                    currency TEXT DEFAULT 'INR',
                    failure_class TEXT NOT NULL,
                    failure_reason TEXT NOT NULL,
                    payment_method TEXT NOT NULL,
                    gateway_route_health TEXT NOT NULL,
                    customer_recovery_history_rate REAL DEFAULT 0.5,
                    customer_opted_out INTEGER DEFAULT 0,
                    retry_count INTEGER DEFAULT 0,
                    time_since_failure_minutes REAL DEFAULT 0.0,
                    merchant_id TEXT DEFAULT 'merchant_custom',
                    customer_id TEXT DEFAULT 'cust_custom',
                    payment_id TEXT,
                    order_id TEXT,
                    current_state TEXT NOT NULL,
                    selected_strategy TEXT,
                    recovered_amount REAL DEFAULT 0.0,
                    is_recovered INTEGER DEFAULT 0,
                    is_escalated INTEGER DEFAULT 0,
                    is_stopped INTEGER DEFAULT 0,
                    raw_event_json TEXT NOT NULL,
                    ground_truth_json TEXT NOT NULL,
                    audit_trail_json TEXT DEFAULT '[]'
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS processed_webhooks (
                    webhook_id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    case_id TEXT,
                    received_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS strategy_learning_stats (
                    failure_class TEXT NOT NULL,
                    strategy TEXT NOT NULL,
                    sample_count INTEGER DEFAULT 0,
                    success_count INTEGER DEFAULT 0,
                    total_recovered_amount REAL DEFAULT 0.0,
                    total_expected_value REAL DEFAULT 0.0,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (failure_class, strategy)
                )
                """
            )
            conn.commit()

    def record_processed_webhook(self, webhook_id: str, event_type: str, case_id: Optional[str], payload: Dict[str, Any]) -> None:
        """Records a processed webhook event to ensure idempotency."""
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO processed_webhooks (webhook_id, event_type, case_id, received_at, payload_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (webhook_id, event_type, case_id, now, json.dumps(payload)),
            )
            conn.commit()

    def is_webhook_processed(self, webhook_id: str) -> bool:
        """Checks if a webhook event has already been processed."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT 1 FROM processed_webhooks WHERE webhook_id = ?",
                (webhook_id,),
            ).fetchone()
            return row is not None

    def save_learning_bucket(self, failure_class: str, strategy: str, sample_count: int, success_count: int, total_recovered: float, total_expected: float) -> None:
        """Persists aggregate Bayesian learning stats for a failure class / strategy pair."""
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO strategy_learning_stats
                (failure_class, strategy, sample_count, success_count, total_recovered_amount, total_expected_value, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (failure_class.upper(), strategy.upper(), sample_count, success_count, total_recovered, total_expected, now),
            )
            conn.commit()

    def load_all_learning_buckets(self) -> List[Dict[str, Any]]:
        """Loads all persisted strategy learning statistics."""
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM strategy_learning_stats").fetchall()
            return [dict(r) for r in rows]

    def get_next_case_id(self) -> str:
        """Generates the next sequential persistent ID (e.g. RACE-CUSTOM-0001)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT case_id FROM custom_cases WHERE case_id LIKE 'RACE-CUSTOM-%'")
            rows = cursor.fetchall()
            max_num = 0
            for r in rows:
                c_id = r["case_id"]
                try:
                    num = int(c_id.split("-")[-1])
                    if num > max_num:
                        max_num = num
                except (ValueError, IndexError):
                    continue
            return f"RACE-CUSTOM-{max_num + 1:04d}"

    def save_case(
        self,
        event: RevenueEvent,
        ground_truth: CaseGroundTruth,
        processed_result: Dict[str, Any],
        audit_trail: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Saves or updates a custom case in the database."""
        now = datetime.now(timezone.utc).isoformat()
        audit_json = json.dumps(audit_trail or [])
        fc_str = event.failure_class.value if hasattr(event.failure_class, "value") else str(event.failure_class)

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO custom_cases (
                    case_id, source, created_at, updated_at, amount, currency,
                    failure_class, failure_reason, payment_method, gateway_route_health,
                    customer_recovery_history_rate, customer_opted_out, retry_count,
                    time_since_failure_minutes, merchant_id, customer_id, payment_id,
                    order_id, current_state, selected_strategy, recovered_amount,
                    is_recovered, is_escalated, is_stopped, raw_event_json,
                    ground_truth_json, audit_trail_json
                ) VALUES (
                    ?, 'CUSTOM', ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?
                )
                """,
                (
                    ground_truth.case_id,
                    now,
                    now,
                    event.amount,
                    event.currency,
                    fc_str,
                    event.failure_reason,
                    event.payment_method,
                    event.gateway_route_health,
                    event.customer_recovery_history_rate,
                    1 if event.customer_opted_out else 0,
                    event.retry_count,
                    event.time_since_failure_minutes,
                    event.merchant_id,
                    event.customer_id,
                    event.payment_id or f"pay_{ground_truth.case_id}",
                    event.order_id or f"ord_{ground_truth.case_id}",
                    processed_result.get("final_state", "AT_RISK"),
                    processed_result.get("selected_strategy", "N/A"),
                    float(processed_result.get("recovered_amount", 0.0)),
                    1 if processed_result.get("is_recovered") else 0,
                    1 if processed_result.get("is_escalated") else 0,
                    1 if processed_result.get("is_stopped") else 0,
                    event.model_dump_json(),
                    ground_truth.model_dump_json(),
                    audit_json,
                ),
            )
            conn.commit()

        return self.get_case(ground_truth.case_id) or {}

    def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single custom case by case_id."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM custom_cases WHERE case_id = ?", (case_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_dict(row)

    def list_cases(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Lists all stored custom cases sorted by creation time descending."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM custom_cases ORDER BY created_at DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [self._row_to_dict(r) for r in rows]

    def update_case_outcome(
        self,
        case_id: str,
        final_state: str,
        recovered_amount: float,
        is_recovered: bool,
        is_escalated: bool,
        is_stopped: bool,
        selected_strategy: str,
        audit_trail: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Updates lifecycle outcome fields for an executed custom case."""
        now = datetime.now(timezone.utc).isoformat()
        audit_json = json.dumps(audit_trail or [])
        with self._get_connection() as conn:
            conn.execute(
                """
                UPDATE custom_cases
                SET updated_at = ?,
                    current_state = ?,
                    recovered_amount = ?,
                    is_recovered = ?,
                    is_escalated = ?,
                    is_stopped = ?,
                    selected_strategy = ?,
                    audit_trail_json = ?
                WHERE case_id = ?
                """,
                (
                    now,
                    final_state,
                    recovered_amount,
                    1 if is_recovered else 0,
                    1 if is_escalated else 0,
                    1 if is_stopped else 0,
                    selected_strategy,
                    audit_json,
                    case_id,
                ),
            )
            conn.commit()

    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Converts an SQLite row to a standard structured dictionary."""
        return {
            "case_id": row["case_id"],
            "source": row["source"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "amount": float(row["amount"]),
            "currency": row["currency"],
            "failure_class": row["failure_class"],
            "failure_reason": row["failure_reason"],
            "payment_method": row["payment_method"],
            "gateway_route_health": row["gateway_route_health"],
            "customer_recovery_history_rate": float(row["customer_recovery_history_rate"]),
            "customer_opted_out": bool(row["customer_opted_out"]),
            "retry_count": int(row["retry_count"]),
            "time_since_failure_minutes": float(row["time_since_failure_minutes"]),
            "merchant_id": row["merchant_id"],
            "customer_id": row["customer_id"],
            "payment_id": row["payment_id"],
            "order_id": row["order_id"],
            "current_state": row["current_state"],
            "selected_strategy": row["selected_strategy"],
            "recovered_amount": float(row["recovered_amount"]),
            "is_recovered": bool(row["is_recovered"]),
            "is_escalated": bool(row["is_escalated"]),
            "is_stopped": bool(row["is_stopped"]),
            "raw_event": json.loads(row["raw_event_json"]),
            "ground_truth": json.loads(row["ground_truth_json"]),
            "audit_trail": json.loads(row["audit_trail_json"]),
        }


def build_custom_ground_truth(event: RevenueEvent, case_id: str) -> CaseGroundTruth:
    """Constructs ground truth counterfactuals and policies for a user-created case."""
    amt = event.amount
    fc = event.failure_class if isinstance(event.failure_class, FailureClass) else FailureClass(event.failure_class)
    gw_health = event.gateway_route_health.upper()
    is_opted_out = event.customer_opted_out

    # Default baseline counterfactual outcome dictionary
    cf_outcomes = {
        "RETRY_NOW": {"outcome": "FAILED", "recovered_amount": 0.0},
        "RETRY_LATER": {"outcome": "FAILED", "recovered_amount": 0.0},
        "REMINDER_THEN_RETRY": {"outcome": "FAILED", "recovered_amount": 0.0},
        "HUMAN_ESCALATION": {"outcome": "FAILED", "recovered_amount": 0.0},
        "STOP": {"outcome": "STOPPED", "recovered_amount": 0.0},
    }

    if is_opted_out or fc == FailureClass.FRAUD_SUSPECTED or fc == FailureClass.EXPIRED_CARD:
        return CaseGroundTruth(
            case_id=case_id,
            event_id=event.event_id,
            true_revenue_at_risk=amt,
            true_recoverable_amount=0.0,
            true_optimal_strategy=RecoveryStrategy.STOP,
            true_counterfactual_outcomes=cf_outcomes,
            allowed_actions=[RecoveryStrategy.STOP],
            requires_escalation=False,
            is_policy_blocked=True,
            scenario_description=f"Unrecoverable or policy-blocked case: {fc.value}",
        )

    if amt > 50000.0:
        cf_outcomes["HUMAN_ESCALATION"] = {"outcome": "RECOVERED", "recovered_amount": amt}
        return CaseGroundTruth(
            case_id=case_id,
            event_id=event.event_id,
            true_revenue_at_risk=amt,
            true_recoverable_amount=amt,
            true_optimal_strategy=RecoveryStrategy.HUMAN_ESCALATION,
            true_counterfactual_outcomes=cf_outcomes,
            allowed_actions=[RecoveryStrategy.HUMAN_ESCALATION, RecoveryStrategy.STOP],
            requires_escalation=True,
            is_policy_blocked=False,
            scenario_description="High-value transaction requiring human escalation",
        )

    if fc == FailureClass.TEMPORARY_NETWORK:
        if gw_health == "UP":
            cf_outcomes["RETRY_NOW"] = {"outcome": "RECOVERED", "recovered_amount": amt}
            cf_outcomes["RETRY_LATER"] = {"outcome": "RECOVERED", "recovered_amount": amt}
            optimal = RecoveryStrategy.RETRY_NOW
        else:
            cf_outcomes["RETRY_LATER"] = {"outcome": "RECOVERED", "recovered_amount": amt}
            optimal = RecoveryStrategy.RETRY_LATER
        allowed = [RecoveryStrategy.RETRY_NOW, RecoveryStrategy.RETRY_LATER, RecoveryStrategy.STOP]
    elif fc == FailureClass.GATEWAY_DEGRADATION:
        cf_outcomes["RETRY_LATER"] = {"outcome": "RECOVERED", "recovered_amount": amt}
        optimal = RecoveryStrategy.RETRY_LATER
        allowed = [RecoveryStrategy.RETRY_LATER, RecoveryStrategy.STOP]
    elif fc in (FailureClass.INSUFFICIENT_FUNDS, FailureClass.AUTH_REQUIRED, FailureClass.CUSTOMER_ABANDONMENT):
        cf_outcomes["REMINDER_THEN_RETRY"] = {"outcome": "RECOVERED", "recovered_amount": amt}
        optimal = RecoveryStrategy.REMINDER_THEN_RETRY
        allowed = [RecoveryStrategy.REMINDER_THEN_RETRY, RecoveryStrategy.STOP]
    else:
        cf_outcomes["RETRY_LATER"] = {"outcome": "RECOVERED", "recovered_amount": amt}
        optimal = RecoveryStrategy.RETRY_LATER
        allowed = [RecoveryStrategy.RETRY_NOW, RecoveryStrategy.RETRY_LATER, RecoveryStrategy.STOP]

    return CaseGroundTruth(
        case_id=case_id,
        event_id=event.event_id,
        true_revenue_at_risk=amt,
        true_recoverable_amount=amt,
        true_optimal_strategy=optimal,
        true_counterfactual_outcomes=cf_outcomes,
        allowed_actions=allowed,
        requires_escalation=False,
        is_policy_blocked=False,
        scenario_description=f"Custom simulation scenario for {fc.value}",
    )
