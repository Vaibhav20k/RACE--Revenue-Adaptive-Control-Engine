"""Idempotency manager preventing duplicate action execution across distributed retries."""

import hashlib
from datetime import datetime, timezone
from typing import Dict, Optional, Any
from pydantic import BaseModel, Field
from backend.core.errors import IdempotencyConflictError


class IdempotencyEntry(BaseModel):
    idempotency_key: str
    case_id: str
    action_type: str
    attempt_number: int
    action_status: str  # "IN_FLIGHT", "COMPLETED", "FAILED"
    request_reference: Optional[str] = None
    result_reference: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class IdempotencyManager:
    """Enforces unique execution identity for financial actions."""

    def __init__(self):
        self._entries: Dict[str, IdempotencyEntry] = {}

    @staticmethod
    def generate_key(
        merchant_id: str,
        customer_id: str,
        payment_id: str,
        action_type: str,
        attempt_number: int,
    ) -> str:
        """Generates a deterministic SHA-256 idempotency key."""
        raw = f"{merchant_id}:{customer_id}:{payment_id}:{action_type}:{attempt_number}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def acquire_lock(
        self,
        idempotency_key: str,
        case_id: str,
        action_type: str,
        attempt_number: int,
    ) -> IdempotencyEntry:
        """Acquires execution lease or raises IdempotencyConflictError if duplicate."""
        if idempotency_key in self._entries:
            existing = self._entries[idempotency_key]
            raise IdempotencyConflictError(
                f"Duplicate action detected for key {idempotency_key} (Status: {existing.action_status})",
                idempotency_key=idempotency_key,
            )

        entry = IdempotencyEntry(
            idempotency_key=idempotency_key,
            case_id=case_id,
            action_type=action_type,
            attempt_number=attempt_number,
            action_status="IN_FLIGHT",
        )
        self._entries[idempotency_key] = entry
        return entry

    def record_completion(
        self,
        idempotency_key: str,
        request_reference: Optional[str],
        result_reference: Optional[str],
        status: str = "COMPLETED",
    ) -> None:
        """Updates idempotency record upon action completion."""
        if idempotency_key in self._entries:
            entry = self._entries[idempotency_key]
            self._entries[idempotency_key] = IdempotencyEntry(
                idempotency_key=entry.idempotency_key,
                case_id=entry.case_id,
                action_type=entry.action_type,
                attempt_number=entry.attempt_number,
                action_status=status,
                request_reference=request_reference,
                result_reference=result_reference,
            )

    def get_entry(self, idempotency_key: str) -> Optional[IdempotencyEntry]:
        """Retrieves stored entry by key."""
        return self._entries.get(idempotency_key)
