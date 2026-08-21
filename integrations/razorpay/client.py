"""Razorpay test-mode API client supporting real test mode and deterministic test adapter."""

import os
import time
import httpx
from typing import Optional, Dict, Any
from integrations.razorpay.schemas import (
    RazorpayOrderRequest,
    RazorpayOrderResponse,
    RazorpayPaymentLinkRequest,
    RazorpayPaymentLinkResponse,
    RazorpayPaymentStatusResponse,
)
from integrations.razorpay.errors import RazorpayAPIError, RazorpayTimeoutError


class RazorpayTestClient:
    """Client for interacting with Razorpay Test Mode APIs."""

    BASE_URL = "https://api.razorpay.com/v1"

    def __init__(
        self,
        key_id: Optional[str] = None,
        key_secret: Optional[str] = None,
        simulate_timeout: bool = False,
        use_mock_adapter: Optional[bool] = None,
    ):
        self.key_id = key_id or os.getenv("RAZORPAY_KEY_ID", "rzp_test_mock_key")
        self.key_secret = key_secret or os.getenv("RAZORPAY_KEY_SECRET", "rzp_test_mock_secret")
        self.simulate_timeout = simulate_timeout
        
        # If credentials are mock/placeholder or explicitly requested, use deterministic adapter
        if use_mock_adapter is not None:
            self.use_mock_adapter = use_mock_adapter
        else:
            self.use_mock_adapter = "placeholder" in self.key_id.lower() or "mock" in self.key_id.lower()

    def create_order(self, request: RazorpayOrderRequest) -> RazorpayOrderResponse:
        """Creates a test-mode order."""
        if self.simulate_timeout:
            raise RazorpayTimeoutError("Upstream timeout while creating order on Razorpay")

        if self.use_mock_adapter:
            order_id = f"order_{int(time.time() * 1000)}"
            return RazorpayOrderResponse(
                id=order_id,
                entity="order",
                amount=request.amount,
                currency=request.currency,
                status="created",
                receipt=request.receipt,
                created_at=int(time.time()),
            )

        # Real API call with basic auth
        try:
            with httpx.Client(base_url=self.BASE_URL, timeout=5.0) as client:
                res = client.post("/orders", json=request.model_dump(), auth=(self.key_id, self.key_secret))
                if res.status_code != 200:
                    raise RazorpayAPIError(f"Failed to create order: {res.text}", status_code=res.status_code)
                return RazorpayOrderResponse.model_validate(res.json())
        except httpx.TimeoutException:
            raise RazorpayTimeoutError()
        except Exception as e:
            if isinstance(e, RazorpayAPIError):
                raise
            raise RazorpayAPIError(str(e))

    def create_payment_link(self, request: RazorpayPaymentLinkRequest) -> RazorpayPaymentLinkResponse:
        """Creates a test-mode payment link / reminder."""
        if self.simulate_timeout:
            raise RazorpayTimeoutError("Upstream timeout while creating payment link on Razorpay")

        if self.use_mock_adapter:
            link_id = f"plink_{int(time.time() * 1000)}"
            return RazorpayPaymentLinkResponse(
                id=link_id,
                short_url=f"https://rzp.io/i/test_{link_id}",
                status="created",
                amount=request.amount,
                currency=request.currency,
                created_at=int(time.time()),
            )

        try:
            with httpx.Client(base_url=self.BASE_URL, timeout=5.0) as client:
                res = client.post("/payment_links", json=request.model_dump(), auth=(self.key_id, self.key_secret))
                if res.status_code != 200:
                    raise RazorpayAPIError(f"Failed to create payment link: {res.text}", status_code=res.status_code)
                return RazorpayPaymentLinkResponse.model_validate(res.json())
        except httpx.TimeoutException:
            raise RazorpayTimeoutError()
        except Exception as e:
            if isinstance(e, RazorpayAPIError):
                raise
            raise RazorpayAPIError(str(e))

    def fetch_payment(self, payment_id: str) -> RazorpayPaymentStatusResponse:
        """Fetches payment status for state reconciliation."""
        if self.simulate_timeout:
            raise RazorpayTimeoutError("Upstream timeout while fetching payment on Razorpay")

        if self.use_mock_adapter:
            return RazorpayPaymentStatusResponse(
                id=payment_id,
                entity="payment",
                amount=500000,
                currency="INR",
                status="captured",
                method="upi",
            )

        try:
            with httpx.Client(base_url=self.BASE_URL, timeout=5.0) as client:
                res = client.get(f"/payments/{payment_id}", auth=(self.key_id, self.key_secret))
                if res.status_code != 200:
                    raise RazorpayAPIError(f"Failed to fetch payment: {res.text}", status_code=res.status_code)
                return RazorpayPaymentStatusResponse.model_validate(res.json())
        except httpx.TimeoutException:
            raise RazorpayTimeoutError()
        except Exception as e:
            if isinstance(e, RazorpayAPIError):
                raise
            raise RazorpayAPIError(str(e))
