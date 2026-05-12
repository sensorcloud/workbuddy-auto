"""
用户数据模型
"""
from sqlalchemy import Column, String, Boolean
from app.models.base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="consumer")  # consumer, provider, admin
    is_active = Column(Boolean, default=True)
