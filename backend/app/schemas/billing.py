"""账单相关 Schema"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class MonthlyBillResponse(BaseModel):
    id: str
    user_id: str
    year: int
    month: int
    total_amount: Decimal
    compute_fee: Decimal
    energy_fee: Decimal
    network_fee: Decimal
    storage_fee: Decimal
    green_cert_discount: Decimal
    actual_pay: Decimal
    order_count: int
    status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class InvoiceCreateRequest(BaseModel):
    type: str = "normal"
    title: str
    tax_no: str
    address: Optional[str] = None
    phone: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None

class InvoiceResponse(BaseModel):
    id: str
    bill_id: str
    type: str
    title: str
    amount: Decimal
    status: str
    issued_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ReconciliationResponse(BaseModel):
    total_orders: int
    total_amount: Decimal
    total_payments: Decimal
    total_refunds: Decimal
    discrepancy: Decimal
    details: list
