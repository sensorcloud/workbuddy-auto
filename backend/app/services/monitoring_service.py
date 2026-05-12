"""
监控服务层
"""
from sqlalchemy.orm import Session
from app.models.asset import Asset
from datetime import datetime


class MonitoringService:
    """监控服务类"""
    
    @staticmethod
    def get_asset_metrics(db: Session, asset_id: str):
        """获取资产监控指标（模拟数据）"""
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            return None
        
        # 模拟实时监控数据
        import random
        return {
            "asset_id": asset_id,
            "status": asset.status,
            "real_time_power_kw": round(random.uniform(2.0, 5.0), 2),
            "total_energy_consumed_kwh": round(random.uniform(10.0, 100.0), 2),
            "total_carbon_kg": round(random.uniform(5.0, 50.0), 2),
            "gpu_utilization": round(random.uniform(60.0, 99.0), 2),
            "temperature": round(random.uniform(50.0, 80.0), 2),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def get_task_status(db: Session, order_id: str):
        """获取任务状态（模拟数据）"""
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return None
        
        import random
        progress = 65
        if order.status == "completed":
            progress = 100
        elif order.status == "pending":
            progress = 0
        
        return {
            "order_id": order_id,
            "status": order.status,
            "progress": progress,
            "current_power_kw": round(random.uniform(2.0, 3.0), 2),
            "total_compute_cost": order.compute_cost or 0,
            "total_energy_cost": order.energy_cost or 0,
            "total_carbon_kg": round(random.uniform(1.0, 2.0), 2),
        }
