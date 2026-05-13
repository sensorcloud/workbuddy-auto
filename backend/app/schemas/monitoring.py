"""监控相关 Schema"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MetricQueryParams(BaseModel):
    metric: str
    from_time: datetime
    to_time: datetime
    interval: str = "1m"

class DataPoint(BaseModel):
    timestamp: datetime
    value: float

class MetricResponse(BaseModel):
    resource_id: str
    metric: str
    data_points: List[DataPoint]
    aggregates: dict

class AlertRuleCreate(BaseModel):
    name: str
    resource_id: Optional[str] = None
    metric: str
    condition: str  # gt / lt / eq / gte / lte
    threshold: float
    duration_seconds: int = 0
    notify_channels: str = "web"
    cooldown_seconds: int = 300

class AlertRuleUpdate(BaseModel):
    name: Optional[str] = None
    metric: Optional[str] = None
    condition: Optional[str] = None
    threshold: Optional[float] = None
    duration_seconds: Optional[int] = None
    notify_channels: Optional[str] = None
    is_active: Optional[int] = None

class AlertRuleResponse(BaseModel):
    id: str
    name: str
    resource_id: Optional[str] = None
    metric: str
    condition: str
    threshold: float
    duration_seconds: int
    notify_channels: str
    cooldown_seconds: int
    is_active: int
    last_triggered_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AlertResponse(BaseModel):
    id: str
    rule_id: Optional[str] = None
    resource_id: str
    metric: str
    value: float
    threshold: float
    condition: str
    status: str
    resolved_at: Optional[datetime] = None
    message: str = ""
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
