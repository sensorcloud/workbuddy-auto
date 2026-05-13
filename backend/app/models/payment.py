"""支付记录模型"""
from sqlalchemy import Column, String, Numeric, DateTime
from app.models.base import Base
from datetime import datetime

class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, index=True)
    order_id = Column(String, index=True, nullable=True)  # 钱包充值时为 NULL
    user_id = Column(String, index=True, nullable=False)
    channel = Column(String, nullable=False)  # balance / alipay / wechat / bankcard
    amount = Column(Numeric(12, 2), nullable=False)
    status = Column(String, default="pending")  # pending / success / failed / refunded / partial_refunded
    trade_no = Column(String, index=True)  # 第三方交易号
    paid_at = Column(DateTime)
    callback_data = Column(String)  # 回调原始数据(JSON string)
    refund_amount = Column(Numeric(12, 2), default=0)
    refund_reason = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
