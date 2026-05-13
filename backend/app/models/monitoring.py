"""监控指标、告警规则与告警记录模型"""
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from app.models.base import Base
from datetime import datetime

class MetricSample(Base):
    __tablename__ = "metric_samples"

    id = Column(String, primary_key=True, index=True)
    resource_id = Column(String, index=True, nullable=False)
    metric_name = Column(String, index=True, nullable=False)  # gpu_util / gpu_memory / cpu_util / memory / power / pue / temperature
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    tags = Column(String)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    resource_id = Column(String, index=True)
    name = Column(String, nullable=False)
    metric = Column(String, nullable=False)
    condition = Column(String, nullable=False)  # gt / lt / eq / gte / lte
    threshold = Column(Float, nullable=False)
    duration_seconds = Column(Integer, default=0)
    notify_channels = Column(String, default="web")
    cooldown_seconds = Column(Integer, default=300)
    is_active = Column(Integer, default=1)
    last_triggered_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, index=True)
    rule_id = Column(String, ForeignKey("alert_rules.id"), index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True, nullable=False)
    resource_id = Column(String, index=True, nullable=False)
    metric = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    condition = Column(String, nullable=False)
    status = Column(String, default="triggered")  # triggered / resolved / silenced
    resolved_at = Column(DateTime)
    message = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
