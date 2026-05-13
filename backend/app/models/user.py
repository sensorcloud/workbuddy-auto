"""
用户数据模型
"""
from sqlalchemy import Column, String, Boolean, DateTime
from app.models.base import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="consumer")  # consumer, provider, admin
    is_active = Column(Boolean, default=True)
    phone = Column(String)  # 手机号
    company_name = Column(String)  # 公司名称
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
