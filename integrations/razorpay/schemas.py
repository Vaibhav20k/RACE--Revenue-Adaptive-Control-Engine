"""Request and response schemas for Razorpay test-mode operations."""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class RazorpayOrderRequest(BaseModel):
    amount: int = Field(gt=0, description="Amount in paise (1 INR = 100 paise)")
    currency: str = "INR"
    receipt: str
    notes: Dict[str, Any] = Field(default_factory=dict)


class RazorpayOrderResponse(BaseModel):
    id: str
    entity: str = "order"
    amount: int
    currency: str
    status: str
    receipt: Optional[str] = None
    created_at: int


class RazorpayPaymentLinkRequest(BaseModel):
    amount: int = Field(gt=0, description="Amount in paise")
    currency: str = "INR"
    description: str
    customer: Dict[str, str]
    notify: Dict[str, bool] = Field(default_factory=lambda: {"sms": True, "email": True})
    reminder_enable: bool = True
    notes: Dict[str, Any] = Field(default_factory=dict)


class RazorpayPaymentLinkResponse(BaseModel):
    id: str
    short_url: str
    status: str
    amount: int
    currency: str
    created_at: int


class RazorpayPaymentStatusResponse(BaseModel):
    id: str
    entity: str = "payment"
    amount: int
    currency: str
    status: str  # "captured", "authorized", "failed", "created"
    order_id: Optional[str] = None
    method: str
    error_code: Optional[str] = None
    error_description: Optional[str] = None
