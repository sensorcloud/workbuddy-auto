"""
订单服务层
"""
from sqlalchemy.orm import Session
from app.models.order import Order
from app.schemas.order import OrderCreate
from datetime import datetime


class OrderService:
    """订单服务类"""
    
    @staticmethod
    def create_order(db: Session, order: OrderCreate) -> Order:
        """创建订单"""
        db_order = Order(
            id=f"order-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            user_id=order.user_id,
            asset_id=order.asset_id,
            status="pending",
            compute_cost=0.0,
            energy_cost=0.0,
            total_cost=0.0,
            selected_quote=order.selected_quote,
            container_image=order.container_image,
            dataset_location=order.dataset_location,
            task_type=order.task_type,
            estimated_duration_hours=order.estimated_duration_hours,
        )
        
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        
        return db_order
    
    @staticmethod
    def list_orders(
        db: Session,
        user_id: str = None,
        status: str = None,
        skip: int = 0,
        limit: int = 100
    ):
        """列出订单"""
        query = db.query(Order)
        
        if user_id:
            query = query.filter(Order.user_id == user_id)
        if status:
            query = query.filter(Order.status == status)
        
        return query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_order(db: Session, order_id: str) -> Order:
        """获取单个订单"""
        return db.query(Order).filter(Order.id == order_id).first()
    
    @staticmethod
    def pay_order(db: Session, order_id: str) -> Order:
        """支付订单"""
        db_order = db.query(Order).filter(Order.id == order_id).first()
        if not db_order:
            return None
        
        if db_order.status != "pending":
            raise ValueError("订单状态不允许支付")
        
        db_order.status = "running"
        db_order.started_at = datetime.utcnow()
        
        # 计算费用
        if db_order.selected_quote:
            db_order.compute_cost = db_order.selected_quote.get("compute_cost", 0)
            db_order.energy_cost = db_order.selected_quote.get("energy_cost", 0)
            db_order.total_cost = db_order.compute_cost + db_order.energy_cost
        
        db.commit()
        db.refresh(db_order)
        
        return db_order
    
    @staticmethod
    def cancel_order(db: Session, order_id: str) -> Order:
        """取消订单"""
        db_order = db.query(Order).filter(Order.id == order_id).first()
        if not db_order:
            return None
        
        if db_order.status not in ["pending", "running"]:
            raise ValueError("订单状态不允许取消")
        
        db_order.status = "cancelled"
        db.commit()
        db.refresh(db_order)
        
        return db_order
    
    @staticmethod
    def complete_order(db: Session, order_id: str) -> Order:
        """完成订单"""
        db_order = db.query(Order).filter(Order.id == order_id).first()
        if not db_order:
            return None
        
        db_order.status = "completed"
        db_order.completed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_order)
        
        return db_order
