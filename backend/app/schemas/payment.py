"""支付相关 Schema"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

class PaymentCreate(BaseModel):
    order_id: str
    channel: str = "balance"  # balance / alipay / wechat / bankcard

class PaymentResponse(BaseModel):
    id: str
    order_id: str
    user_id: str
    channel: str
    amount: Decimal
    status: str
    trade_no: Optional[str] = None
    paid_at: Optional[datetime] = None
    payment_url: Optional[str] = None
    qr_code: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PaymentCallback(BaseModel):
    status: str  # success / failed
    trade_no: str
    amount: Decimal

class PaymentCallbackResult(BaseModel):
    success: bool
    message: str
