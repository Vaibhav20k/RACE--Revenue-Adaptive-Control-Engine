"""Razorpay integration specific exceptions."""

from backend.core.errors import RACEError


class RazorpayAPIError(RACEError):
    """Raised when Razorpay API returns an error response."""
    def __init__(self, message: str, status_code: int = 400, error_code: str = "BAD_REQUEST_ERROR"):
        super().__init__(message, code=error_code)
        self.status_code = status_code


class RazorpayTimeoutError(RazorpayAPIError):
    """Raised when upstream Razorpay API request times out."""
    def __init__(self, message: str = "Razorpay upstream request timed out"):
        super().__init__(message, status_code=504, error_code="GATEWAY_TIMEOUT")
