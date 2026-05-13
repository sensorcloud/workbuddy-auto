"""
监控服务层
提供指标采集、存储、查询、告警规则管理等功能
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from datetime import datetime, timedelta
import uuid
import random
import math

from app.models.asset import Asset
from app.models.monitoring import MetricSample, AlertRule, Alert


class MonitoringService:
    """监控服务类"""

    @staticmethod
    def generate_mock_metrics(db: Session) -> int:
        """
        按 Asset 生成结构化模拟指标。
        查询所有 status="online" 的 Asset，对每个 Asset 生成一组指标：
        - gpu_util: 正弦波 + 随机噪声 (30%-95%)
        - gpu_memory: 线性增长 + 波动 (40%-90%)
        - cpu_util: 基于 gpu_util * 0.3 + noise (10%-50%)
        - memory: 随机波动 (20%-80%)
        - power: 基于 gpu_util 线性变化 + 峰谷系数 (100W-500W)
        - pue: 资产的 PUE + 小波动 (1.1-1.8)
        - temperature: 基于 power 线性变化 (40-85°C)
        写入 MetricSample 表，返回插入数量
        """
        # 查询在线资产
        assets = db.query(Asset).filter(Asset.status == "online").all()

        if not assets:
            return 0

        timestamp = datetime.utcnow()
        hour = timestamp.hour

        # 峰谷时段系数（简化版）
        if 8 <= hour < 11 or 18 <= hour < 21:
            power_multiplier = 1.2  # 峰时
        elif 23 <= hour or hour < 7:
            power_multiplier = 0.8  # 谷时
        else:
            power_multiplier = 1.0  # 平时

        count = 0
        for asset in assets:
            # 获取资产的 PUE 和 GPU 信息
            pue = (
                asset.energy_profile.get("PUE", 1.3) if asset.energy_profile else 1.3
            )
            gpu_count = (
                asset.spec.get("gpu_count", 1) if asset.spec else 1
            )
            gpu_util_base = 50 + 30 * math.sin(timestamp.timestamp() / 3600)  # 正弦波基础

            # 生成各指标
            metrics_data = [
                {
                    "metric_name": "gpu_util",
                    "value": gpu_util_base + random.uniform(-10, 10),
                },
                {
                    "metric_name": "gpu_memory",
                    "value": 50 + (count % 20),  # 线性增长 + 波动
                },
                {
                    "metric_name": "cpu_util",
                    "value": gpu_util_base * 0.3 + random.uniform(-5, 5),
                },
                {
                    "metric_name": "memory",
                    "value": random.uniform(20, 80),
                },
                {
                    "metric_name": "power",
                    "value": (gpu_util_base / 100) * gpu_count * 200 * power_multiplier + 100,
                },
                {
                    "metric_name": "pue",
                    "value": pue + random.uniform(-0.05, 0.05),
                },
                {
                    "metric_name": "temperature",
                    "value": 40 + (gpu_util_base / 100) * 45 + random.uniform(-3, 3),
                },
            ]

            # 限制范围
            for m in metrics_data:
                if m["metric_name"] == "gpu_util":
                    m["value"] = max(30, min(95, m["value"]))
                elif m["metric_name"] == "gpu_memory":
                    m["value"] = max(40, min(90, m["value"]))
                elif m["metric_name"] == "cpu_util":
                    m["value"] = max(10, min(50, m["value"]))
                elif m["metric_name"] == "memory":
                    m["value"] = max(20, min(80, m["value"]))
                elif m["metric_name"] == "power":
                    m["value"] = max(100, min(500, m["value"]))
                elif m["metric_name"] == "pue":
                    m["value"] = max(1.1, min(1.8, m["value"]))
                elif m["metric_name"] == "temperature":
                    m["value"] = max(40, min(85, m["value"]))

                # 写入 MetricSample
                sample = MetricSample(
                    id=str(uuid.uuid4()),
                    resource_id=asset.id,
                    metric_name=m["metric_name"],
                    value=m["value"],
                    timestamp=timestamp,
                    tags=f'{{"gpu_count": {gpu_count}}}',
                )
                db.add(sample)
                count += 1

        db.commit()
        return count

    @staticmethod
    def store_metrics(db: Session, resource_id: str, metrics: dict) -> None:
        """
        存储一组指标到 MetricSample 表
        """
        timestamp = datetime.utcnow()

        for metric_name, value in metrics.items():
            sample = MetricSample(
                id=str(uuid.uuid4()),
                resource_id=resource_id,
                metric_name=metric_name,
                value=float(value),
                timestamp=timestamp,
            )
            db.add(sample)

        db.commit()

    @staticmethod
    def query_metrics(
        db: Session,
        resource_id: str,
        metric: str,
        from_time: datetime,
        to_time: datetime,
    ) -> dict:
        """
        查询历史指标数据。
        - 从 MetricSample 表查询
        - 计算 aggregates: avg, max, min, count
        - 返回 {"resource_id", "metric", "data_points": [...], "aggregates": {...}, "from": ..., "to": ...}
        """
        samples = (
            db.query(MetricSample)
            .filter(
                MetricSample.resource_id == resource_id,
                MetricSample.metric_name == metric,
                MetricSample.timestamp >= from_time,
                MetricSample.timestamp <= to_time,
            )
            .order_by(MetricSample.timestamp.asc())
            .all()
        )

        data_points = [
            {"timestamp": s.timestamp, "value": s.value} for s in samples
        ]

        # 计算统计值
        if samples:
            values = [s.value for s in samples]
            aggregates = {
                "avg": sum(values) / len(values),
                "max": max(values),
                "min": min(values),
                "count": len(values),
            }
        else:
            aggregates = {"avg": 0, "max": 0, "min": 0, "count": 0}

        return {
            "resource_id": resource_id,
            "metric": metric,
            "data_points": data_points,
            "aggregates": aggregates,
            "from": from_time.isoformat() if isinstance(from_time, datetime) else from_time,
            "to": to_time.isoformat() if isinstance(to_time, datetime) else to_time,
        }

    @staticmethod
    def get_latest_metrics(db: Session, resource_id: str) -> dict:
        """获取资源最新指标快照（最近一条每种 metric 的记录）"""
        # 查询每种 metric 的最新记录
        metrics = (
            db.query(
                MetricSample.metric_name,
                func.max(MetricSample.timestamp).label("max_ts"),
            )
            .filter(MetricSample.resource_id == resource_id)
            .group_by(MetricSample.metric_name)
            .all()
        )

        result = {}
        for m in metrics:
            latest = (
                db.query(MetricSample)
                .filter(
                    MetricSample.resource_id == resource_id,
                    MetricSample.metric_name == m.metric_name,
                    MetricSample.timestamp == m.max_ts,
                )
                .first()
            )
            if latest:
                result[m.metric_name] = {
                    "value": latest.value,
                    "timestamp": latest.timestamp.isoformat(),
                }

        return result

    @staticmethod
    def check_alert_rules(db: Session, resource_id: str, metrics: dict) -> list:
        """
        检查告警规则。
        - 查询该资源 + 该用户的所有活跃规则
        - 对每条规则：检查条件是否满足 (value > threshold 等)
        - 检查持续时间（简单实现：如果 duration_seconds > 0，查询最近 duration_seconds 的数据是否持续超阈值）
        - 检查冷却期
        - 满足条件时触发告警：创建 Alert 记录 + 更新 AlertRule.last_triggered_at
        - 返回触发的告警列表
        """
        # 获取资产所有者
        asset = db.query(Asset).filter(Asset.id == resource_id).first()
        if not asset:
            return []

        user_id = asset.owner_id

        # 查询活跃规则
        rules = (
            db.query(AlertRule)
            .filter(
                AlertRule.user_id == user_id,
                AlertRule.is_active == 1,
            )
            .all()
        )

        triggered_alerts = []
        current_time = datetime.utcnow()

        for rule in rules:
            # 检查资源匹配
            if rule.resource_id and rule.resource_id != resource_id:
                continue

            # 检查冷却期
            if rule.last_triggered_at:
                cooldown_delta = timedelta(seconds=rule.cooldown_seconds)
                if current_time - rule.last_triggered_at < cooldown_delta:
                    continue

            # 获取当前指标值
            metric_name = rule.metric
            if metric_name not in metrics:
                continue

            current_value = metrics[metric_name]

            # 检查条件
            condition_met = False
            if rule.condition == "gt" and current_value > rule.threshold:
                condition_met = True
            elif rule.condition == "lt" and current_value < rule.threshold:
                condition_met = True
            elif rule.condition == "gte" and current_value >= rule.threshold:
                condition_met = True
            elif rule.condition == "lte" and current_value <= rule.threshold:
                condition_met = True
            elif rule.condition == "eq" and abs(current_value - rule.threshold) < 0.001:
                condition_met = True

            # 检查持续时间（简化实现）
            if condition_met and rule.duration_seconds > 0:
                duration_delta = timedelta(seconds=rule.duration_seconds)
                from_time = current_time - duration_delta
                # 查询是否持续超阈值
                continuous_samples = (
                    db.query(MetricSample)
                    .filter(
                        MetricSample.resource_id == resource_id,
                        MetricSample.metric_name == metric_name,
                        MetricSample.timestamp >= from_time,
                    )
                    .all()
                )

                all_breach = True
                for sample in continuous_samples:
                    sample_breach = False
                    if rule.condition == "gt" and sample.value > rule.threshold:
                        sample_breach = True
                    elif rule.condition == "lt" and sample.value < rule.threshold:
                        sample_breach = True
                    elif rule.condition == "gte" and sample.value >= rule.threshold:
                        sample_breach = True
                    elif rule.condition == "lte" and sample.value <= rule.threshold:
                        sample_breach = True

                    if not sample_breach:
                        all_breach = False
                        break

                condition_met = all_breach

            # 触发告警
            if condition_met:
                # 更新规则的触发时间
                rule.last_triggered_at = current_time

                # 创建告警记录
                alert = Alert(
                    id=str(uuid.uuid4()),
                    rule_id=rule.id,
                    user_id=user_id,
                    resource_id=resource_id,
                    metric=metric_name,
                    value=current_value,
                    threshold=rule.threshold,
                    condition=rule.condition,
                    status="triggered",
                    message=f'{rule.name}: {metric_name} {rule.condition} {rule.threshold}, 当前值: {current_value}',
                )
                db.add(alert)
                triggered_alerts.append(alert)

        if triggered_alerts:
            db.commit()

        return triggered_alerts


class AlertService:
    """告警服务类"""

    @staticmethod
    def create_alert_rule(db: Session, user_id: str, rule_data: dict) -> AlertRule:
        """创建告警规则"""
        rule_id = str(uuid.uuid4())
        rule = AlertRule(
            id=rule_id,
            user_id=user_id,
            resource_id=rule_data.get("resource_id"),
            name=rule_data.get("name"),
            metric=rule_data.get("metric"),
            condition=rule_data.get("condition"),  # gt / lt / eq / gte / lte
            threshold=float(rule_data.get("threshold")),
            duration_seconds=rule_data.get("duration_seconds", 0),
            notify_channels=rule_data.get("notify_channels", "web"),
            cooldown_seconds=rule_data.get("cooldown_seconds", 300),
            is_active=1,
        )
        db.add(rule)
        db.commit()
        db.refresh(rule)
        return rule

    @staticmethod
    def list_alert_rules(db: Session, user_id: str) -> list:
        """获取用户所有告警规则"""
        return (
            db.query(AlertRule)
            .filter(AlertRule.user_id == user_id)
            .order_by(AlertRule.created_at.desc())
            .all()
        )

    @staticmethod
    def update_alert_rule(
        db: Session, rule_id: str, user_id: str, update_data: dict
    ) -> AlertRule:
        """更新告警规则"""
        rule = (
            db.query(AlertRule)
            .filter(AlertRule.id == rule_id, AlertRule.user_id == user_id)
            .first()
        )
        if not rule:
            raise ValueError("告警规则不存在")

        if "name" in update_data:
            rule.name = update_data["name"]
        if "metric" in update_data:
            rule.metric = update_data["metric"]
        if "condition" in update_data:
            rule.condition = update_data["condition"]
        if "threshold" in update_data:
            rule.threshold = float(update_data["threshold"])
        if "duration_seconds" in update_data:
            rule.duration_seconds = update_data["duration_seconds"]
        if "notify_channels" in update_data:
            rule.notify_channels = update_data["notify_channels"]
        if "is_active" in update_data:
            rule.is_active = update_data["is_active"]

        db.commit()
        db.refresh(rule)
        return rule

    @staticmethod
    def delete_alert_rule(db: Session, rule_id: str, user_id: str) -> bool:
        """删除告警规则"""
        rule = (
            db.query(AlertRule)
            .filter(AlertRule.id == rule_id, AlertRule.user_id == user_id)
            .first()
        )
        if not rule:
            return False

        db.delete(rule)
        db.commit()
        return True

    @staticmethod
    def list_alerts(
        db: Session,
        user_id: str,
        status: str = None,
        resource_id: str = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """获取告警列表"""
        query = db.query(Alert).filter(Alert.user_id == user_id)

        if status:
            query = query.filter(Alert.status == status)
        if resource_id:
            query = query.filter(Alert.resource_id == resource_id)

        total = query.count()
        offset = (page - 1) * page_size
        items = (
            query.order_by(Alert.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return {"items": items, "total": total, "page": page, "page_size": page_size}

    @staticmethod
    def resolve_alert(db: Session, alert_id: str, user_id: str) -> Alert:
        """手动解除告警"""
        alert = (
            db.query(Alert)
            .filter(Alert.id == alert_id, Alert.user_id == user_id)
            .first()
        )
        if not alert:
            raise ValueError("告警不存在")

        alert.status = "resolved"
        alert.resolved_at = datetime.utcnow()

        db.commit()
        db.refresh(alert)
        return alert
