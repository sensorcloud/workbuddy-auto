"""
订单服务层
"""
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime
import uuid

from app.models.order import Order
from app.schemas.order import OrderCreate


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
        limit: int = 100,
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
        """
        支付订单。设置 status="paid", paid_at=now（支付和运行是两步）
        """
        db_order = db.query(Order).filter(Order.id == order_id).first()
        if not db_order:
            return None

        if db_order.status != "pending":
            raise ValueError("订单状态不允许支付")

        # 修改：设置 status="paid" 而不是 "running"
        db_order.status = "paid"
        db_order.paid_at = datetime.utcnow()

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

        if db_order.status not in ["pending", "paid", "running"]:
            raise ValueError("订单状态不允许取消")

        db_order.status = "cancelled"
        db_order.cancelled_at = datetime.utcnow()

        # 如果有冻结金额，需要解冻
        if db_order.payment_id:
            from app.services.wallet_service import WalletService

            # 解冻金额
            WalletService.unfreeze(
                db, db_order.user_id, Decimal(str(db_order.total_cost or 0)), order_id=order_id
            )

        db.commit()
        db.refresh(db_order)

        return db_order

    @staticmethod
    def complete_order(db: Session, order_id: str) -> Order:
        """
        标记订单完成（已有，但需增强：触发结算 - consume 冻结金额）
        现有代码设置 status="completed", completed_at
        增强：调用 WalletService.consume() 从冻结金额中扣除
        """
        db_order = db.query(Order).filter(Order.id == order_id).first()
        if not db_order:
            return None

        db_order.status = "completed"
        db_order.completed_at = datetime.utcnow()

        # 增强：调用 WalletService.consume() 从冻结金额中扣除
        if db_order.total_cost and db_order.total_cost > 0:
            try:
                from app.services.wallet_service import WalletService

                WalletService.consume(
                    db,
                    db_order.user_id,
                    Decimal(str(db_order.total_cost)),
                    order_id=order_id,
                )
            except Exception:
                # 消费失败不影响订单完成状态
                pass

        db.commit()
        db.refresh(db_order)

        return db_order

    @staticmethod
    def review_order(
        db: Session, order_id: str, user_id: str, score: int, text: str = None
    ) -> dict:
        """
        订单评价。仅 completed 状态可评价。
        - 设置 order.review_score, review_text, reviewed_at
        - 更新 Asset.rating (平均评分) 和 Asset.total_orders
        - 返回 {"success": True, "review": {...}}
        """
        db_order = db.query(Order).filter(Order.id == order_id).first()
        if not db_order:
            return {"success": False, "message": "订单不存在"}

        if db_order.user_id != user_id:
            return {"success": False, "message": "无权限评价此订单"}

        if db_order.status != "completed":
            return {"success": False, "message": "只能评价已完成的订单"}

        if db_order.review_score is not None:
            return {"success": False, "message": "此订单已评价"}

        if score < 1 or score > 5:
            return {"success": False, "message": "评分必须在 1-5 之间"}

        # 更新订单评价
        db_order.review_score = score
        db_order.review_text = text
        db_order.reviewed_at = datetime.utcnow()

        # 更新资产评分
        from app.models.asset import Asset

        asset = db.query(Asset).filter(Asset.id == db_order.asset_id).first()
        if asset:
            # 计算新的平均评分
            all_reviews = (
                db.query(Order)
                .filter(
                    Order.asset_id == db_order.asset_id,
                    Order.review_score.isnot(None),
                )
                .all()
            )
            total_score = sum(r.review_score for r in all_reviews) + score
            review_count = len(all_reviews) + 1
            new_rating = total_score / review_count

            asset.rating = round(new_rating, 2)
            asset.total_orders = (asset.total_orders or 0) + 1

        db.commit()
        db.refresh(db_order)

        return {
            "success": True,
            "review": {
                "order_id": order_id,
                "score": score,
                "text": text,
                "reviewed_at": (
                    db_order.reviewed_at.isoformat() if db_order.reviewed_at else None
                ),
            },
        }

    @staticmethod
    def refund_order(
        db: Session, order_id: str, user_id: str, reason: str, amount: float = None
    ) -> dict:
        """
        申请退款。
        - 未使用 (status=paid): 全额退款
        - 运行中 (status=running): 按比例退款（简化：退 50%）
        - 调用 WalletService.refund() 退还金额
        - 更新 order.refund_status, refund_amount, refund_reason
        - 更新 order.status = "cancelled", cancelled_at = now
        - 返回 {"success": True, "refund_amount": ..., "refund_id": ...}
        """
        db_order = db.query(Order).filter(Order.id == order_id).first()
        if not db_order:
            return {"success": False, "message": "订单不存在"}

        if db_order.user_id != user_id:
            return {"success": False, "message": "无权限申请退款"}

        if db_order.status not in ["paid", "running"]:
            return {"success": False, "message": "此状态不允许申请退款"}

        if db_order.refund_status != "none":
            return {"success": False, "message": "此订单已申请过退款"}

        # 计算退款金额
        total_cost = db_order.total_cost or 0
        if amount is None:
            # 默认全额退款
            refund_amount = total_cost
        else:
            refund_amount = min(amount, total_cost)

        # 如果是运行中订单，按 50% 退款
        if db_order.status == "running" and amount is None:
            refund_amount = total_cost * 0.5

        # 调用钱包退款
        from app.services.wallet_service import WalletService

        refund_result = WalletService.refund(
            db,
            user_id,
            Decimal(str(refund_amount)),
            order_id=order_id,
        )

        if not refund_result.get("success"):
            return {"success": False, "message": refund_result.get("message", "退款失败")}

        # 更新订单退款状态
        db_order.refund_status = "pending"
        db_order.refund_amount = refund_amount
        db_order.refund_reason = reason
        db_order.status = "cancelled"
        db_order.cancelled_at = datetime.utcnow()

        db.commit()
        db.refresh(db_order)

        return {
            "success": True,
            "order_id": order_id,
            "refund_amount": refund_amount,
            "refund_status": "pending",
            "message": "退款申请已提交",
        }

    @staticmethod
    def get_status_history(db: Session, order_id: str) -> list:
        """
        订单状态变更历史。
        基于 Order 的各时间字段推算：
        - created_at → status="pending"
        - paid_at → status="paid"
        - started_at → status="running"
        - completed_at → status="completed"
        - cancelled_at → status="cancelled"
        返回 [{"status": "pending", "timestamp": "...", "remark": "订单创建"}, ...]
        """
        db_order = db.query(Order).filter(Order.id == order_id).first()
        if not db_order:
            return []

        history = []

        # 订单创建
        if db_order.created_at:
            history.append(
                {
                    "status": "pending",
                    "timestamp": db_order.created_at.isoformat(),
                    "remark": "订单创建",
                }
            )

        # 支付
        if db_order.paid_at:
            history.append(
                {
                    "status": "paid",
                    "timestamp": db_order.paid_at.isoformat(),
                    "remark": "支付成功",
                }
            )

        # 启动
        if db_order.started_at:
            history.append(
                {
                    "status": "running",
                    "timestamp": db_order.started_at.isoformat(),
                    "remark": "任务启动",
                }
            )

        # 完成
        if db_order.completed_at:
            history.append(
                {
                    "status": "completed",
                    "timestamp": db_order.completed_at.isoformat(),
                    "remark": "任务完成",
                }
            )

        # 取消
        if db_order.cancelled_at:
            history.append(
                {
                    "status": "cancelled",
                    "timestamp": db_order.cancelled_at.isoformat(),
                    "remark": db_order.refund_reason or "订单取消",
                }
            )

        # 按时间排序
        history.sort(key=lambda x: x["timestamp"])

        return history
