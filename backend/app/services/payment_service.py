"""
支付服务层
包含 MockPaymentGateway 和 PaymentService
"""
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime
import uuid
import time
import base64

from app.models.payment import Payment
from app.models.order import Order
from app.core.config import settings


class MockPaymentGateway:
    """模拟支付网关，接口按真实支付网关设计"""

    @staticmethod
    def create_trade(amount: Decimal, channel: str, order_id: str) -> dict:
        """
        创建模拟支付交易
        """
        timestamp = int(time.time() * 1000)
        trade_no = f"MOCK-{channel.upper()}-{timestamp}"

        # 生成模拟支付链接和二维码
        payment_url = f"https://mock-pay.example.com/pay/{trade_no}"
        qr_code = base64.b64encode(f"mock://qr/{trade_no}".encode()).decode()

        return {
            "trade_no": trade_no,
            "payment_url": payment_url,
            "qr_code": qr_code,
        }

    @staticmethod
    def confirm_payment(trade_no: str) -> dict:
        """
        模拟确认支付（2秒延迟后成功）
        """
        time.sleep(2)
        return {"status": "success", "trade_no": trade_no}

    @staticmethod
    def query_status(trade_no: str) -> dict:
        """
        查询支付状态
        """
        return {"status": "success", "trade_no": trade_no}

    @staticmethod
    def create_refund(trade_no: str, amount: Decimal) -> dict:
        """
        模拟退款
        """
        return {
            "status": "refunded",
            "trade_no": trade_no,
            "refund_amount": str(amount),
        }


class PaymentService:
    """支付服务类"""

    @staticmethod
    def create_payment(db: Session, user_id: str, order_id: str, channel: str = "balance") -> dict:
        """
        创建支付请求。

        - 查询订单，校验状态为 pending
        - 如果 channel == "balance"：调用 WalletService.freeze() 冻结余额
          → Payment 状态直接设为 success → 更新订单状态为 paid
        - 如果 channel != "balance"：调用 MockPaymentGateway.create_trade()
          → Payment 状态为 pending → 返回 payment_url/qr_code
        - 创建 Payment 记录
        """
        # 查询订单
        db_order = db.query(Order).filter(Order.id == order_id).first()
        if not db_order:
            return {"success": False, "message": "订单不存在"}

        if db_order.status != "pending":
            return {"success": False, "message": "订单状态不允许支付"}

        if db_order.user_id != user_id:
            return {"success": False, "message": "无权限支付此订单"}

        # 计算金额（从 selected_quote 获取）
        compute_cost = db_order.compute_cost or 0
        energy_cost = db_order.energy_cost or 0
        total_cost = Decimal(str(compute_cost + energy_cost))

        payment_id = str(uuid.uuid4())

        # 延迟导入避免循环依赖
        from app.services.wallet_service import WalletService

        if channel == "balance":
            # 余额支付：冻结金额
            freeze_result = WalletService.freeze(
                db, user_id, total_cost, order_id=order_id
            )
            if not freeze_result.get("success"):
                return {"success": False, "message": freeze_result.get("message", "余额冻结失败")}

            # 创建支付记录（直接成功）
            payment = Payment(
                id=payment_id,
                order_id=order_id,
                user_id=user_id,
                channel=channel,
                amount=total_cost,
                status="success",
                paid_at=datetime.utcnow(),
            )
            db.add(payment)

            # 更新订单状态为 paid
            db_order.status = "paid"
            db_order.paid_at = datetime.utcnow()
            db_order.payment_id = payment_id

            db.commit()
            db.refresh(payment)
            db.refresh(db_order)

            return {
                "success": True,
                "payment_id": payment_id,
                "status": "success",
                "message": "支付成功（余额）",
            }
        else:
            # 第三方支付：调用模拟网关
            gateway_result = MockPaymentGateway.create_trade(
                total_cost, channel, order_id
            )

            # 创建支付记录（pending）
            payment = Payment(
                id=payment_id,
                order_id=order_id,
                user_id=user_id,
                channel=channel,
                amount=total_cost,
                status="pending",
                trade_no=gateway_result["trade_no"],
            )
            db.add(payment)
            db.commit()
            db.refresh(payment)

            return {
                "success": True,
                "payment_id": payment_id,
                "status": "pending",
                "trade_no": gateway_result["trade_no"],
                "payment_url": gateway_result["payment_url"],
                "qr_code": gateway_result["qr_code"],
            }

    @staticmethod
    def handle_callback(db: Session, payment_id: str, callback_data: dict) -> dict:
        """
        处理支付回调。

        - 更新 Payment 状态为 success/failed
        - 如果成功：更新 Order 状态为 paid，设置 paid_at
        - 如果是充值回调：调用 WalletService.recharge() 增加余额
        """
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            return {"success": False, "message": "支付记录不存在"}

        status = callback_data.get("status", "failed")
        payment.status = "success" if status == "success" else "failed"

        if status == "success":
            payment.paid_at = datetime.utcnow()
            payment.trade_no = callback_data.get("trade_no", payment.trade_no)

            # 更新关联订单状态
            db_order = db.query(Order).filter(Order.id == payment.order_id).first()
            if db_order and db_order.status == "pending":
                db_order.status = "paid"
                db_order.paid_at = datetime.utcnow()
                db_order.payment_id = payment_id

            db.commit()
            db.refresh(payment)
            return {"success": True, "message": "支付成功"}

        db.commit()
        return {"success": False, "message": "支付失败"}

    @staticmethod
    def mock_pay(db: Session, payment_id: str) -> dict:
        """
        开发用：模拟支付成功回调
        """
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            return {"success": False, "message": "支付记录不存在"}

        return PaymentService.handle_callback(
            db,
            payment_id,
            {"status": "success", "trade_no": payment.trade_no or f"MOCK-SIM-{payment_id}"},
        )

    @staticmethod
    def get_payment(db: Session, payment_id: str) -> Payment:
        """查询支付记录"""
        return db.query(Payment).filter(Payment.id == payment_id).first()

    @staticmethod
    def get_by_order_id(db: Session, order_id: str) -> Payment:
        """根据订单ID查询支付"""
        return db.query(Payment).filter(Payment.order_id == order_id).first()

    @staticmethod
    def refund_payment(db: Session, payment_id: str, amount: Decimal, reason: str = None) -> dict:
        """
        退款支付
        """
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            return {"success": False, "message": "支付记录不存在"}

        if payment.status != "success":
            return {"success": False, "message": "只有已支付的订单可以退款"}

        # 更新支付状态
        payment.status = "refunded"
        payment.refund_amount = amount
        payment.refund_reason = reason

        # 延迟导入
        from app.services.wallet_service import WalletService

        # 退款到钱包
        refund_result = WalletService.refund(
            db, payment.user_id, amount, order_id=payment.order_id
        )

        db.commit()
        db.refresh(payment)

        return {
            "success": True,
            "payment_id": payment_id,
            "refund_amount": float(amount),
            "message": "退款成功",
        }
