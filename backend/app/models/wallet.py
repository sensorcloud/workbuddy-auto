"""钱包与交易流水模型"""
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey
from app.models.base import Base
from datetime import datetime

class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), unique=True, index=True, nullable=False)
    balance = Column(Numeric(12, 2), default=0, nullable=False)
    frozen = Column(Numeric(12, 2), default=0, nullable=False)
    total_recharge = Column(Numeric(12, 2), default=0)
    total_withdraw = Column(Numeric(12, 2), default=0)
    total_consume = Column(Numeric(12, 2), default=0)
    credit_limit = Column(Numeric(12, 2), default=0)
    low_balance_alert = Column(Numeric(12, 2), default=100)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, index=True)
    wallet_id = Column(String, ForeignKey("wallets.id"), index=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    type = Column(String, nullable=False)  # recharge / consume / withdraw / refund / freeze / unfreeze
    amount = Column(Numeric(12, 2), nullable=False)
    balance_after = Column(Numeric(12, 2), nullable=False)
    order_id = Column(String, ForeignKey("orders.id"), index=True)
    payment_id = Column(String, ForeignKey("payments.id"))
    remark = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
