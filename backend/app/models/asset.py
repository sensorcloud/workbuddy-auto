"""
资产数据模型
"""
from sqlalchemy import Column, String, Float, Boolean, JSON, Integer, DateTime
from app.models.base import Base
from datetime import datetime

class Asset(Base):
    __tablename__ = "assets"

    id = Column(String, primary_key=True, index=True)
    owner_id = Column(String, index=True, nullable=False)
    type = Column(String, nullable=False)  # compute, storage
    name = Column(String)  # 资产名称（如 "A100 8卡 GPU集群 #1"）
    spec = Column(JSON)  # GPU规格、存储规格等
    pricing = Column(JSON)  # 定价信息
    energy_profile = Column(JSON)  # 能源配置
    location = Column(JSON)  # 位置信息
    status = Column(String, default="online")  # online, offline, maintenance
    availability_sla = Column(Float, default=99.9)  # SLA 可用性
    rating = Column(Float, default=0)  # 平均评分
    total_orders = Column(Integer, default=0)  # 累计订单数
    pricing_type = Column(String, default="fixed")  # fixed / spot / auction
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
