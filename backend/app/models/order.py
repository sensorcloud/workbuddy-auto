"""
订单数据模型
"""
from sqlalchemy import Column, String, Float, JSON, DateTime, Integer
from app.models.base import Base
from datetime import datetime

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
    payment_id = Column(String)  # 关联支付记录
    paid_at = Column(DateTime)  # 支付时间
    completed_at = Column(DateTime)  # 完成时间
    cancelled_at = Column(DateTime)  # 取消时间
    started_at = Column(DateTime)  # 启动时间
    instance_type = Column(String, default="on_demand")  # on_demand / reserved / spot
    review_score = Column(Integer)  # 综合评分 1-5
    review_text = Column(String)  # 评价内容
    reviewed_at = Column(DateTime)  # 评价时间
    refund_status = Column(String, default="none")  # none / pending / approved / rejected / completed
    refund_amount = Column(Float, default=0.0)
    refund_reason = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
