"""
钱包 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel

from app.database import get_db
from app.core.security import get_current_user
from app.schemas.wallet import WalletBalanceResponse, WalletRechargeRequest, WalletWithdrawRequest, TransactionRecord
from app.services.wallet_service import WalletService
from app.services.payment_service import MockPaymentGateway
from app.models.payment import Payment
import uuid

router = APIRouter()


class LowBalanceAlertRequest(BaseModel):
    threshold: Decimal


@router.get("/balance", response_model=WalletBalanceResponse)
async def get_balance(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    查询钱包余额
    """
    user_id = current_user.get("user_id", current_user.get("sub", "current_user"))
    wallet = WalletService.get_or_create_wallet(db, user_id)
    info = WalletService.get_balance_info(db, user_id)

    return WalletBalanceResponse(
        balance=Decimal(str(info["balance"])),
        frozen=Decimal(str(info["frozen"])),
        available=Decimal(str(info["available"])),
        total_recharge=Decimal(str(info["total_recharge"])),
        total_withdraw=Decimal(str(info["total_withdraw"])),
        total_consume=Decimal(str(info["total_consume"])),
        credit_limit=Decimal(str(info["credit_limit"])),
        low_balance_alert=Decimal(str(info["low_balance_alert"])),
    )


@router.post("/recharge")
async def recharge(
    req: WalletRechargeRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    充值（模拟第三方支付）
    """
    user_id = current_user.get("user_id", current_user.get("sub", "current_user"))

    # 创建模拟支付交易
    gateway_result = MockPaymentGateway.create_trade(req.amount, req.channel, f"recharge-{user_id}")

    # 创建支付记录
    payment_id = str(uuid.uuid4())
    payment = Payment(
        id=payment_id,
        order_id=None,
        user_id=user_id,
        channel=req.channel,
        amount=req.amount,
        status="pending",
        trade_no=gateway_result["trade_no"],
    )
    db.add(payment)
    db.commit()

    # 模拟直接充值成功（开发环境）
    payment.status = "success"
    payment.paid_at = datetime.utcnow()
    db.commit()

    # 调用钱包充值
    result = WalletService.recharge(db, user_id, req.amount, payment_id=payment_id)

    return {
        "payment_id": payment_id,
        "transaction_id": payment_id,
        "amount": req.amount,
        "payment_url": gateway_result["payment_url"],
        "status": "success",
        "message": "充值成功",
    }


@router.post("/withdraw")
async def withdraw(
    req: WalletWithdrawRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    提现申请
    """
    user_id = current_user.get("user_id", current_user.get("sub", "current_user"))
    bank_info = {
        "bank_card": req.bank_card,
        "bank_name": req.bank_name,
        "account_name": req.account_name,
    }

    result = WalletService.withdraw(db, user_id, req.amount, bank_info=bank_info)

    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("message", "提现申请失败"))

    withdraw_id = str(uuid.uuid4())
    return {
        "withdraw_id": withdraw_id,
        "amount": req.amount,
        "status": "pending",
        "message": result.get("message", "提现申请已提交"),
    }


@router.put("/low-balance-alert")
async def set_low_balance_alert(
    body: LowBalanceAlertRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    设置低余额告警阈值
    """
    user_id = current_user.get("user_id", current_user.get("sub", "current_user"))
    result = WalletService.set_low_balance_alert(db, user_id, body.threshold)

    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("message", "设置失败"))

    return result


@router.get("/transactions")
async def get_transactions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    type: Optional[str] = Query(None, description="交易类型: recharge, freeze, unfreeze, consume, refund, withdraw"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
):
    """
    查询交易流水
    """
    user_id = current_user.get("user_id", current_user.get("sub", "current_user"))
    result = WalletService.get_transactions(
        db, user_id,
        tx_type=type,
        page=page,
        page_size=page_size,
        start_date=start_date,
        end_date=end_date,
    )

    items = []
    for tx in result["items"]:
        items.append(TransactionRecord(
            id=tx.id,
            type=tx.type,
            amount=tx.amount,
            balance_after=tx.balance_after,
            order_id=tx.order_id,
            remark=tx.remark,
            created_at=tx.created_at,
        ))

    return {
        "items": items,
        "total": result["total"],
        "page": result["page"],
        "page_size": result["page_size"],
    }
