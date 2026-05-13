"""
调度服务层
集成峰谷定价计算
"""
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime
import random

from app.models.asset import Asset
from app.models.order import Order
from app.core.pricing import (
    calculate_adjusted_price,
    get_period_type,
    get_price_multiplier,
)


class SchedulingService:
    """调度服务类"""

    @staticmethod
    def get_quote(db: Session, task_type: str, strategy: str = "cheapest", estimated_duration_hours: float = 1.0):
        """
        获取智能报价，集成峰谷定价
        """
        # 获取当前时段信息
        period_type = get_period_type()
        multiplier = get_price_multiplier()

        # 查询可用资产
        assets = db.query(Asset).filter(Asset.status == "online").limit(10).all()

        if not assets:
            # 返回模拟数据（带峰谷定价）
            base_compute = 15.0
            adjusted_compute = float(calculate_adjusted_price(Decimal(str(base_compute))))

            return {
                "task_type": task_type,
                "strategy": strategy,
                "period_type": period_type,
                "multiplier": float(multiplier),
                "quotes": [
                    {
                        "asset_id": "asset-sim-001",
                        "provider_id": "provider-sim",
                        "compute_cost": round(adjusted_compute * estimated_duration_hours, 2),
                        "energy_cost": round(3.5 * estimated_duration_hours, 2),
                        "total_cost": round((adjusted_compute + 3.5) * estimated_duration_hours, 2),
                        "estimated_carbon_kg": round(0.8 * estimated_duration_hours, 2),
                        "carbon_saved_kg": round(12.5 * estimated_duration_hours, 2),
                        "match_reason": f"推荐方案：使用上海光伏发电+ A100，绿色低碳且价格适中（{period_type}时段）",
                        "period_type": period_type,
                        "multiplier": float(multiplier),
                    },
                    {
                        "asset_id": "asset-sim-002",
                        "provider_id": "provider-sim-2",
                        "compute_cost": round(28.0 * estimated_duration_hours, 2),
                        "energy_cost": round(5.6 * estimated_duration_hours, 2),
                        "total_cost": round(33.6 * estimated_duration_hours, 2),
                        "estimated_carbon_kg": round(0.3 * estimated_duration_hours, 2),
                        "carbon_saved_kg": round(18.0 * estimated_duration_hours, 2),
                        "match_reason": f"绿色方案：使用张家口风力发电+ H100，碳排放最低",
                        "period_type": period_type,
                        "multiplier": float(multiplier),
                    },
                    {
                        "asset_id": "asset-sim-003",
                        "provider_id": "provider-sim-3",
                        "compute_cost": round(8.5 * estimated_duration_hours, 2),
                        "energy_cost": round(3.4 * estimated_duration_hours, 2),
                        "total_cost": round(11.9 * estimated_duration_hours, 2),
                        "estimated_carbon_kg": round(1.5 * estimated_duration_hours, 2),
                        "carbon_saved_kg": round(5.0 * estimated_duration_hours, 2),
                        "match_reason": f"经济方案：使用深圳混合供电+ L40S，性价比最高",
                        "period_type": period_type,
                        "multiplier": float(multiplier),
                    },
                ],
                "recommended": None,
            }

        # 基于真实资产生成报价
        quotes = []
        for asset in assets:
            base_price = Decimal(str(asset.pricing.get("compute_price_per_hour", 15.0) if asset.pricing else 15.0))

            # 应用峰谷定价
            adjusted_price = calculate_adjusted_price(base_price)

            power_source = asset.energy_profile.get("power_source", "grid") if asset.energy_profile else "grid"
            pue = Decimal(str(asset.energy_profile.get("PUE", 1.3) if asset.energy_profile else 1.3))

            # 根据策略调整价格
            if strategy == "cheapest":
                price_multiplier = Decimal("0.8")
                discount_label = "竞价折扣"
            elif strategy == "greenest":
                price_multiplier = Decimal("1.0") if power_source in ("solar", "wind") else Decimal("0.9")
                discount_label = "绿色优先"
            else:  # fastest
                price_multiplier = Decimal("1.1")
                discount_label = "快速部署"

            # 应用策略价格系数后，再应用峰谷系数
            compute_cost = (adjusted_price * price_multiplier * Decimal(str(estimated_duration_hours)))
            compute_cost = compute_cost.quantize(Decimal("0.01"))

            # 能源成本也应用峰谷系数
            base_energy = base_price * Decimal("0.2") * pue * Decimal(str(estimated_duration_hours))
            energy_cost = (base_energy * Decimal(str(multiplier))).quantize(Decimal("0.01"))

            total_cost = (compute_cost + energy_cost).quantize(Decimal("0.01"))

            carbon_saved = round(random.uniform(0.5, 15.0) * estimated_duration_hours, 2)
            estimated_carbon = round(random.uniform(0.3, 5.0) * estimated_duration_hours, 2)

            gpu = asset.spec.get("gpu", "GPU") if asset.spec else "GPU"
            region = asset.location.get("region", "") if asset.location else ""

            quotes.append({
                "asset_id": asset.id,
                "provider_id": asset.owner_id,
                "compute_cost": float(compute_cost),
                "energy_cost": float(energy_cost),
                "total_cost": float(total_cost),
                "estimated_carbon_kg": estimated_carbon,
                "carbon_saved_kg": carbon_saved,
                "match_reason": f"{discount_label}：{region} {power_source}供电 + {gpu}，总费用 ¥{total_cost}（{period_type}时段×{multiplier}）",
                "period_type": period_type,
                "multiplier": float(multiplier),
            })

        # 按策略排序
        if strategy == "cheapest":
            quotes.sort(key=lambda x: x["total_cost"])
        elif strategy == "greenest":
            quotes.sort(key=lambda x: -x["carbon_saved_kg"])
        else:
            quotes.sort(key=lambda x: x["total_cost"])

        return {
            "task_type": task_type,
            "strategy": strategy,
            "period_type": period_type,
            "multiplier": float(multiplier),
            "quotes": quotes,
            "recommended": quotes[0] if quotes else None,
        }

    @staticmethod
    def submit_task(db: Session, user_id: str, asset_id: str, task_config: dict):
        """提交任务"""
        selected_quote = task_config.get("selected_quote", {})

        # 提取峰谷定价信息
        period_type = selected_quote.get("period_type", get_period_type())
        multiplier = selected_quote.get("multiplier", float(get_price_multiplier()))

        # 创建订单
        order = Order(
            id=f"order-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            user_id=user_id,
            asset_id=asset_id,
            status="pending",
            task_type=task_config.get("task_type"),
            estimated_duration_hours=task_config.get("estimated_hours", 1.0),
            container_image=task_config.get("container_image"),
            dataset_location=task_config.get("dataset_location"),
            selected_quote=selected_quote,
            compute_cost=selected_quote.get("compute_cost", 0),
            energy_cost=selected_quote.get("energy_cost", 0),
            total_cost=selected_quote.get("total_cost", 0),
        )

        db.add(order)
        db.commit()
        db.refresh(order)

        return {
            "order_id": order.id,
            "status": order.status,
            "message": "任务已提交，请支付后开始执行",
            "period_type": period_type,
            "multiplier": multiplier,
        }
