"""Razorpay test-mode API client supporting real test mode and deterministic test adapter."""

import os
import time
import logging
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

logger = logging.getLogger("race.integrations.razorpay")


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
        self.key_id = key_id or os.getenv("RAZORPAY_KEY_ID", "")
        self.key_secret = key_secret or os.getenv("RAZORPAY_KEY_SECRET", "")
        self.simulate_timeout = simulate_timeout
        
        # If credentials are mock/placeholder/empty or explicitly requested, use deterministic adapter
        if use_mock_adapter is not None:
            self.use_mock_adapter = use_mock_adapter
        else:
            is_placeholder = (
                not self.key_id
                or not self.key_secret
                or "placeholder" in self.key_id.lower()
                or "mock" in self.key_id.lower()
                or "placeholder" in self.key_secret.lower()
                or "mock" in self.key_secret.lower()
            )
            self.use_mock_adapter = is_placeholder

        logger.info(f"Razorpay integration mode initialized: {self.integration_mode}")

    @property
    def integration_mode(self) -> str:
        """Returns runtime environment mode: TEST_MODE or MOCK."""
        return "MOCK" if self.use_mock_adapter else "TEST_MODE"

    @property
    def key_id_prefix(self) -> str:
        """Returns safe non-secret prefix of Key ID for UI/diagnostics."""
        if not self.key_id or self.use_mock_adapter:
            return "rzp_test_mock"
        return self.key_id[:12] + "..." if len(self.key_id) > 12 else self.key_id

    def create_order(self, request: RazorpayOrderRequest) -> RazorpayOrderResponse:
        """Creates a test-mode order on Razorpay."""
        if self.simulate_timeout:
            logger.warning("Simulated upstream timeout triggered for create_order")
            raise RazorpayTimeoutError("Upstream timeout while creating order on Razorpay")

        if self.use_mock_adapter:
            order_id = f"order_mock_{int(time.time() * 1000)}"
            logger.info(f"[MOCK] Created mock order {order_id} for amount {request.amount} paise")
            return RazorpayOrderResponse(
                id=order_id,
                entity="order",
                amount=request.amount,
                currency=request.currency,
                status="created",
                receipt=request.receipt,
                created_at=int(time.time()),
            )

        # Real Test Mode API call with basic auth
        logger.info(f"[TEST_MODE] Dispatching real order creation to Razorpay for receipt {request.receipt}")
        try:
            with httpx.Client(base_url=self.BASE_URL, timeout=8.0) as client:
                res = client.post("/orders", json=request.model_dump(), auth=(self.key_id, self.key_secret))
                if res.status_code != 200:
                    err_msg = res.text
                    logger.error(f"[TEST_MODE] Razorpay order creation failed with status {res.status_code}")
                    raise RazorpayAPIError(f"Failed to create order: {err_msg}", status_code=res.status_code)
                data = res.json()
                logger.info(f"[TEST_MODE] Successfully created Razorpay order {data.get('id')} with status {data.get('status')}")
                return RazorpayOrderResponse.model_validate(data)
        except httpx.TimeoutException:
            logger.error("[TEST_MODE] Gateway timeout while communicating with Razorpay Orders API")
            raise RazorpayTimeoutError("Upstream timeout while creating order on Razorpay")
        except Exception as e:
            if isinstance(e, (RazorpayAPIError, RazorpayTimeoutError)):
                raise
            logger.error(f"[TEST_MODE] Unexpected error during Razorpay order creation: {type(e).__name__}")
            raise RazorpayAPIError(f"Razorpay communication error: {str(e)}")

    def create_payment_link(self, request: RazorpayPaymentLinkRequest) -> RazorpayPaymentLinkResponse:
        """Creates a test-mode payment link on Razorpay."""
        if self.simulate_timeout:
            logger.warning("Simulated upstream timeout triggered for create_payment_link")
            raise RazorpayTimeoutError("Upstream timeout while creating payment link on Razorpay")

        if self.use_mock_adapter:
            link_id = f"plink_mock_{int(time.time() * 1000)}"
            logger.info(f"[MOCK] Created mock payment link {link_id}")
            return RazorpayPaymentLinkResponse(
                id=link_id,
                short_url=f"https://rzp.io/i/test_{link_id}",
                status="created",
                amount=request.amount,
                currency=request.currency,
                created_at=int(time.time()),
            )

        logger.info(f"[TEST_MODE] Dispatching payment link creation to Razorpay for amount {request.amount} paise")
        try:
            with httpx.Client(base_url=self.BASE_URL, timeout=8.0) as client:
                res = client.post("/payment_links", json=request.model_dump(), auth=(self.key_id, self.key_secret))
                if res.status_code != 200:
                    err_msg = res.text
                    logger.error(f"[TEST_MODE] Razorpay payment link creation failed with status {res.status_code}")
                    raise RazorpayAPIError(f"Failed to create payment link: {err_msg}", status_code=res.status_code)
                data = res.json()
                logger.info(f"[TEST_MODE] Successfully created Razorpay payment link {data.get('id')}")
                return RazorpayPaymentLinkResponse.model_validate(data)
        except httpx.TimeoutException:
            logger.error("[TEST_MODE] Gateway timeout while creating payment link on Razorpay")
            raise RazorpayTimeoutError("Upstream timeout while creating payment link on Razorpay")
        except Exception as e:
            if isinstance(e, (RazorpayAPIError, RazorpayTimeoutError)):
                raise
            logger.error(f"[TEST_MODE] Unexpected error during Razorpay payment link creation: {type(e).__name__}")
            raise RazorpayAPIError(f"Razorpay payment link error: {str(e)}")

    def fetch_payment(self, payment_id: str) -> RazorpayPaymentStatusResponse:
        """Fetches payment status from Razorpay for authoritative outcome verification."""
        if self.simulate_timeout:
            logger.warning("Simulated upstream timeout triggered for fetch_payment")
            raise RazorpayTimeoutError("Upstream timeout while fetching payment on Razorpay")

        if self.use_mock_adapter:
            logger.info(f"[MOCK] Returning verified payment status for {payment_id}")
            return RazorpayPaymentStatusResponse(
                id=payment_id,
                entity="payment",
                amount=500000,
                currency="INR",
                status="captured",
                method="upi",
            )

        logger.info(f"[TEST_MODE] Fetching payment details from Razorpay for {payment_id}")
        try:
            with httpx.Client(base_url=self.BASE_URL, timeout=8.0) as client:
                res = client.get(f"/payments/{payment_id}", auth=(self.key_id, self.key_secret))
                if res.status_code != 200:
                    err_msg = res.text
                    logger.error(f"[TEST_MODE] Razorpay payment fetch failed with status {res.status_code}")
                    raise RazorpayAPIError(f"Failed to fetch payment: {err_msg}", status_code=res.status_code)
                data = res.json()
                logger.info(f"[TEST_MODE] Successfully fetched payment {payment_id}: status={data.get('status')}")
                return RazorpayPaymentStatusResponse.model_validate(data)
        except httpx.TimeoutException:
            logger.error(f"[TEST_MODE] Gateway timeout while fetching payment {payment_id}")
            raise RazorpayTimeoutError("Upstream timeout while fetching payment on Razorpay")
        except Exception as e:
            if isinstance(e, (RazorpayAPIError, RazorpayTimeoutError)):
                raise
            logger.error(f"[TEST_MODE] Unexpected error during Razorpay payment fetch: {type(e).__name__}")
            raise RazorpayAPIError(f"Razorpay payment query error: {str(e)}")

