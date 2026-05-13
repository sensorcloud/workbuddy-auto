"""
账单服务层
提供月度账单生成、查询、发票管理、对账等功能
"""
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime
import uuid

from app.models.billing import MonthlyBill, Invoice
from app.models.order import Order
from app.models.payment import Payment
from app.models.wallet import Transaction


class BillingService:
    """账单服务类"""

    @staticmethod
    def generate_monthly_bill(
        db: Session, user_id: str, year: int, month: int
    ) -> MonthlyBill:
        """
        生成月度账单。汇总指定月份所有已完成订单的费用：
        - 查询 Order (status="completed", completed_at 在该月份)
        - 汇总 compute_fee, energy_fee, network_fee=0, storage_fee=0
        - green_cert_discount=0 (P1)
        - actual_pay = total_amount - green_cert_discount
        - 如果已存在该月账单则更新，否则新建
        """
        # 计算月份范围
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        # 查询已完成订单
        orders = (
            db.query(Order)
            .filter(
                Order.user_id == user_id,
                Order.status == "completed",
                Order.completed_at >= start_date,
                Order.completed_at < end_date,
            )
            .all()
        )

        # 汇总费用
        total_compute_fee = Decimal("0")
        total_energy_fee = Decimal("0")
        total_network_fee = Decimal("0")
        total_storage_fee = Decimal("0")
        total_green_cert_discount = Decimal("0")

        for order in orders:
            total_compute_fee += Decimal(str(order.compute_cost or 0))
            total_energy_fee += Decimal(str(order.energy_cost or 0))
            # network_fee 和 storage_fee 从订单中获取（如果没有则默认为0）
            total_network_fee += Decimal("0")  # P1 暂不支持
            total_storage_fee += Decimal("0")  # P1 暂不支持

        total_amount = total_compute_fee + total_energy_fee + total_network_fee + total_storage_fee
        actual_pay = total_amount - total_green_cert_discount

        # 检查是否已存在账单
        bill = (
            db.query(MonthlyBill)
            .filter(
                MonthlyBill.user_id == user_id,
                MonthlyBill.year == year,
                MonthlyBill.month == month,
            )
            .first()
        )

        if bill:
            # 更新现有账单
            bill.total_amount = total_amount
            bill.compute_fee = total_compute_fee
            bill.energy_fee = total_energy_fee
            bill.network_fee = total_network_fee
            bill.storage_fee = total_storage_fee
            bill.green_cert_discount = total_green_cert_discount
            bill.actual_pay = actual_pay
            bill.order_count = len(orders)
        else:
            # 创建新账单
            bill_id = str(uuid.uuid4())
            bill = MonthlyBill(
                id=bill_id,
                user_id=user_id,
                year=year,
                month=month,
                total_amount=total_amount,
                compute_fee=total_compute_fee,
                energy_fee=total_energy_fee,
                network_fee=total_network_fee,
                storage_fee=total_storage_fee,
                green_cert_discount=total_green_cert_discount,
                actual_pay=actual_pay,
                order_count=len(orders),
                status="generated",
            )
            db.add(bill)

        db.commit()
        db.refresh(bill)
        return bill

    @staticmethod
    def get_bill(db: Session, user_id: str, year: int, month: int) -> MonthlyBill:
        """
        查询月度账单，不存在时自动生成
        """
        bill = (
            db.query(MonthlyBill)
            .filter(
                MonthlyBill.user_id == user_id,
                MonthlyBill.year == year,
                MonthlyBill.month == month,
            )
            .first()
        )

        if not bill:
            bill = BillingService.generate_monthly_bill(db, user_id, year, month)

        return bill

    @staticmethod
    def list_bills(
        db: Session, user_id: str, page: int = 1, page_size: int = 12
    ) -> dict:
        """
        账单列表，按年月倒序
        """
        query = db.query(MonthlyBill).filter(MonthlyBill.user_id == user_id)

        total = query.count()
        offset = (page - 1) * page_size
        items = (
            query.order_by(MonthlyBill.year.desc(), MonthlyBill.month.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return {"items": items, "total": total, "page": page, "page_size": page_size}

    @staticmethod
    def create_invoice(
        db: Session, bill_id: str, user_id: str, invoice_data: dict
    ) -> Invoice:
        """
        申请发票。
        - 验证账单存在且状态为 generated/paid
        - 创建 Invoice 记录
        - 模拟开票：设置 status="issued", issued_at=now
        """
        bill = db.query(MonthlyBill).filter(MonthlyBill.id == bill_id).first()
        if not bill:
            raise ValueError("账单不存在")

        if bill.user_id != user_id:
            raise ValueError("无权限为此账单申请发票")

        if bill.status not in ("generated", "paid"):
            raise ValueError("账单状态不允许申请发票")

        # 检查是否已有发票
        existing = (
            db.query(Invoice)
            .filter(Invoice.bill_id == bill_id, Invoice.user_id == user_id)
            .first()
        )
        if existing:
            raise ValueError("此账单已存在发票")

        # 创建发票记录
        invoice_id = str(uuid.uuid4())
        invoice = Invoice(
            id=invoice_id,
            bill_id=bill_id,
            user_id=user_id,
            type=invoice_data.get("type", "normal"),
            title=invoice_data.get("title"),
            tax_no=invoice_data.get("tax_no"),
            amount=bill.actual_pay,
            status="pending",
        )
        db.add(invoice)

        # 模拟开票：设置 status="issued", issued_at=now
        invoice.status = "issued"
        invoice.issued_at = datetime.utcnow()

        db.commit()
        db.refresh(invoice)
        return invoice

    @staticmethod
    def list_invoices(
        db: Session,
        user_id: str,
        bill_id: str = None,
        status: str = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """
        发票列表
        """
        query = db.query(Invoice).filter(Invoice.user_id == user_id)

        if bill_id:
            query = query.filter(Invoice.bill_id == bill_id)

        if status:
            query = query.filter(Invoice.status == status)

        total = query.count()
        offset = (page - 1) * page_size
        items = (
            query.order_by(Invoice.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return {"items": items, "total": total, "page": page, "page_size": page_size}

    @staticmethod
    def reconcile(db: Session, user_id: str, start_date: str, end_date: str) -> dict:
        """
        对账管理。核查交易流水与订单一致性：
        - total_orders, total_amount (订单总额)
        - total_payments (支付总额)
        - total_refunds (退款总额)
        - discrepancy = total_amount - total_payments + total_refunds
        - details: 逐笔明细
        """
        from datetime import datetime

        start_dt = datetime.fromisoformat(start_date) if isinstance(start_date, str) else start_date
        end_dt = datetime.fromisoformat(end_date) if isinstance(end_date, str) else end_date

        # 查询订单
        orders = (
            db.query(Order)
            .filter(
                Order.user_id == user_id,
                Order.created_at >= start_dt,
                Order.created_at <= end_dt,
            )
            .all()
        )

        total_orders = len(orders)
        total_amount = Decimal("0")
        for order in orders:
            total_amount += Decimal(str(order.total_cost or 0))

        # 查询支付
        payments = (
            db.query(Payment)
            .filter(
                Payment.user_id == user_id,
                Payment.status == "success",
                Payment.paid_at >= start_dt,
                Payment.paid_at <= end_dt,
            )
            .all()
        )

        total_payments = Decimal("0")
        for payment in payments:
            total_payments += Decimal(str(payment.amount or 0))

        # 查询退款
        transactions = (
            db.query(Transaction)
            .filter(
                Transaction.user_id == user_id,
                Transaction.type == "refund",
                Transaction.created_at >= start_dt,
                Transaction.created_at <= end_dt,
            )
            .all()
        )

        total_refunds = Decimal("0")
        for tx in transactions:
            total_refunds += Decimal(str(tx.amount or 0))

        # 计算差异
        discrepancy = total_amount - total_payments + total_refunds

        # 逐笔明细
        details = []

        # 订单明细
        for order in orders:
            details.append(
                {
                    "type": "order",
                    "id": order.id,
                    "amount": float(order.total_cost or 0),
                    "date": order.created_at.isoformat() if order.created_at else None,
                    "status": order.status,
                }
            )

        # 支付明细
        for payment in payments:
            details.append(
                {
                    "type": "payment",
                    "id": payment.id,
                    "amount": float(payment.amount or 0),
                    "date": payment.paid_at.isoformat() if payment.paid_at else None,
                    "channel": payment.channel,
                }
            )

        # 退款明细
        for tx in transactions:
            details.append(
                {
                    "type": "refund",
                    "id": tx.id,
                    "amount": float(tx.amount or 0),
                    "date": tx.created_at.isoformat() if tx.created_at else None,
                    "order_id": tx.order_id,
                }
            )

        # 按日期排序
        details.sort(key=lambda x: x["date"] or "", reverse=True)

        return {
            "total_orders": total_orders,
            "total_amount": float(total_amount),
            "total_payments": float(total_payments),
            "total_refunds": float(total_refunds),
            "discrepancy": float(discrepancy),
            "details": details,
        }
