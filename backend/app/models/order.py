"""
订单数据模型
"""
from sqlalchemy import Column, String, Float, JSON
from app.models.base import Base

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    asset_id = Column(String, index=True, nullable=False)
    status = Column(String, default="pending")  # pending, running, completed, cancelled, failed
    compute_cost = Column(Float, default=0.0)
    energy_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    selected_quote = Column(JSON)  # 选中的报价方案
    container_image = Column(String)
    dataset_location = Column(String)
    task_type = Column(String)
    estimated_duration_hours = Column(Float)
