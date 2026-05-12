"""
支付服务层
"""
from sqlalchemy.orm import Session
from app.models.order import Order
from datetime import datetime


class PaymentService:
    """支付服务类"""
    
    @staticmethod
    def process_payment(db: Session, order_id: str, payment_method: str = "balance") -> dict:
        """处理支付"""
        db_order = db.query(Order).filter(Order.id == order_id).first()
        if not db_order:
            return {"success": False, "message": "订单不存在"}
        
        if db_order.status != "pending":
            return {"success": False, "message": "订单状态不允许支付"}
        
        # 模拟支付处理
        db_order.status = "running"
        db_order.started_at = datetime.utcnow()
        db_order.compute_cost = db_order.selected_quote.get("compute_cost", 0) if db_order.selected_quote else 0
        db_order.energy_cost = db_order.selected_quote.get("energy_cost", 0) if db_order.selected_quote else 0
        db_order.total_cost = db_order.compute_cost + db_order.energy_cost
        
        db.commit()
        db.refresh(db_order)
        
        return {"success": True, "order": db_order}
    
    @staticmethod
    def get_payment_status(db: Session, order_id: str) -> dict:
        """获取支付状态"""
        db_order = db.query(Order).filter(Order.id == order_id).first()
        if not db_order:
            return {"success": False, "message": "订单不存在"}
        
        return {
            "success": True,
            "status": db_order.status,
            "total_cost": db_order.total_cost,
            "paid_at": db_order.started_at
        }
