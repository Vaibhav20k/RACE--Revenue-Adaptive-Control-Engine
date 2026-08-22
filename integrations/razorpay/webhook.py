"""Razorpay Webhook verification and event handler."""

import os
import hmac
import hashlib
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger("race.integrations.razorpay.webhook")


class RazorpayWebhookHandler:
    """Handles HMAC-SHA256 signature verification and parsing for Razorpay webhooks."""

    def __init__(self, webhook_secret: Optional[str] = None):
        self.secret = webhook_secret or os.getenv("RAZORPAY_WEBHOOK_SECRET", "rzp_test_whsec_race_2026")

    def verify_signature(self, raw_body: bytes, signature: Optional[str]) -> bool:
        """Verifies that the incoming webhook payload was signed with the expected secret."""
        if not signature or not self.secret:
            logger.warning("[Webhook] Missing webhook signature or secret")
            return False

        try:
            computed = hmac.new(
                self.secret.encode("utf-8"),
                raw_body,
                hashlib.sha256,
            ).hexdigest()
            is_valid = hmac.compare_digest(computed, signature)
            if not is_valid:
                logger.warning("[Webhook] HMAC-SHA256 signature verification failed")
            return is_valid
        except Exception as e:
            logger.error(f"[Webhook] Signature computation error: {type(e).__name__}")
            return False

    def parse_event(self, payload: Dict[str, Any]) -> Tuple[str, Dict[str, Any], Optional[str]]:
        """Parses webhook event type, entity payload, and correlated case/order receipt."""
        event_type = payload.get("event", "unknown")
        contains = payload.get("contains", [])
        
        entity_data: Dict[str, Any] = {}
        if "payment" in contains and "payment" in payload.get("payload", {}):
            entity_data = payload["payload"]["payment"].get("entity", {})
        elif "order" in contains and "order" in payload.get("payload", {}):
            entity_data = payload["payload"]["order"].get("entity", {})
        elif "payload" in payload:
            first_key = next(iter(payload["payload"]), None)
            if first_key:
                entity_data = payload["payload"][first_key].get("entity", {})

        # Extract correlated reference from notes or receipt
        notes = entity_data.get("notes", {})
        case_id = notes.get("case_id") or notes.get("race_case_id")
        receipt = entity_data.get("receipt")

        return event_type, entity_data, case_id or receipt
