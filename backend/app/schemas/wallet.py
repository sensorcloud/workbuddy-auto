"""钱包相关 Schema"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

class WalletBalanceResponse(BaseModel):
    balance: Decimal
    frozen: Decimal
    available: Decimal
    total_recharge: Decimal
    total_withdraw: Decimal
    total_consume: Decimal
    credit_limit: Decimal
    low_balance_alert: Decimal

class WalletRechargeRequest(BaseModel):
    amount: Decimal = Field(gt=0)
    channel: str = "alipay"

class WalletWithdrawRequest(BaseModel):
    amount: Decimal = Field(gt=0)
    bank_card: str
    bank_name: str
    account_name: str

class TransactionRecord(BaseModel):
    id: str
    type: str
    amount: Decimal
    balance_after: Decimal
    order_id: Optional[str] = None
    remark: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
