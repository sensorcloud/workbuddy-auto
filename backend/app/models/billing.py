"""月度账单与发票模型"""
from sqlalchemy import Column, String, Numeric, Integer, DateTime, ForeignKey
from app.models.base import Base
from datetime import datetime

class MonthlyBill(Base):
    __tablename__ = "monthly_bills"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    total_amount = Column(Numeric(12, 2), default=0)
    compute_fee = Column(Numeric(12, 2), default=0)
    energy_fee = Column(Numeric(12, 2), default=0)
    network_fee = Column(Numeric(12, 2), default=0)
    storage_fee = Column(Numeric(12, 2), default=0)
    green_cert_discount = Column(Numeric(12, 2), default=0)
    actual_pay = Column(Numeric(12, 2), default=0)
    order_count = Column(Integer, default=0)
    status = Column(String, default="generated")  # generated / paid / overdue
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(String, primary_key=True, index=True)
    bill_id = Column(String, ForeignKey("monthly_bills.id"), index=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    type = Column(String, default="normal")  # normal / vat_special / vat_digital
    title = Column(String, nullable=False)
    tax_no = Column(String, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    status = Column(String, default="pending")  # pending / issued / sent / failed
    issued_at = Column(DateTime)
    sent_at = Column(DateTime)
    file_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
