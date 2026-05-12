"""
收益服务层
"""
from sqlalchemy.orm import Session
from app.models.order import Order
from sqlalchemy import func
from datetime import datetime, timedelta


class EarningsService:
    """收益服务类"""
    
    @staticmethod
    def get_earnings_summary(db: Session, user_id: str, period: str = "today"):
        """获取收益摘要"""
        query = db.query(Order).filter(Order.user_id == user_id)
        
        # 时间过滤
        now = datetime.utcnow()
        if period == "today":
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
            query = query.filter(Order.created_at >= start_time)
        elif period == "week":
            start_time = now - timedelta(days=7)
            query = query.filter(Order.created_at >= start_time)
        elif period == "month":
            start_time = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            query = query.filter(Order.created_at >= start_time)
        
        orders = query.filter(Order.status.in_(["running", "completed"])).all()
        
        total_earnings = sum(order.total_cost or 0 for order in orders)
        order_count = len(orders)
        
        return {
            "total_earnings": total_earnings,
            "order_count": order_count,
            "period": period
        }
    
    @staticmethod
    def get_earnings_detail(db: Session, user_id: str, start_date: datetime = None, end_date: datetime = None):
        """获取收益明细"""
        query = db.query(Order).filter(Order.user_id == user_id)
        
        if start_date:
            query = query.filter(Order.created_at >= start_date)
        if end_date:
            query = query.filter(Order.created_at <= end_date)
        
        orders = query.order_by(Order.created_at.desc()).all()
        
        return [
            {
                "order_id": order.id,
                "created_at": order.created_at,
                "total_cost": order.total_cost,
                "status": order.status
            }
            for order in orders
        ]
