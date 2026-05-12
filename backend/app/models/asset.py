"""
资产数据模型
"""
from sqlalchemy import Column, String, Float, Boolean, JSON
from app.models.base import Base

class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(String, primary_key=True, index=True)
    owner_id = Column(String, index=True, nullable=False)
    type = Column(String, nullable=False)  # compute, storage
    spec = Column(JSON)  # GPU规格、存储规格等
    pricing = Column(JSON)  # 定价信息
    energy_profile = Column(JSON)  # 能源配置
    location = Column(JSON)  # 位置信息
    status = Column(String, default="online")  # online, offline, maintenance
