from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class OrderCreate(BaseModel):
    user_id: Optional[str] = None  # API层从token自动注入
    asset_id: str
    selected_quote: Optional[Dict[str, Any]] = None
    container_image: Optional[str] = None
    dataset_location: Optional[str] = None
    task_type: Optional[str] = None
    estimated_duration_hours: Optional[float] = None


class OrderResponse(BaseModel):
    id: str
    user_id: str
    asset_id: str
    status: str
    compute_cost: Optional[float] = None
    energy_cost: Optional[float] = None
    total_cost: Optional[float] = None
    selected_quote: Optional[Dict[str, Any]] = None
    container_image: Optional[str] = None
    dataset_location: Optional[str] = None
    task_type: Optional[str] = None
    estimated_duration_hours: Optional[float] = None
    payment_id: Optional[str] = None
    paid_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    instance_type: Optional[str] = "on_demand"
    review_score: Optional[int] = None
    review_text: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    refund_status: Optional[str] = "none"
    refund_amount: Optional[float] = 0.0
    refund_reason: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderUpdate(BaseModel):
    status: Optional[str] = None
    payment_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None


class OrderPaid(BaseModel):
    """订单支付成功"""
    order_id: str
    payment_id: str
    paid_at: datetime


class OrderCompleted(BaseModel):
    """订单完成"""
    order_id: str
    completed_at: datetime
    actual_duration_hours: Optional[float] = None


class ReviewCreate(BaseModel):
    """创建评价"""
    order_id: str
    score: int = 5  # 1-5
    text: Optional[str] = None


class ReviewResponse(BaseModel):
    """评价响应"""
    order_id: str
    score: int
    text: Optional[str] = None
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RefundRequest(BaseModel):
    """退款请求"""
    order_id: str
    reason: str


class RefundResponse(BaseModel):
    """退款响应"""
    order_id: str
    refund_status: str  # pending / approved / rejected / completed
    refund_amount: float
    refund_reason: Optional[str] = None


class StatusHistory(BaseModel):
    """订单状态历史"""
    status: str
    timestamp: datetime
    remark: Optional[str] = None


class OrderListParams(BaseModel):
    """订单列表查询参数"""
    user_id: Optional[str] = None
    asset_id: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
