"""Standardized structured exceptions for RACE."""


class RACEError(Exception):
    """Base exception for RACE."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        super().__init__(message)
        self.code = code
        self.message = message


class PolicyViolationError(RACEError):
    """Raised when an action violates safety or business policy."""
    def __init__(self, message: str, rule: str):
        super().__init__(message, code="POLICY_VIOLATION")
        self.rule = rule


class IdempotencyConflictError(RACEError):
    """Raised when duplicate action execution is attempted."""
    def __init__(self, message: str, idempotency_key: str):
        super().__init__(message, code="IDEMPOTENCY_CONFLICT")
        self.idempotency_key = idempotency_key


class GatewayExecutionError(RACEError):
    """Raised when upstream payment gateway request fails or times out."""
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message, code="GATEWAY_EXECUTION_ERROR")
        self.status_code = status_code
