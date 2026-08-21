"""Immutable audit ledger recording structured financial and recovery decisions."""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from backend.audit.models import AuditRecord


class AuditLedger:
    """In-memory and file-backed append-only audit ledger."""

    def __init__(self, persistence_path: Optional[Path] = None):
        self._records: List[AuditRecord] = []
        self.persistence_path = persistence_path

    def record_entry(self, entry: AuditRecord) -> None:
        """Appends a new audit record to the ledger."""
        self._records.append(entry)
        if self.persistence_path:
            self.persistence_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.persistence_path, "a", encoding="utf-8") as f:
                f.write(entry.model_dump_json() + "\n")

    def get_records_for_case(self, case_id: str) -> List[AuditRecord]:
        """Retrieves all chronological audit events for a given recovery case."""
        return [r for r in self._records if r.case_id == case_id]

    def get_all_records(self) -> List[AuditRecord]:
        """Returns all records in the ledger."""
        return list(self._records)

    def generate_human_explanation(self, record: AuditRecord) -> str:
        """Generates a human-readable explanation derived strictly from structured decision data."""
        return (
            f"Case {record.case_id}: Revenue at risk of INR {record.revenue_at_risk:.2f} due to "
            f"{record.failure_class} ({record.failure_reason}). "
            f"Evaluated candidates {record.candidate_actions}. "
            f"Selected {record.selected_action} because {record.selection_reason}. "
            f"Policy gate returned {record.policy_decision}. "
            f"Action status: {record.action_status} (Ref: {record.request_reference or 'N/A'}). "
            f"Outcome: {record.outcome or 'PENDING'} with INR {record.recovered_amount:.2f} captured."
        )
