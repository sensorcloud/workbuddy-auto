"""
钱包服务层
提供钱包余额管理、冻结/解冻、消费、充值、提现、退款等操作
所有金额操作使用 Decimal，事务安全
"""
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime
import uuid

from app.models.wallet import Wallet, Transaction
from app.models.asset import Asset
from app.core.config import settings


class WalletService:
    """钱包服务类"""

    @staticmethod
    def get_or_create_wallet(db: Session, user_id: str) -> Wallet:
        """
        获取或创建钱包。新用户注册时自动创建，开发环境赠送初始金额
        """
        wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
        if wallet:
            return wallet

        # 创建新钱包
        wallet_id = str(uuid.uuid4())
        initial_balance = settings.WALLET_INITIAL_BALANCE

        wallet = Wallet(
            id=wallet_id,
            user_id=user_id,
            balance=initial_balance,
            frozen=Decimal("0"),
            total_recharge=Decimal("0"),
            total_withdraw=Decimal("0"),
            total_consume=Decimal("0"),
            credit_limit=Decimal("0"),
            low_balance_alert=Decimal("100"),
        )
        db.add(wallet)

        # 记录初始充值交易
        tx = Transaction(
            id=str(uuid.uuid4()),
            wallet_id=wallet_id,
            user_id=user_id,
            type="recharge",
            amount=initial_balance,
            balance_after=initial_balance,
            remark="新用户注册赠送",
        )
        db.add(tx)

        db.commit()
        db.refresh(wallet)
        return wallet

    @staticmethod
    def get_wallet(db: Session, user_id: str) -> Wallet:
        """获取钱包（不自动创建）"""
        return db.query(Wallet).filter(Wallet.user_id == user_id).first()

    @staticmethod
    def check_balance(db: Session, user_id: str, amount: Decimal) -> bool:
        """
        检查可用余额是否充足（balance - frozen >= amount）
        """
        wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
        if not wallet:
            return False

        available = wallet.balance - wallet.frozen
        return available >= amount

    @staticmethod
    def freeze(db: Session, user_id: str, amount: Decimal, order_id: str = None) -> dict:
        """
        冻结金额。同一事务中：
        1. with_for_update() 锁定 Wallet 行
        2. 检查 available >= amount
        3. wallet.frozen += amount
        4. 写入 Transaction(type="freeze")
        5. commit
        """
        try:
            wallet = (
                db.query(Wallet)
                .filter(Wallet.user_id == user_id)
                .with_for_update()
                .first()
            )
            if not wallet:
                # 自动创建钱包
                wallet = WalletService.get_or_create_wallet(db, user_id)
                wallet = (
                    db.query(Wallet)
                    .filter(Wallet.user_id == user_id)
                    .with_for_update()
                    .first()
                )

            available = wallet.balance - wallet.frozen
            if available < amount:
                return {"success": False, "message": f"可用余额不足，需要 {amount}，可用 {available}"}

            wallet.frozen = wallet.frozen + amount

            # 写入交易记录
            tx = Transaction(
                id=str(uuid.uuid4()),
                wallet_id=wallet.id,
                user_id=user_id,
                type="freeze",
                amount=amount,
                balance_after=wallet.balance,
                order_id=order_id,
                remark=f"冻结金额 {amount}",
            )
            db.add(tx)

            db.commit()
            db.refresh(wallet)

            return {
                "success": True,
                "wallet_id": wallet.id,
                "frozen": float(wallet.frozen),
                "balance": float(wallet.balance),
            }

        except Exception as e:
            db.rollback()
            return {"success": False, "message": f"冻结失败: {str(e)}"}

    @staticmethod
    def unfreeze(db: Session, user_id: str, amount: Decimal, order_id: str = None) -> dict:
        """
        解冻金额（退款时用）。减少 frozen，写入 Transaction(type="unfreeze")
        """
        try:
            wallet = (
                db.query(Wallet)
                .filter(Wallet.user_id == user_id)
                .with_for_update()
                .first()
            )
            if not wallet:
                return {"success": False, "message": "钱包不存在"}

            if wallet.frozen < amount:
                amount = wallet.frozen  # 最多解冻已冻结的金额

            wallet.frozen = wallet.frozen - amount

            # 写入交易记录
            tx = Transaction(
                id=str(uuid.uuid4()),
                wallet_id=wallet.id,
                user_id=user_id,
                type="unfreeze",
                amount=amount,
                balance_after=wallet.balance,
                order_id=order_id,
                remark=f"解冻金额 {amount}",
            )
            db.add(tx)

            db.commit()
            db.refresh(wallet)

            return {
                "success": True,
                "wallet_id": wallet.id,
                "unfrozen": float(amount),
                "frozen": float(wallet.frozen),
            }

        except Exception as e:
            db.rollback()
            return {"success": False, "message": f"解冻失败: {str(e)}"}

    @staticmethod
    def consume(db: Session, user_id: str, amount: Decimal, order_id: str = None) -> dict:
        """
        消费（从冻结金额中扣除）。同一事务中：
        1. with_for_update() 锁定 Wallet 行
        2. wallet.frozen -= amount（如果冻结金额不足则从 balance 扣）
        3. wallet.total_consume += amount
        4. 写入 Transaction(type="consume")
        5. commit
        """
        try:
            wallet = (
                db.query(Wallet)
                .filter(Wallet.user_id == user_id)
                .with_for_update()
                .first()
            )
            if not wallet:
                return {"success": False, "message": "钱包不存在"}

            # 先从冻结金额扣除
            if wallet.frozen >= amount:
                wallet.frozen = wallet.frozen - amount
            else:
                # 冻结金额不足，从余额扣
                remaining = amount - wallet.frozen
                wallet.frozen = Decimal("0")
                wallet.balance = wallet.balance - remaining

            wallet.total_consume = wallet.total_consume + amount

            # 写入交易记录
            tx = Transaction(
                id=str(uuid.uuid4()),
                wallet_id=wallet.id,
                user_id=user_id,
                type="consume",
                amount=amount,
                balance_after=wallet.balance,
                order_id=order_id,
                remark=f"消费扣款 {amount}",
            )
            db.add(tx)

            db.commit()
            db.refresh(wallet)

            return {
                "success": True,
                "wallet_id": wallet.id,
                "consumed": float(amount),
                "balance": float(wallet.balance),
                "frozen": float(wallet.frozen),
            }

        except Exception as e:
            db.rollback()
            return {"success": False, "message": f"消费失败: {str(e)}"}

    @staticmethod
    def recharge(db: Session, user_id: str, amount: Decimal, payment_id: str = None) -> dict:
        """
        充值。wallet.balance += amount, wallet.total_recharge += amount, Transaction(type="recharge")
        """
        try:
            wallet = (
                db.query(Wallet)
                .filter(Wallet.user_id == user_id)
                .with_for_update()
                .first()
            )
            if not wallet:
                # 自动创建钱包
                wallet = WalletService.get_or_create_wallet(db, user_id)
                wallet = (
                    db.query(Wallet)
                    .filter(Wallet.user_id == user_id)
                    .with_for_update()
                    .first()
                )

            wallet.balance = wallet.balance + amount
            wallet.total_recharge = wallet.total_recharge + amount

            # 写入交易记录
            tx = Transaction(
                id=str(uuid.uuid4()),
                wallet_id=wallet.id,
                user_id=user_id,
                type="recharge",
                amount=amount,
                balance_after=wallet.balance,
                payment_id=payment_id,
                remark=f"充值 {amount}",
            )
            db.add(tx)

            db.commit()
            db.refresh(wallet)

            return {
                "success": True,
                "wallet_id": wallet.id,
                "recharged": float(amount),
                "balance": float(wallet.balance),
            }

        except Exception as e:
            db.rollback()
            return {"success": False, "message": f"充值失败: {str(e)}"}

    @staticmethod
    def withdraw(db: Session, user_id: str, amount: Decimal, bank_info: dict = None) -> dict:
        """
        提现申请。冻结对应金额，T+1 审核。
        wallet.frozen += amount, wallet.balance -= amount, Transaction(type="withdraw")
        """
        try:
            wallet = (
                db.query(Wallet)
                .filter(Wallet.user_id == user_id)
                .with_for_update()
                .first()
            )
            if not wallet:
                return {"success": False, "message": "钱包不存在"}

            available = wallet.balance - wallet.frozen
            if available < amount:
                return {"success": False, "message": f"可用余额不足，需要 {amount}，可用 {available}"}

            wallet.balance = wallet.balance - amount
            wallet.frozen = wallet.frozen + amount

            # 写入交易记录
            remark = "提现申请"
            if bank_info:
                remark += f" - {bank_info.get('bank_name', '')} {bank_info.get('account_name', '')}"

            tx = Transaction(
                id=str(uuid.uuid4()),
                wallet_id=wallet.id,
                user_id=user_id,
                type="withdraw",
                amount=amount,
                balance_after=wallet.balance,
                remark=remark,
            )
            db.add(tx)

            db.commit()
            db.refresh(wallet)

            return {
                "success": True,
                "wallet_id": wallet.id,
                "withdrawn": float(amount),
                "balance": float(wallet.balance),
                "frozen": float(wallet.frozen),
                "message": "提现申请已提交，等待审核",
            }

        except Exception as e:
            db.rollback()
            return {"success": False, "message": f"提现申请失败: {str(e)}"}

    @staticmethod
    def refund(db: Session, user_id: str, amount: Decimal, order_id: str = None) -> dict:
        """
        退款。wallet.balance += amount, wallet.frozen -= amount（如果还有冻结）, Transaction(type="refund")
        """
        try:
            wallet = (
                db.query(Wallet)
                .filter(Wallet.user_id == user_id)
                .with_for_update()
                .first()
            )
            if not wallet:
                # 自动创建钱包
                wallet = WalletService.get_or_create_wallet(db, user_id)
                wallet = (
                    db.query(Wallet)
                    .filter(Wallet.user_id == user_id)
                    .with_for_update()
                    .first()
                )

            # 优先解冻，再增加余额
            if wallet.frozen > Decimal("0"):
                unfreeze_amount = min(wallet.frozen, amount)
                wallet.frozen = wallet.frozen - unfreeze_amount
                remaining = amount - unfreeze_amount
                if remaining > Decimal("0"):
                    wallet.balance = wallet.balance + remaining
            else:
                wallet.balance = wallet.balance + amount

            # 写入交易记录
            tx = Transaction(
                id=str(uuid.uuid4()),
                wallet_id=wallet.id,
                user_id=user_id,
                type="refund",
                amount=amount,
                balance_after=wallet.balance,
                order_id=order_id,
                remark=f"退款 {amount}",
            )
            db.add(tx)

            db.commit()
            db.refresh(wallet)

            return {
                "success": True,
                "wallet_id": wallet.id,
                "refunded": float(amount),
                "balance": float(wallet.balance),
                "frozen": float(wallet.frozen),
            }

        except Exception as e:
            db.rollback()
            return {"success": False, "message": f"退款失败: {str(e)}"}

    @staticmethod
    def get_transactions(
        db: Session,
        user_id: str,
        tx_type: str = None,
        page: int = 1,
        page_size: int = 20,
        start_date: datetime = None,
        end_date: datetime = None,
    ) -> dict:
        """
        查询交易流水，支持类型筛选和时间范围。
        返回 {"items": [...], "total": int, "page": int, "page_size": int}
        """
        query = db.query(Transaction).filter(Transaction.user_id == user_id)

        if tx_type:
            query = query.filter(Transaction.type == tx_type)

        if start_date:
            query = query.filter(Transaction.created_at >= start_date)

        if end_date:
            query = query.filter(Transaction.created_at <= end_date)

        total = query.count()
        offset = (page - 1) * page_size
        items = (
            query.order_by(Transaction.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return {"items": items, "total": total, "page": page, "page_size": page_size}

    @staticmethod
    def set_low_balance_alert(db: Session, user_id: str, threshold: Decimal) -> dict:
        """设置低余额告警阈值"""
        wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
        if not wallet:
            return {"success": False, "message": "钱包不存在"}

        wallet.low_balance_alert = threshold
        db.commit()
        db.refresh(wallet)

        return {"success": True, "threshold": float(threshold)}

    @staticmethod
    def get_balance_info(db: Session, user_id: str) -> dict:
        """获取余额信息（供前端显示）"""
        wallet = WalletService.get_or_create_wallet(db, user_id)

        return {
            "wallet_id": wallet.id,
            "balance": float(wallet.balance),
            "frozen": float(wallet.frozen),
            "available": float(wallet.balance - wallet.frozen),
            "total_recharge": float(wallet.total_recharge),
            "total_withdraw": float(wallet.total_withdraw),
            "total_consume": float(wallet.total_consume),
            "credit_limit": float(wallet.credit_limit),
            "low_balance_alert": float(wallet.low_balance_alert),
        }
