"""Spot 配置模型（P1 先建表）"""
from sqlalchemy import Column, String, Numeric, Integer, ForeignKey, DateTime
from app.models.base import Base
from datetime import datetime

class SpotConfig(Base):
    __tablename__ = "spot_configs"

    id = Column(String, primary_key=True, index=True)
    asset_id = Column(String, ForeignKey("assets.id"), unique=True, index=True, nullable=False)
    min_price = Column(Numeric(12, 2), nullable=False)
    max_price = Column(Numeric(12, 2), nullable=False)
    current_price = Column(Numeric(12, 2))
    interruptible = Column(Integer, default=1)
    notification_minutes = Column(Integer, default=5)
    status = Column(String, default="available")  # available / allocated / maintenance
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
